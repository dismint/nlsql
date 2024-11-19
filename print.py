import sqlparse
from rich.console import Console
import sqlglot
from sqlglot import parse_one
import json

console = Console()
console.clear()

MAPPING_FILE = "mappings/mapped.json"

with open(MAPPING_FILE) as f:
    mappings = json.load(f)
    for i, mapp in enumerate(mappings):
        console.clear()
        console.print(f"{i} / {len(mappings)}\n")
        console.print(mapp["question"])
        console.print()
        console.print(mapp["topics"], highlight=False)
        console.print()
        for col in mapp["columns"]:
            console.print(col, highlight=False)
        console.print()
        console.print(json.dumps(mapp["mapping"], indent=4), highlight=False)
        console.print()
        qualified = mapp["qualified"]
        console.print(parse_one(qualified).sql(pretty=True), highlight=False)
        input()
