# cspell:ignore secdef secdefSearch

import logging

import requests

import urllib3

import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s : %(lineno)d - %(message)s')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s : %(lineno)d - %(message)s"
)

PREFERRED_EXCHANGES = (
    "AMEX",
    "ARCA",
    "BATS",
    "IEX",
    "NASDAQ",
    "NYSE",
    "SMART",
)




def secdefSearch(symbol):
    url = f"https://localhost:4002/v1/api/iserver/secdef/search?symbol={symbol}"
    try:
        search_request = requests.get(url=url, verify=False)
        search_request.raise_for_status()
        data = search_request.json()
    except Exception as e:
        raise ValueError(f"API request failed for {symbol}: {e}")

    if not isinstance(data, list):
        raise ValueError(f"Unexpected API response for {symbol}: {data}")

    selected_contract = None
    for contract in data:
        if not isinstance(contract, dict):
            continue
        desc = contract.get("description", "")
        if desc in PREFERRED_EXCHANGES:
            for secType in contract.get("sections", []):
                if secType.get("secType") == "OPT":
                    selected_contract = contract
                    logging.info(f"Selected exchange: {desc}")
                    break
            if selected_contract:
                break
    if not selected_contract:
        for contract in data:
            if not isinstance(contract, dict):
                continue
            for secType in contract.get("sections", []):
                if secType.get("secType") == "OPT":
                    selected_contract = contract
                    logging.info(
                        f"Fallback exchange: {contract.get('description', 'Unknown')}"
                    )
                    break
            if selected_contract:
                break

    if not selected_contract:
        raise ValueError(f"No option contract found for {symbol}")

    underConid = selected_contract.get("conid")
    if not underConid:
        raise ValueError(f"No conid for {symbol}")

    months = []
    for secType in selected_contract.get("sections", []):
        if secType.get("secType") == "OPT":
            months_str = secType.get("months", "")
            if months_str:
                months = months_str.split(";")
            break

    if not months:
        raise ValueError(f"No option months for {symbol}")

    return underConid, months


__MAIN__ = __name__ == "__main__"
underConid,months = secdefSearch("TREX") if __MAIN__ else None

logging.info(f"underConid: {underConid}, months: {months}") 

data = {"underConid": underConid, "months": months}
json_string = json.dumps(data, indent=4)
with open("secdef_search_output.json", "w") as json_file:
    json_file.write(json_string)