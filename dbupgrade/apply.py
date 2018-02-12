from typing import Sequence

from dbupgrade.files import FileInfo


def apply_files(db_url: str, files: Sequence[FileInfo]) -> None:
    raise NotImplementedError("apply_files()")
