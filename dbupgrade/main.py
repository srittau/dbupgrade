import logging
import sys

from dbupgrade.args import parse_args
from dbupgrade.upgrade import db_upgrade


def main() -> None:
    try:
        args = parse_args(sys.argv)
        log_level = logging.WARNING if args.quiet else logging.INFO
        logging.basicConfig(level=log_level)
        db_upgrade(args)
    except KeyboardInterrupt:
        pass
