import logging
import sys

from dbupgrade.args import parse_args
from dbupgrade.upgrade import db_upgrade
from dbupgrade.version import version_info_from_args


def main() -> None:
    try:
        args = parse_args(sys.argv)
        log_level = logging.WARNING if args.quiet else logging.INFO
        logging.basicConfig(level=log_level)
        if not db_upgrade(
            args.schema,
            args.db_url,
            args.script_path,
            version_info_from_args(args),
        ):
            sys.exit(1)
    except KeyboardInterrupt:
        pass
