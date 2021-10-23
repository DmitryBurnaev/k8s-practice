import json
import os

from urllib.request import urlopen


class ExchangeInfoProvider:
    source_url = 'http://data.fixer.io/api/latest'
    source_api_key = os.getenv('FIXER_API_KEY')

    def get_rate(self):
        url = f'{self.source_url}?access_key={self.source_api_key}&format=1&base=EUR&symbols=RUB'
        print(url)
        try:
            with urlopen(url) as resp:
                response_text = resp.read().decode()
                response_data = json.loads(response_text)
        except Exception as err:
            print(err)

        print(response_data)
        return response_data


if __name__ == '__main__':
    pr = ExchangeInfoProvider()
    pr.get_rate()
