import json
import logging
import socket
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from src.providers import ExchangeInfoProvider

logger = logging.getLogger(__name__)


class CurrencyExchangeServer(ThreadingHTTPServer):

    def __init__(self, bind: str, port: int):
        self.address_family, sock_address = self._get_best_family(bind, port)
        super().__init__(sock_address, CurrencyExchangeHTTPHandler)

    def __enter__(self):
        host, port = self.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        # logger.info(f"Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...")
        print(f"Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...")
        return super().__enter__()

    @staticmethod
    def _get_best_family(*address):
        infos = socket.getaddrinfo(
            *address,
            type=socket.SOCK_STREAM,
            flags=socket.AI_PASSIVE,
        )
        family, *_, sockaddr = next(iter(infos))
        return family, sockaddr


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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", "-b", metavar="ADDRESS",
                        help='Specify alternate bind address [default: all interfaces]')
    parser.add_argument("port", action="store", default=8000, type=int,
                        nargs="?", help="Specify alternate port [default: 8000]")
    args = parser.parse_args()

    with CurrencyExchangeServer(args.bind, args.port) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)
