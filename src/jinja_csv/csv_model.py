import csv
import itertools
import datetime

import dateutil.parser

class CSVRow(object):
    def __init__(self, row):
        self.data = tuple(row)

    def __iter__(self):
        return iter(self.data)

    def __eq__(self, other):
        return hasattr(other, '__iter__') and self.data == tuple(other)

    def __len__(self):
        return len(self.data)

    def _getslice(self, start, end):
        if start is None:
            start = 0
        if end is None:
            end = len(self)
        return slice(start, end)

    def __getitem__(self, idx):
        if isinstance(idx, (int, slice)):
            try:
                return self.data[idx]
            except IndexError:
                raise IndexError('CSVRow index out of range')
        raise TypeError('CSVRow can only be indexed with integers or slices, not {}'.format(type(idx).__name__))

    def cast(self, filters):
        if not filters:
            return self
        return CSVRow(self._cast_row(filters))

    def _cast_row(self, filters):
        if len(filters) != len(self):
            raise ValueError('number of filters does not match number of CSV columns; {} != {}'.format(len(filters), len(self)))
        return [f(v) for f, v in zip(filters, self)]

    def __str__(self):
        return str(self.data)


class CSVDictRow(CSVRow):
    def __init__(self, fieldnames, row):
        if len(fieldnames) != len(row):
            raise ValueError("number of fields should match number of columns")
        super().__init__(row)
        self._idx_map = {}
        for idx, field in enumerate(fieldnames):
            self._idx_map[field] = idx
        self.fieldnames = fieldnames

    def _getindex(self, i):
        if isinstance(i, int):
            return i
        return self._idx_map[i]

    def _getslice(self, start, end, step=None):
        if start is None:
            start = 0
        else:
            start = self._getindex(start)
        if end is None:
            end = len(self)
        elif isinstance(end, str):
            end = self._idx_map.get(end)+1
            
        return slice(start, end, step)


    def __getitem__(self, idx):
        if isinstance(idx, str):
            idx = self._getindex(idx)
        if isinstance(idx, int):
            try:
                return self.data[idx]
            except IndexError:
                raise IndexError('CSVDictRow index out of range')
        if not isinstance(idx, slice):
            msg = ('CSVDictRow can only be indexed with integers, fieldnames, '
                   'or slices, not {}').format(type(idx).__name__)
            raise TypeError(msg)
        if idx.step is not None and not isinstance(idx.step, int):
            raise TypeError('slice indices must be integers or None or have an __index__ method')
        return self.data[self._getslice(idx.start, idx.stop, idx.step)]

    def cast(self, filters):
        if not filters:
            return self
        return CSVDictRow(self.fieldnames, self._cast_row(filters))


class CSVColumn(object):
    def __init__(self, col, name=None):
        self.data = tuple(col)
        self.fieldname = name

    def __getitem__(self, idx):
        return self.data[idx]

    def __iter__(self):
        return iter(self.data)

    def __eq__(self, other):
        return hasattr(other, '__iter__') and self.data == tuple(other)

    def __len__(self):
        return len(self.data)

    def cast(self, filter_func):
        return CSVColumn(filter(filter_func, self.data), name=self.fieldname)

    def __str__(self):
        if self.fieldname:
            return '{}: {}'.format(self.fieldname, self.data)
        return str(self.data)


def cast_to_bool(s=None):
    if s is None:
        return False
    if isinstance(s, str):
        if s.lower() in ['true', 'yes', 'y']:
            return True
        elif s.lower() in ['false', 'no', 'n']:
            return False
        raise ValueError()
    else:
        return bool(s)

def cast_to_date(d=None, parserinfo=None, **kwargs):
    if d is None:
        d = 0
    if isinstance(d, datetime.date):
        return d
    if isinstance(d, str):
        return dateutil.parser.parse(d, parserinfo=parserinfo, **kwargs)
    if isinstance(d, int):
        return datetime.datetime.fromtimestamp(d)
    raise ValueError()


class CSVModel:
    def __init__(self, rows, types=None):
        rows = tuple(rows)
        max_len = max(map(len, rows))
        if types is None:
            casts = [int, float, cast_to_bool, cast_to_date]
            types = [str]*max_len
            for i in range(max_len):
                # try to find the most specific cast
                for cast in casts:
                    try:
                        list(map(cast, (row[i] for row in rows if i < len(row))))
                    except ValueError:
                        continue
                    types[i] = cast
                    break
        elif len(types) != max_len:
            raise ValueError(('number of given types ({}) should match '
                              'number of columns ({})!').format(len(types), max_len))

        new_rows = []
        for row in rows:
            new_row = [t(row[i]) if i < len(row) else t() for i, t in enumerate(types)]
            new_rows.append(self._init_row(new_row))
        self._rows = tuple(new_rows)
        self._cols = tuple(self._init_col(i) for i in range(max_len))
        self.num_cols = max_len
        self.num_rows = len(rows)
        self.types = types

    def _init_row(self, row):
        return CSVRow(row)

    def _init_col(self, col_num):
        return CSVColumn(row[col_num] for row in self._rows)

    def cast(self, filters):
        return CSVModel(self._rows, types=tuple(filters))

    def cast_range(self, filters, start=None, end=None):
        if not self._rows:
            return
        filterlen = len(filters)
        csvrow = self._rows[0]
        rangelen = len(csvrow[start:end])
        if rangelen != filterlen:
            raise ValueError('Number of filters ({}) should match number of columns ({})!'.format(filterlen, rangelen))
        new_filters = list(self.types)
        new_filters[csvrow._getslice(start, end)] = filters
        return self.cast(new_filters)

    def __iter__(self):
        return iter(self._rows)

    def __len__(self):
        return self.num_rows

    def __reversed__(self):
        return reversed(self._rows)

    def __str__(self):
        return '\n'.join(map(str, self._rows))

    def rows(self):
        return self._rows

    def row_slice(self, start=None, end=None):
        return CSVModel(self._rows[start:end], types=self.types)

    def iterrows(self):
        return iter(self._rows)

    def cols(self):
        return self._cols

    def col_slice(self, start=None, end=None):
        return CSVModel((row[start:end] for row in self._rows), types=self.types[start:end])

    def itercols(self):
        return iter(self._cols)

    @classmethod
    def from_file(cls, filename, types=None):
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            if types is None:
                return cls(reader)
            rows = []
            for row in reader:
                rows.append([cast(item) for cast, item in itertools.zip_longest(types, row)])
            return cls(rows, types=types)


class CSVDictModel(CSVModel):
    def __init__(self, fieldnames, rows, types=None):
        self.fieldnames = tuple(fieldnames)
        super().__init__(rows, types=types)
        if not self._rows:
            raise ValueError('rows cannot be empty!')

    def __str__(self):
        return '\n'.join(map(str, itertools.chain([self.fieldnames], self._rows)))

    def _init_row(self, row):
        return CSVDictRow(self.fieldnames, row)

    def _init_col(self, col_num):
        return CSVColumn((row[col_num] for row in self._rows), name=self.fieldnames[col_num])

    def cast(self, filters):
        return CSVDictModel(self.fieldnames, self._rows, types=tuple(filters))

    def row_slice(self, start, end):
        return CSVDictModel(self.fieldnames, self._rows[start:end], types=self.types)

    def col_slice(self, start, end):
        s = self._rows[0]._getslice(start, end)
        return CSVDictModel(self.fieldnames[s], (row[s] for row in self._rows),
                            types=self.types[s])

    @classmethod
    def from_file(cls, filename, types=None):
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            rows = []
            if types is None:
                for row in reader:
                    rows.append(tuple(row[field] for field in reader.fieldnames))
                return cls(reader.fieldnames, rows)
            for row in reader:
                row_data = []
                for cast, field in itertools.zip_longest(types, reader.fieldnames):
                    row_data.append(cast(row[field]))
                rows.append(row_data)
            return cls(reader.fieldnames, rows, types=types)
