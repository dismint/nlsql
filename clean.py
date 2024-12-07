import json

with open('fabian2_annotated_mapped.json') as f:
    data = json.load(f)
    final = []
    for obj in data:
        newobj = {}
        newobj["db"] = "dw"
        newobj["question"] = obj["question"]
        newobj["sql"] = obj["sql"]
        newobj["mapping"] = obj["mapping"]
        final.append(newobj)
    with open('fabian2_mapped.json', 'w') as outfile:
        json.dump(final, outfile, indent=2)
