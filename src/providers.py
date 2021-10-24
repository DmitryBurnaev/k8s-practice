import json
import os
import logging
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


if __name__ == '__main__':
    pr = ExchangeInfoProvider()
    print(pr.get_rate())
