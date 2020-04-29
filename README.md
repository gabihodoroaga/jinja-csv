# jinja-csv

Use Jinja2 templates to format data from CSV files.

## Installation

Works on Python 3.4+.

```bash
pip3 install https://github.com/gabihodoroaga/jinja-csv/releases/download/v0.2/jinja_csv-0.2-py3-none-any.whl
```

or 

```bash
git clone https://github.com/gabihodoroaga/jinja-csv.git

cd jinja-csv

python setup.py install

```

## Example usage

Simple usage with output
```bash
jinja-csv -i example/users.csv -t example/users.j2 -o example/users.sql

```

If you don't specify the output argument then you can pipe the result to another command.

```bash
jinja-csv -i example/users.csv -t example/users.j2 | mysql -u root -p testdb
```


## Authors

* Raymond Chee (original author)
* Gabriel Hodoroaga

## Acknowledgments

Forked from [github.com/rjchee/jinja-csv](https://github.com/rjchee/jinja-csv), fixed some issues and created the setup.
