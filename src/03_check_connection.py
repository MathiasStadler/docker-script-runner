# check connection, is valid and ready to use
# FOUND FROM HEERE
# https://www.interactivebrokers.com/campus/ibkr-quant-news/handling-options-chains/

import logging
import urllib
import requests

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s : %(lineno)d - %(message)s')




def check_gateway():
        # /v1/api/tickle
        url = f'https://localhost:4002/v1/api/tickle'
        try:
            search_request = requests.get(url=url, verify=False)
            search_request.raise_for_status()
            data = search_request.json()
            data = data.get('data', {})
            logging.info(f"gateway ready : {data}")
            data = search_request.json()
            logging.debug(f"Gateway request ata : {data}")
        except Exception as e:
            raise ValueError(f"gateway not ready : {e}")

if __name__ == "__main__":
    check_gateway();