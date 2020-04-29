import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='jinja-csv',  
    version='0.2',
    author="Raymond Chee, Gabriel Hodoroaga",
    author_email="gabihodoroaga@gmail.com",
    description="Use Jinja templates to format data from CSV files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gabihodoroaga/jinja-csv",
    package_dir={'': 'src'},
    packages=['jinja_csv'],
    include_package_data=True,
    entry_points={'console_scripts': [
        'jinja-csv = jinja_csv.jinja_csv:main',
    ]},
    install_requires=[
        'Jinja2==2.8',
        'MarkupSafe==0.23',
        'python-dateutil==2.6.0',
        'six==1.12.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False
)
