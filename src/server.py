import json
import logging
import socket
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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

    def do_GET(self):
        content = json.dumps(self._get_exchange())
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()
        self.wfile.write(content.encode())

    @staticmethod
    def _get_exchange(base_currency='USD'):
        logger.info('Getting exchange rate: base currency %s', base_currency)
        return {'GBP': 1.4}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', metavar='ADDRESS',
                        help='Specify alternate bind address [default: all interfaces]')
    parser.add_argument('port', action='store', default=8000, type=int,
                        nargs='?', help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    with CurrencyExchangeServer(args.bind, args.port) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            sys.exit(0)
