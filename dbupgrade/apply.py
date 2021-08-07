import logging
from typing import Sequence

from sqlalchemy.exc import SQLAlchemyError

from dbupgrade.db import update_sql
from dbupgrade.files import FileInfo


def apply_files(db_url: str, files: Sequence[FileInfo]) -> None:
    for file_info in files:
        try:
            apply_file(db_url, file_info)
        except SQLAlchemyError as exc:
            logging.error(str(exc))
            return


def apply_file(db_url: str, file_info: FileInfo) -> None:
    logging.info(
        "applying #{0.version} (API level {0.api_level})".format(file_info)
    )
    with open(file_info.filename, "r") as stream:
        sql = stream.read()
        update_sql(
            db_url,
            sql,
            file_info.schema,
            file_info.version,
            file_info.api_level,
            transaction=file_info.transaction,
        )
