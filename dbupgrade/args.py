from __future__ import annotations

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class Arguments:
    schema: str
    db_url: str
    script_path: str
    api_level: int | None = None
    max_version: int | None = None
    ignore_api_level: bool = False
    quiet: bool = False
    json: bool = False

    def __post_init__(self) -> None:
        if self.ignore_api_level and self.api_level is not None:
            raise ValueError(
                "ignore_api_level and api_level are mutually exclusive"
            )


def arguments_from_args(args: Namespace) -> Arguments:
    return Arguments(
        args.schema,
        args.db_url,
        args.script_path,
        args.api_level,
        args.max_version,
        args.ignore_api_level,
        args.quiet,
        args.json,
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="print upgrade information as JSON, implies -q",
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
