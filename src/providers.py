import os


class ExchangeInfoProvider:
    source_url = 'http://data.fixer.io/api/latest'
    source_api_key = os.getenv('FIXER_API_KEY')

    def get_rate(self):
        url = f'{self.source_url}?access_key={self.source_api_key}&format=1&base=EUR&symbols=RUB'
        return {}
