import os.path
from os import listdir
from typing import List


class FileInfo:

    def __init__(self, schema: str, dialect: str, version: int,
                 api_level: int) -> None:
        self.schema = schema
        self.dialect = dialect
        self.version = version
        self.api_level = api_level

    def __lt__(self, other: "FileInfo") -> bool:
        if self.schema != other.schema or self.dialect != other.dialect:
            raise TypeError("FileInfos must have the same schema and dialect")
        return self.version < other.version

    def __repr__(self) -> str:
        return f"FileInfo({repr(self.schema)}, {repr(self.dialect)}, " \
               f"{self.version}, {self.api_level})"


def collect_sql_files(directory: str) -> List[str]:
    return [os.path.join(directory, fn) for fn
            in listdir(directory) if fn.endswith(".sql")]
