import json
import os
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Optional

from urllib.parse import urlencode
from urllib.request import urlopen


logger = logging.getLogger(__name__)


class ExchangeInfoProvider:
    source_url = 'http://data.fixer.io/api/latest'
    source_api_key = os.getenv('FIXER_API_KEY')

    def get_rate(self, base: str = 'EUR', target: str = 'RUB') -> Optional[float]:
        query_string = urlencode({
            'format': 1,
            'base': base,
            'symbols': target,
            'access_key': self.source_api_key,
        })
        try:
            with urlopen(f'{self.source_url}?{query_string}') as resp:
                response_text = resp.read().decode()
                response_data = json.loads(response_text)

            rate = response_data["rates"][target]

        except KeyError as err:
            logger.error("Couldn't parse currency rate response: key not found (%s) | resp: %s", err, response_data)

        except Exception as err:
            logger.exception("Couldn't get currency exchange rate: %s", err)

        else:
            return rate


class CurrencyExchangeHTTPHandler(BaseHTTPRequestHandler):

    class GetRateException(Exception):
        def __init__(self, message: str):
            self.message = message

        def __str__(self):
            return self.message

    def do_GET(self):
        try:
            currency_rate_content = self._get_exchange_rate()
        except self.GetRateException as err:
            content = json.dumps({"status": "ERROR", "message": err.message})
            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)
        else:
            content = json.dumps({"status": "OK", "rate": currency_rate_content})
            self.send_response(HTTPStatus.OK)

        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()
        self.wfile.write(content.encode())

    def _get_exchange_rate(self, base_currency='EUR', target_currency='RUB'):
        logger.info("Getting exchange rate: base currency %s", base_currency)
        pr = ExchangeInfoProvider()
        if rate := pr.get_rate(base=base_currency, target=target_currency):
            return {base_currency: rate}

        raise self.GetRateException("Couldn't get currency rate...")


if __name__ == '__main__':
    pr = ExchangeInfoProvider()
    print(pr.get_rate())
