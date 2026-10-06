# check connection, is valid and ready to use
# FOUND FROM HEERE
# https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains/

import logging
import urllib
import requests

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s : %(lineno)d - %(message)s"
)


def check_gateway():
    # /v1/api/tickle
    url = f"https://localhost:4002/v1/api/tickle"
    try:
        search_request = requests.get(url=url, verify=False)
        search_request.raise_for_status()
        data = search_request.json()
        logging.debug(f"Gateway request ata : {data}")
        iserver = data.get("iserver", {})
        # iserver_established = iserver.get("established")
        iserver_established_authStatus = iserver.get("authStatus")
        authenticated = iserver_established_authStatus_authenticated = iserver_established_authStatus.get("authenticated")
        established = iserver_established_authStatus_established = iserver_established_authStatus.get("established")
        connected = iserver_established_authStatus_connected = iserver_established_authStatus.get("connected")
        # established = data.get("established")
        # connected = data.get("connected")
        # authenticated = data.get("authenticated")
        if not None in (established, connected, authenticated):
            logging.info(f"gateway ready : {data}")
            return True
    except Exception as e:
        raise ValueError(f"gateway not ready : {e}")


if __name__ == "__main__":
    if check_gateway():
        logging.info("Gateway is ready and connected.")
    elif not check_gateway():
        logging.warning("Gateway is not ready or not connected.")
