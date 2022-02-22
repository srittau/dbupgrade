import logging
from typing import List, Sequence

from dbupgrade.apply import apply_files
from dbupgrade.db import fetch_current_db_versions
from dbupgrade.files import FileInfo, collect_sql_files
from dbupgrade.filter import Filter
from dbupgrade.sql_file import parse_sql_files
from dbupgrade.url import dialect_from_url
from dbupgrade.version import VersionInfo, create_version_matcher


def db_upgrade(
    schema: str,
    db_url: str,
    script_path: str,
    version_info: VersionInfo,
) -> bool:
    filter_ = create_filter(schema, db_url, version_info)
    files = read_files_to_apply(script_path, filter_)
    return apply_files(db_url, files)


def create_filter(
    schema: str, db_url: str, version_info: VersionInfo
) -> Filter:
    version, api_level = fetch_current_db_versions(db_url, schema)
    logging.info(
        "current version: {version}, current API level: {api_level}".format(
            version=version, api_level=api_level
        )
    )
    matcher = create_version_matcher(version_info, version + 1, api_level)
    dialect = dialect_from_url(db_url)
    return Filter(schema, dialect, matcher)


def read_files_to_apply(script_path: str, filter_: Filter) -> List[FileInfo]:
    files = parse_sql_files(collect_sql_files(script_path))
    return filter_files(files, filter_)


def filter_files(files: Sequence[FileInfo], filter_: Filter) -> List[FileInfo]:
    matching = [f for f in files if filter_.matches(f)]
    matching.sort()
    return matching
