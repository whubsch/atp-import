import re
import os
from resources import street_expand

folder_path = "./data"

files = [
    os.path.join(root, file)
    for root, _, files in os.walk(folder_path)
    for file in files
    if file.endswith(".osm")
]

for file in files:
    with open(file, "r") as f:
        contents = f.read()

    for abbr, replacement in street_expand.items():
        contents = re.sub(
          rf"(<tag k='addr:street' v='.*)(\b{abbr.title()}\b\.?)", rf"\1{replacement.title()}", contents
        )

    contents = re.sub(
        r"(<tag k='addr:street' v='.*)(\bN\.?E\b\.?)", r"\1Northeast", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*)(\bS\.?E\b\.?)", r"\1Southeast", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*)(\bN\.?W\b\.?)", r"\1Northwest", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*)(\bS\.?W\b\.?)", r"\1Southwest", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*[^\.])(\bE\b\.)", r"\1East", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*[^\.])(\bW\b\.)", r"\1West", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*[^\.])(\bN\b\.)", r"\1North", contents
    )
    contents = re.sub(
        r"(<tag k='addr:street' v='.*[^\.])(\bS\b\.)", r"\1South", contents
    )

    contents = re.sub(r"(<tag k='addr:street' v='.*)(\bRt\b\.?)", r"\1Route", contents)

    with open(file, "w") as f:  # w unreadable, w+ clears, r+ appends
        f.write(contents)
