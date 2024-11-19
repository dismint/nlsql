import os
import re
import csv
import json

path = os.path.join(os.getcwd(), 'schemas')
files = os.listdir(path)
csv_files = [file for file in files if file.endswith('.csv')]

schema = {}

for file in csv_files:
    path = os.path.join(os.getcwd(), 'schemas', file)
    table = file.split('.')[0]
    schema[table] = {}
    with open(path, 'r') as f:
        normalized_lines = (re.sub(r'\s*;\s*', ';', line.strip()) for line in f)
        reader = csv.reader(normalized_lines, delimiter=';')
        rows = [row for row in reader if row]
        for row in rows[2:]:
            assert len(row) == 3
            schema[table][row[0]] = row[1]

print(json.dumps(schema, indent=4))
