import jinja2, os

from .csv_model import cast_to_bool
from .csv_model import cast_to_date

class CSVJinjaView:
    def __init__(self, env=None, template_path=None, env_options=None, view_options=None):
        if env is None:
            if env_options is None:
                env_options = {}
            if 'trim_blocks' not in env_options:
                env_options['trim_blocks'] = True
            if 'lstrip_blocks' not in env_options:
                env_options['lstrip_blocks'] = True
            if 'loader' not in env_options:
                env_options['loader'] = jinja2.FileSystemLoader([os.getcwd() if template_path is None else template_path, os.path.realpath(__file__)])
            env = jinja2.Environment(**env_options)
        if view_options is None:
            view_options = {
                'default_datetime_fmt': '%D',
            }
        self.default_datetime_fmt = view_options['default_datetime_fmt']
        self.env = env
        self._register_filters()

    def _register_filters(self):
        filters = {
            'cast': self.cast,
            'castrange': self.cast_range,
            'rowrange': row_range,
            'columnrange': column_range,
            'getcolumns': columns,
            'sortedby': sortedby,
            'bool': cast_to_bool,
            'date': cast_to_date,
            'dateformat': self.dateformat,
            'sumcolumns': sumcolumns
        }
        self.env.filters.update(filters)

    def render_jinja_template(self, template_name, model, **kwargs):
        return self.env.get_template(template_name).render(
                    rows=model, **kwargs)

    def render_template_for_rows(self, template_name, model, rowkey, **kwargs):
        template = self.env.get_template(template_name)
        return list((row[rowkey], template.render(row=row, fieldnames=model.fieldnames, **kwargs)) for row in model)

    def cast(self, rows, filters):
        return rows.cast(list(self.env.filters.get(f, str) for f in filters))

    def cast_range(self, rows, filters, start=None, end=None):
        return rows.cast_range(list(self.env.filters.get(f, str) for f in filters), start, end)

    def dateformat(self, dt, fmt=None):
        return dt.strftime(fmt or self.default_datetime_fmt)

def row_range(rows, start=None, end=None):
    return rows.row_slice(start, end)

def column_range(rows, start=None, end=None):
    return rows.col_slice(start, end)

def columns(rows, column_list=None):
    cols = rows.cols()
    if column_list is None:
        return cols
    return [cols[idx] for idx in column_list]

def sumcolumns(rows, column_list=None):
    cols = rows.cols()
    if column_list is None:
        return cols.length
    return len(column_list)

def sortedby(rows, sortkeys):
    def keyfunc(row):
        if isinstance(sortkeys, int) or isinstance(sortkeys, str):
            return row[sortkeys]
        return tuple(row[key] for key in sortkeys)
    return sorted(rows, key=keyfunc)
