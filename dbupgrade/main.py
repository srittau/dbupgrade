import logging
import sys

from dbupgrade.args import parse_args
from dbupgrade.upgrade import db_upgrade


def main() -> None:
    try:
        args = parse_args(sys.argv)
        log_level = logging.WARNING if args.quiet else logging.INFO
        logging.basicConfig(level=log_level)
        if not db_upgrade(args):
            sys.exit(1)
    except KeyboardInterrupt:
        pass
