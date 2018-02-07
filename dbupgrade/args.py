from argparse import ArgumentParser, Namespace
from typing import Sequence


class Arguments:

    def __init__(self, args: Namespace) -> None:
        self.schema = args.schema
        self.db_url = args.db_url
        self.script_path = args.script_path
        self.has_explicit_api_level = args.api_level is not None
        self.api_level = args.api_level or 0
        self.ignore_api_level = args.ignore_api_level
        self.has_max_version = args.max_version is not None
        self.max_version = args.max_version or 0


def parse_args(argv: Sequence[str]) -> Arguments:
    parser = ArgumentParser(prog=argv[0], description="upgrade a database schema")
    parser.add_argument("schema", help="database schema to upgrade")
    parser.add_argument("db_url", help="URL of the database to upgrade")
    parser.add_argument(
        "script_path", help="directory that contains the SQL scripts")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l", "--api-level", help="maximum API level to upgrade to", type=int)
    group.add_argument(
        "-L", "--ignore-api-level", action="store_true",
        help="upgrade all scripts no matter the API level")
    parser.add_argument(
        "-m", "--max-version", help="maximum version to upgrade to", type=int)
    args = parser.parse_args(argv[1:])
    return Arguments(args)
