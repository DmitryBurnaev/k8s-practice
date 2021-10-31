import os
import sys
import socket
import argparse
import logging.config
from http.server import ThreadingHTTPServer

from src.handlers import CurrencyExchangeHTTPHandler

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d.%m.%Y %H:%M:%S",
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "standard"}},
    "loggers": {
        "app": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": True},
        "handlers": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
})
logger = logging.getLogger(__name__)


class CurrencyExchangeServer(ThreadingHTTPServer):

    def __init__(self, bind: str, port: int):
        self.address_family, sock_address = self._get_best_family(bind, port)
        super().__init__(sock_address, CurrencyExchangeHTTPHandler)

    def __enter__(self):
        host, port = self.socket.getsockname()[:2]
        url_host = f'[{host}]' if ':' in host else host
        # TODO: fix logging
        logger.info(f"Serving HTTP on {host} port {port} (http://{url_host}:{port}/) ...")
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


if __name__ == "__main__":
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
