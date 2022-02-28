from dataclasses import dataclass

from .files import FileInfo

from dbupgrade.version import VersionMatcher


@dataclass
class Filter:
    schema: str
    dialect: str
    version_matcher: VersionMatcher

    def matches(self, file_info: FileInfo) -> bool:
        return (
            file_info.schema == self.schema
            and file_info.dialect == self.dialect
            and self.version_matcher.matches(file_info)
        )
