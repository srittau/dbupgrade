import logging
from typing import Sequence

from dbupgrade.db import execute_stream
from dbupgrade.files import FileInfo


def apply_files(db_url: str, files: Sequence[FileInfo]) -> None:
    for file_info in files:
        apply_file(db_url, file_info)


def apply_file(db_url: str, file_info: FileInfo) -> None:
    logging.info(
        f"applying #{file_info.version} (API level {file_info.api_level})")
    with open(file_info.filename, "r") as stream:
        execute_stream(db_url, stream, file_info.schema,
                       file_info.version, file_info.api_level)
