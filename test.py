import os
import re
import csv
import json
import sqlglot
from sqlglot import parse_one
from sqlglot.optimizer import qualify

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

def get_children(node):
    depth = node.depth
    children = [child for child in node.walk() if child.depth == depth + 1]
    children.reverse()
    return children

alias_map = {}
table_set = set()

def recur(node):
    if type(node) == sqlglot.exp.Table:
        table_set.add(node.name.upper())
    if type(node) == sqlglot.exp.Table and (alias := node.alias) and node.name != alias:
        if alias in alias_map:
            print(f"BAD, {alias} already exists {alias_map}")
        alias_map[alias] = node.name
    for child in get_children(node):
        recur(child)

def rename(node):
    if type(node) == sqlglot.exp.Column and (table := node.table):
        if table in alias_map and alias_map[table]:
            node.set("table", alias_map[table])
    for child in get_children(node):
        rename(child)

FILE = "queries/spider_queries.json"

allcol = set()
with open(FILE, "r") as f:
    data = json.load(f)
    for i, query in enumerate(data):
        try:
            alias_map = {}
            sql = query["sql"]
            parsed = parse_one(sql, read="mysql")
            try:
                qualify.qualify(parsed)
            except Exception as e:
                print("\033[91m" + "CANNOT QUALIFY" + "\033[0m")
                print(parsed.sql(pretty=True))
                print(e)
            recur(parsed)
            rename(parsed)
            columns = set([col for col in parsed.find_all(sqlglot.exp.Column)])
            columns = set([col.table.upper() for col in columns if col.table])
            columns = set([col for col in columns if col in table_set])
            allcol = allcol.union(columns)
        except Exception as ee:
            print("\033[91m" + "ERROR" + "\033[0m")
            try:
                print(parse_one(query["sql"]).sql(pretty=True))
            except Exception as e:
                print("went bad")
                print(query["sql"])
            print(ee)
print(len(table_set), table_set)
print(len(allcol), allcol)
