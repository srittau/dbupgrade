import logging
import sys

from dbupgrade.args import parse_args
from dbupgrade.upgrade import db_upgrade


def main() -> None:
    try:
        logging.basicConfig(level=logging.INFO)
        args = parse_args(sys.argv)
        db_upgrade(args)
    except KeyboardInterrupt:
        pass
