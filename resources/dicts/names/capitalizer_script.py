import json

import os
import os.path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

names: dict[str, dict[str, list[str]] | list[str]]

with open("./names.json") as fp:
    names = json.load(fp)

# iterate through all suffixes and capitalize them
for key in names:
    if key.endswith("_suffixes"):
        sub = names[key]
        if isinstance(sub, list):
            sub = [s.capitalize() for s in sub]
        elif isinstance(sub, dict):
            sub = {k: [s.capitalize() for s in v] for (k, v) in sub.items()}
        names[key] = sub

with open("./names.json", "w") as fp:
    json.dump(names, fp, indent=2)
