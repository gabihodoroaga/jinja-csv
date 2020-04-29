#!/bin/bash
cd src
python3 -m jinja_csv.jinja_csv -i ../example/users.csv -t ../example/users.j2
cd ..
