import json

with open('mappings/mapped.json') as f:
    data = json.load(f)
    final = []
    for obj in data:
        newobj = {}
        newobj["question"] = obj["question"]
        newobj["sql"] = obj["sql"]
        newobj["mapping"] = obj["mapping"]
        final.append(newobj)
    with open('clean.json', 'w') as outfile:
        json.dump(final, outfile, indent=2)


