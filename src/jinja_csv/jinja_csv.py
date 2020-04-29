import os, sys, argparse

from .csv_model import CSVDictModel
from .csv_view import CSVJinjaView
from pathlib import Path

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
    parser.add_argument('-o', '--output', help="Specify the output file or folder. If ommited it will print sdtin.")
    parser.add_argument('-f', '--files', action='store_true', help="Generate one file per row")
    parser.add_argument('-r', '--row',default=0, help='The row index to use as the file name')
    parser.add_argument('-e', '--ext', default='.txt', help='The extension of the generated files')
    args = parser.parse_args()

    if (args.files  and args.output == None):
        parser.error('The --files argument requires the --output to be present')

    template_path = os.path.dirname(args.template)
    template_file=os.path.basename(args.template)

    if args.files:
        # make sure that the output folder exists or create it
        Path(args.output).mkdir(parents=True, exist_ok=True)
        # render the tempalates
        render_template_per_row(args.inputfile,
            template_file, 
            lambda name:os.path.join(args.output, '_'.join(name.lower().split()) + args.ext),
            template_path,
            None,
            args.row)
    else:
        output = render_template_from_csv(args.inputfile, template_file, template_path)
        if not args.output:
            print(output, end='')
        else:
            with open(args.output, 'w') as fp:
                fp.write(output)

if __name__ == '__main__':
    main()
