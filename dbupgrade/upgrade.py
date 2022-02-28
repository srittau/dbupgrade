from __future__ import annotations

import logging
from typing import List, Sequence

from .apply import apply_files
from .db import fetch_current_db_versions
from .files import FileInfo, collect_sql_files
from .filter import Filter
from .result import UpgradeResult, VersionResult
from .sql_file import parse_sql_files
from .url import dialect_from_url
from .version import VersionInfo, create_version_matcher


def db_upgrade(
    schema: str,
    db_url: str,
    script_path: str,
    version_info: VersionInfo,
) -> UpgradeResult:
    old_version, old_api_level, filter_ = create_filter(
        schema, db_url, version_info
    )
    files = read_files_to_apply(script_path, filter_)
    applied_scripts, failed_script = apply_files(db_url, files)
    try:
        new_version = applied_scripts[-1].version
        new_api_level = applied_scripts[-1].api_level
    except IndexError:
        new_version = old_version
        new_api_level = old_api_level
    return UpgradeResult(
        VersionResult(old_version, old_api_level),
        VersionResult(new_version, new_api_level),
        applied_scripts,
        failed_script,
    )


def create_filter(
    schema: str, db_url: str, version_info: VersionInfo
) -> tuple[int, int, Filter]:
    version, api_level = fetch_current_db_versions(db_url, schema)
    logging.info(
        "current version: {version}, current API level: {api_level}".format(
            version=version, api_level=api_level
        )
    )
    matcher = create_version_matcher(version_info, version + 1, api_level)
    dialect = dialect_from_url(db_url)
    return version, api_level, Filter(schema, dialect, matcher)


def read_files_to_apply(script_path: str, filter_: Filter) -> List[FileInfo]:
    files = parse_sql_files(collect_sql_files(script_path))
    return filter_files(files, filter_)


def filter_files(files: Sequence[FileInfo], filter_: Filter) -> List[FileInfo]:
    matching = [f for f in files if filter_.matches(f)]
    matching.sort()
    return matching
