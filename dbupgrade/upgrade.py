import logging
from typing import List, Sequence

from dbupgrade.apply import apply_files
from dbupgrade.args import Arguments
from dbupgrade.db import fetch_current_db_versions
from dbupgrade.files import FileInfo, collect_sql_files
from dbupgrade.filter import Filter, filter_from_arguments
from dbupgrade.sql_file import parse_sql_files


def db_upgrade(args: Arguments) -> None:
    filter_ = create_filter(args)
    files = read_files_to_apply(args.script_path, filter_)
    apply_files(args.db_url, files)


def create_filter(args: Arguments) -> Filter:
    version, api_level = fetch_current_db_versions(args.db_url, args.schema)
    logging.info(
        "current version: {version}, current API level: {api_level}".format(
            version=version, api_level=api_level
        )
    )
    return filter_from_arguments(args, version + 1, api_level)


def read_files_to_apply(script_path: str, filter_: Filter) -> List[FileInfo]:
    files = parse_sql_files(collect_sql_files(script_path))
    return filter_files(files, filter_)


def filter_files(files: Sequence[FileInfo], filter_: Filter) -> List[FileInfo]:
    matching = [f for f in files if filter_.matches(f)]
    matching.sort()
    return matching
