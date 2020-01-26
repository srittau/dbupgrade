from argparse import ArgumentParser, Namespace
from typing import Optional, Sequence


class Arguments:
    def __init__(
        self,
        schema: str,
        db_url: str,
        script_path: str,
        api_level: Optional[int] = None,
        max_version: Optional[int] = None,
        ignore_api_level: bool = False,
        quiet: bool = False,
    ) -> None:
        if ignore_api_level and api_level is not None:
            raise ValueError(
                "ignore_api_level and api_level are mutually exclusive"
            )
        self.schema = schema
        self.db_url = db_url
        self.script_path = script_path
        self.has_explicit_api_level = api_level is not None
        self.api_level = api_level or 0
        self.ignore_api_level = ignore_api_level
        self.has_max_version = max_version is not None
        self.max_version = max_version or 0
        self.quiet = quiet


def arguments_from_args(args: Namespace) -> Arguments:
    return Arguments(
        args.schema,
        args.db_url,
        args.script_path,
        args.api_level,
        args.max_version,
        args.ignore_api_level,
        args.quiet,
    )


def parse_args(argv: Sequence[str]) -> Arguments:
    parser = ArgumentParser(
        prog=argv[0], description="upgrade a database schema"
    )
    parser.add_argument("schema", help="database schema to upgrade")
    parser.add_argument("db_url", help="URL of the database to upgrade")
    parser.add_argument(
        "script_path", help="directory that contains the SQL scripts"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress informational output",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l", "--api-level", help="maximum API level to upgrade to", type=int
    )
    group.add_argument(
        "-L",
        "--ignore-api-level",
        action="store_true",
        help="upgrade all scripts no matter the API level",
    )
    parser.add_argument(
        "-m", "--max-version", help="maximum version to upgrade to", type=int
    )
    args = parser.parse_args(argv[1:])
    return arguments_from_args(args)
