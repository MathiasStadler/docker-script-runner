# check connection, is valid and ready to use
# FOUND FROM HEERE
# https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains/

import logging
import urllib
import requests
import urllib3

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s : %(lineno)d - %(message)s"
)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_gateway() -> None:

    #method var resp
    resp = False

    try:
        # /v1/api/tickle
        url = f"https://localhost:4002/v1/api/tickle"
        resp = requests.get(url=url, verify=False)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"gateway not ready : {e}")
    except urllib.error.URLError as e:
        raise ValueError(f"gateway not ready : {e}")

    try:
        data = resp.json()
        logging.debug(f"Gateway request ata : {data}")
        established = data.get("established")
        connected = data.get("connected")
        authenticated = data.get("authenticated")
        if not None in (established, connected, authenticated):
            logging.info(f"gateway ready : {data}")
            return True
    except Exception as e:
        raise ValueError(f"gateway not ready : {e}")
    return False


if __name__ == "__main__":
    check_gateway()
