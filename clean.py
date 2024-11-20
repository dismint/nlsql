import json

with open('spider_annotated_mapped.json') as f:
    data = json.load(f)
    final = []
    for obj in data:
        newobj = {}
        newobj["question"] = obj["question"]
        newobj["sql"] = obj["sql"]
        newobj["mapping"] = obj["mapping"]
        final.append(newobj)
    with open('spider_mapped.json', 'w') as outfile:
        json.dump(final, outfile, indent=2)


