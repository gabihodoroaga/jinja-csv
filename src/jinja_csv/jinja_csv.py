import os, sys, argparse

from .csv_model import CSVDictModel
from .csv_view import CSVJinjaView

def render_template_from_csv(csvfile, templatefile, template_path=None, options=None, **kwargs):
    model = CSVDictModel.from_file(csvfile)
    view = CSVJinjaView(template_path=template_path, env_options=options)
    return view.render_jinja_template(templatefile, model, **kwargs)

def render_template_per_row(csvfile, templatefile, filemapper, template_path=None, options=None, rowkey=0, **kwargs):
    model = CSVDictModel.from_file(csvfile)
    view = CSVJinjaView(template_path=template_path, env_options=options)
    for output in view.render_template_for_rows(templatefile, model, rowkey, **kwargs):
        with open(filemapper(output[0]), 'w') as fp:
            fp.write(output[1])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputfile', required=True, help="Specify the input csv file.")
    parser.add_argument('-t', '--template', required=True, help="Specify the template file.")
    parser.add_argument('-o', '--output', help="Specify the output file. If ommited it will print sdtin.")
    args = parser.parse_args()
    output = render_template_from_csv(args.inputfile, args.template)
    if not args.output:
        print(output, end='')
    else:
        with open(args.output, 'w') as fp:
            fp.write(output)

if __name__ == '__main__':
    main()
