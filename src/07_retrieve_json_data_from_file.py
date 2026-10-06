# from here
# https://codeinstitute.net/de/blog/working-with-json-in-python/

import json

with open("secdef_search_output.json", "r") as json_file:
    data = json.load(json_file)

underConid = data.get("underConid")
months = data.get("months")
print(underConid)
print(months)


# cat secdef_search_output.json | python -c "import sys; print(sys.stdin.read())"