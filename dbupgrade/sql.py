from typing import Sequence, List

from dbupgrade.files import FileInfo


def parse_sql_files(files: Sequence[str]) -> List[FileInfo]:
    raise NotImplementedError("parse_sql_files")
