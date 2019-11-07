import csv
from datetime import datetime
import tempfile
import unittest

from csv_model import CSVRow
from csv_model import CSVDictRow
from csv_model import CSVModel
from csv_model import CSVDictModel
from csv_model import CSVColumn
from csv_model import cast_to_bool
from csv_model import cast_to_date

class TestCSVRow(unittest.TestCase):

    def setUp(self):
        self.data = ['Hello', 3.5, 1, '', '99']
        self.row = CSVRow(self.data)
    
    def test_iter(self):
        self.assertEqual(list(self.row), self.data)

    def test_contains(self):
        for val in self.data:
            self.assertIn(val, self.row)

    def test_len(self):
        self.assertEqual(len(self.row), len(self.data))

    def test_get(self):
        for i, val in enumerate(self.data):
            self.assertEqual(self.row[i], val)
        self.assertEqual(self.row[-1], '99')
        self.assertEqual(self.row[-3], 1)

    def test_get_slice(self):
        self.assertEqual(self.row[:3], ('Hello', 3.5, 1))
        self.assertEqual(self.row[3:], ('', '99'))
        self.assertEqual(self.row[1:3], (3.5, 1))
        self.assertEqual(self.row[::2], ('Hello', 1, '99'))
        self.assertEqual(self.row[1:5:2], (3.5, ''))

    def test_eq(self):
        self.assertEqual(self.row, self.data)

    def test_cast(self):
        self.assertEqual(self.row.cast([set, str, str, bool, int]),
                                       [set(['H', 'e', 'l', 'o']), '3.5', '1', False, 99])
        self.assertEqual(self.row.cast([bool]*len(self.data)), list(map(bool, self.data)))


class TestCSVDictRow(TestCSVRow):

    def setUp(self):
        self.data = ['Hello', 3.5, 1, '', '99']
        self.fields = ['Text', 'Score', 'Count', 'Comments', 'Rank']
        self.row = CSVDictRow(self.fields, self.data)

    def test_get_fieldnames(self):
        for field, val in zip(self.fields, self.data):
            self.assertEqual(self.row[field], val)

    def test_get_slice_fieldnames(self):
        self.assertEqual(self.row[slice('Comments')], ('Hello', 3.5, 1, ''))
        self.assertEqual(self.row[slice('Comments', None)], ('', '99'))
        self.assertEqual(self.row[slice('Score', 'Comments')], (3.5, 1, ''))
        self.assertEqual(self.row[slice('Text', 'Count')], ('Hello', 3.5, 1))
        self.assertEqual(self.row[slice('Score', 5, 2)], (3.5, ''))


class TestCSVColumn(unittest.TestCase):

    def setUp(self):
        self.data = list(range(5))
        self.col = CSVColumn(self.data)

    def test_get(self):
        for i, val in enumerate(self.data):
            self.assertEqual(self.col[i], val)
        self.assertEqual(self.col[-1], 4)
        self.assertEqual(self.col[-2], 3)

    def test_get_slice(self):
        self.assertEqual(self.col[:3], (0, 1, 2))
        self.assertEqual(self.col[:10], (0, 1, 2, 3, 4))
        self.assertEqual(self.col[2:], (2, 3, 4))
        self.assertEqual(self.col[-3:], (2, 3, 4))
        self.assertEqual(self.col[:-3], (0, 1))
        self.assertEqual(self.col[1:3], (1, 2))
        self.assertEqual(self.col[::2], (0, 2, 4))

    def test_str(self):
        self.assertNotIn(':', str(self.col))

        name = 'Test_Name'
        col = CSVColumn(self.data, name=name)
        self.assertIn(name, str(col))

    def test_len(self):
        self.assertEqual(len(self.col), 5)

    def test_eq(self):
        self.assertEqual(self.col, self.data)
        self.assertEqual(self.col, range(5))
        self.assertNotEqual(self.col, range(6))
        self.assertNotEqual(self.col, [0, 3, 1, 2, 4])


class TestCastFunctions(unittest.TestCase):
    def test_cast_to_bool(self):
        data = [None, 'true', 'TRUE', 'YES', 'Y', 'y', 'Yes', 'FALSE', 'False', 'NO', 'n', 'N',
                0, 1, [], ['f'], True, False]
        expected = [False, True, True, True, True, True, True, False, False, False, False, False,
                False, True, False, True, True, False]
        self.assertEqual(len(data), len(expected),
                         msg='# of test cases should match # of expected outcomes')
        for test_case, expect in zip(data, expected):
            self.assertEqual(cast_to_bool(test_case), expect)

    def test_cast_to_bool_error(self):
        data = ['eh', 'nyes', 'yo', 'yno']
        for test_case in data:
            with self.assertRaises(ValueError):
                cast_to_bool(test_case)

    def test_cast_to_date(self):
        day = datetime(2017, 7, 2, 0, 0, 0)
        data = [None, '7/2/2017', '07/02/2017', '7/2/2017 0:00:00', '2017-07-02', 100, day]
        expected = [datetime.fromtimestamp(0), day, day, day, day, datetime.fromtimestamp(100), day]
        self.assertEqual(len(data), len(expected),
                         msg='# of test cases should match # of expected outcomes')
        for test_case, expect in zip(data, expected):
            self.assertEqual(cast_to_date(test_case), expect)

    def test_cast_to_date_error(self):
        data = [[], 'Time abcdefg', "2000000 o'clock", '2017/04/03/01/02/03/04', '2017-04-03-99-01', '']
        for test_case in data:
            with self.assertRaises(ValueError, msg=test_case):
                cast_to_date(test_case)


def getValueTypeList(rows):
    return list((item, type(item)) for row in rows for item in row)


class TestCSVModel(unittest.TestCase):

    def setUp(self):
        self.data = [
            ['Hello', '3.6', '1', '', '99', 'True'],
            ['Bye', '9', '0', 'eh', '9.5', 'false'],
            ['s', '3.14', '55', 's', 'false', 'yes'],
            ['eee', '4', '88', 'f', 'yes', 'NO']
        ]
        self.model = CSVModel(self.data)

    def assertCSVModelsAreEqual(self, m1, m2, msg=None):
        self.assertEqual(getValueTypeList(m1), getValueTypeList(m2), msg=msg)

    def test_autocast(self):
        expected_results = [
            ['Hello', 3.6, 1, '', '99', True],
            ['Bye', 9.0, 0, 'eh', '9.5', False],
            ['s', 3.14, 55, 's', 'false', True],
            ['eee', 4.0, 88, 'f', 'yes', False]
        ]
        self.assertCSVModelsAreEqual(expected_results, self.model)

    def test_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            writer = csv.writer(f)
            writer.writerows(self.data)
            f.flush()
            file_model = CSVModel.from_file(f.name)
            self.assertCSVModelsAreEqual(file_model, self.model)

    def test_from_file_with_types(self):
        types = [str, float, int, bool, str, cast_to_bool]
        expected_results = [
            ['Hello', 3.6, 1, False, '99', True],
            ['Bye', 9.0, 0, True, '9.5', False],
            ['s', 3.14, 55, True, 'false', True],
            ['eee', 4.0, 88, True, 'yes', False],
        ]
        with tempfile.NamedTemporaryFile(mode='w') as f:
            writer = csv.writer(f)
            writer.writerows(self.data)
            f.flush()
            file_model = CSVModel.from_file(f.name, types=types)
            self.assertCSVModelsAreEqual(file_model, expected_results)

    def test_cast(self):
        filters = [str, bool, float, len, lambda x:str(x)[0], int]
        expected_results = [
            ['Hello', True, 1.0, 0, '9', 1],
            ['Bye', True, 0.0, 2, '9', 0],
            ['s', True, 55.0, 1, 'f', 1],
            ['eee', True, 88.0, 1, 'y', 0]
        ]
        model = self.model.cast(filters)
        self.assertCSVModelsAreEqual(expected_results, model)

    def test_cast_range(self):
        tests = [
            {
                'filters': [int, float, len],
                'start': 1,
                'stop': 4,
                'expected': [
                    ['Hello', 3, 1.0, 0, '99', True],
                    ['Bye', 9, 0.0, 2, '9.5', False],
                    ['s', 3, 55.0, 1, 'false', True],
                    ['eee', 4, 88.0, 1, 'yes', False]
                ]
            },
            {
                'filters': [str]*6,
                'start': None,
                'stop': None,
                'expected': [
                    ['Hello', '3.6', '1', '', '99', 'True'],
                    ['Bye', '9.0', '0', 'eh', '9.5', 'False'],
                    ['s', '3.14', '55', 's', 'false', 'True'],
                    ['eee', '4.0', '88', 'f', 'yes', 'False']
                ]
            },
            {
                'filters': [str]*6,
                'start': 0,
                'stop': None,
                'expected': [
                    ['Hello', '3.6', '1', '', '99', 'True'],
                    ['Bye', '9.0', '0', 'eh', '9.5', 'False'],
                    ['s', '3.14', '55', 's', 'false', 'True'],
                    ['eee', '4.0', '88', 'f', 'yes', 'False']
                ]
            },
            {
                'filters': [lambda x:x[1], int],
                'start': 4,
                'stop': None,
                'expected': [
                    ['Hello', 3.6, 1, '', '9', 1],
                    ['Bye', 9.0, 0, 'eh', '.', 0],
                    ['s', 3.14, 55, 's', 'a', 1],
                    ['eee', 4.0, 88, 'f', 'e', 0]
                ]
            },
            {
                'filters': [lambda x:str(x)[-1], int],
                'start': None,
                'stop': 2,
                'expected': [
                    ['o', 3, 1, '', '99', True],
                    ['e', 9, 0, 'eh', '9.5', False],
                    ['s', 3, 55, 's', 'false', True],
                    ['e', 4, 88, 'f', 'yes', False]
                ]
            },
            {
                'filters': [bool],
                'start': 2,
                'stop': 3,
                'expected': [
                    ['Hello', 3.6, True, '', '99', True],
                    ['Bye', 9.0, False, 'eh', '9.5', False],
                    ['s', 3.14, True, 's', 'false', True],
                    ['eee', 4.0, True, 'f', 'yes', False]
                ]
            }
        ]

        for idx, test in enumerate(tests):
            casted_model = self.model.cast_range(test['filters'], test['start'], test['stop'])
            errMsg = 'test case #{}'.format(idx)
            self.assertCSVModelsAreEqual(casted_model, test['expected'], msg=errMsg)

    def test_row_slice(self):
        expected_results = [
            ['Bye', 9.0, 0, 'eh', '9.5', False],
            ['s', 3.14, 55, 's', 'false', True]
        ]
        self.assertCSVModelsAreEqual(self.model.row_slice(1, 3), expected_results)

    def test_col_slice(self):
        expected_results = [
            [1, ''],
            [0, 'eh'],
            [55, 's'],
            [88, 'f']
        ]
        self.assertCSVModelsAreEqual(self.model.col_slice(2, 4), expected_results)

    def test_str(self):
        expected = "('Hello', 3.6, 1, '', '99', True)\n" \
            "('Bye', 9.0, 0, 'eh', '9.5', False)\n" \
            "('s', 3.14, 55, 's', 'false', True)\n" \
            "('eee', 4.0, 88, 'f', 'yes', False)"
        self.assertEqual(expected, str(self.model))

class TestCSVDictModel(TestCSVModel):
    def setUp(self):
        self.fieldnames = ['Greeting', 'Rating', 'Score', 'Comment', 'Something', 'eh']
        self.data = [
            ['Hello', '3.6', '1', '', '99', 'True'],
            ['Bye', '9', '0', 'eh', '9.5', 'false'],
            ['s', '3.14', '55', 's', 'false', 'yes'],
            ['eee', '4', '88', 'f', 'yes', 'NO']
        ]
        self.model = CSVDictModel(self.fieldnames, self.data)


    def test_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            writer = csv.DictWriter(f, self.fieldnames)
            writer.writeheader()
            rows = [dict(zip(self.fieldnames, row)) for row in self.data]
            writer.writerows(rows)
            f.flush()
            file_model = CSVDictModel.from_file(f.name)
            self.assertCSVModelsAreEqual(file_model, self.model)
            self.assertEqual(file_model.fieldnames, self.model.fieldnames)

    def test_from_file_with_types(self):
        types = [str, float, int, bool, str, cast_to_bool]
        expected_results = [
            ['Hello', 3.6, 1, False, '99', True],
            ['Bye', 9.0, 0, True, '9.5', False],
            ['s', 3.14, 55, True, 'false', True],
            ['eee', 4.0, 88, True, 'yes', False],
        ]
        with tempfile.NamedTemporaryFile(mode='w') as f:
            writer = csv.DictWriter(f, self.fieldnames)
            writer.writeheader()
            rows = [dict(zip(self.fieldnames, row)) for row in self.data]
            writer.writerows(rows)
            f.flush()
            file_model = CSVDictModel.from_file(f.name, types=types)
            self.assertCSVModelsAreEqual(file_model, expected_results)

    def test_cast_range_fieldnames(self):
        tests = [
            {
                'filters': [int, float, len],
                'start': 'Rating',
                'stop': 'Comment',
                'expected': [
                    ['Hello', 3, 1.0, 0, '99', True],
                    ['Bye', 9, 0.0, 2, '9.5', False],
                    ['s', 3, 55.0, 1, 'false', True],
                    ['eee', 4, 88.0, 1, 'yes', False]
                ]
            },
            {
                'filters': [str]*6,
                'start': 'Greeting',
                'stop': None,
                'expected': [
                    ['Hello', '3.6', '1', '', '99', 'True'],
                    ['Bye', '9.0', '0', 'eh', '9.5', 'False'],
                    ['s', '3.14', '55', 's', 'false', 'True'],
                    ['eee', '4.0', '88', 'f', 'yes', 'False']
                ]
            },
            {
                'filters': [lambda x:x[1], int],
                'start': 'Something',
                'stop': None,
                'expected': [
                    ['Hello', 3.6, 1, '', '9', 1],
                    ['Bye', 9.0, 0, 'eh', '.', 0],
                    ['s', 3.14, 55, 's', 'a', 1],
                    ['eee', 4.0, 88, 'f', 'e', 0]
                ]
            },
            {
                'filters': [lambda x:str(x)[-1], int],
                'start': None,
                'stop': 'Rating',
                'expected': [
                    ['o', 3, 1, '', '99', True],
                    ['e', 9, 0, 'eh', '9.5', False],
                    ['s', 3, 55, 's', 'false', True],
                    ['e', 4, 88, 'f', 'yes', False]
                ]
            },
            {
                'filters': [bool],
                'start': 'Score',
                'stop': 'Score',
                'expected': [
                    ['Hello', 3.6, True, '', '99', True],
                    ['Bye', 9.0, False, 'eh', '9.5', False],
                    ['s', 3.14, True, 's', 'false', True],
                    ['eee', 4.0, True, 'f', 'yes', False]
                ]
            }
        ]

        for idx, test in enumerate(tests):
            casted_model = self.model.cast_range(test['filters'], test['start'], test['stop'])
            errMsg = 'test case #{}'.format(idx)
            self.assertCSVModelsAreEqual(casted_model, test['expected'], msg=errMsg)

    def test_col_slice(self):
        super(TestCSVDictModel, self).test_col_slice()
        expected_results = [
            [1, ''],
            [0, 'eh'],
            [55, 's'],
            [88, 'f']
        ]
        self.assertCSVModelsAreEqual(self.model.col_slice('Score', 'Comment'), expected_results)

    def test_str(self):
        expected = "('Greeting', 'Rating', 'Score', 'Comment', 'Something', 'eh')\n" \
            "('Hello', 3.6, 1, '', '99', True)\n" \
            "('Bye', 9.0, 0, 'eh', '9.5', False)\n" \
            "('s', 3.14, 55, 's', 'false', True)\n" \
            "('eee', 4.0, 88, 'f', 'yes', False)"
        self.assertEqual(expected, str(self.model))


if __name__ == '__main__':
    unittest.main()
