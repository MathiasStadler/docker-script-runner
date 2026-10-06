# cat secdef_search_output.json | python -c "import sys; print(sys.stdin.read())"


import json
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s : %(lineno)d - %(message)s"
)

json_string = sys.stdin.read()
data = json.loads(json_string)
logging.info(f"Data read from stdin: {data}")

underConid = data.get("underConid")
logging.info(f"underConid: {underConid}")

data_months = data.get("months")
if data_months is not None:
    logging.info(f"months: {data_months}")
    