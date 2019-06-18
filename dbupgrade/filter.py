from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.url import dialect_from_url

MAX_API_LEVEL = 999999
MAX_VERSION = 999999


class Filter:
    def __init__(
        self,
        schema: str,
        dialect: str,
        min_version: int,
        max_version: int,
        target_api_level: int,
    ) -> None:
        if max_version < min_version:
            raise ValueError("max_version smaller than min_version")
        self.schema = schema
        self.dialect = dialect
        self.min_version = min_version
        self.max_version = max_version
        self.target_api_level = target_api_level

    def matches(self, file_info: FileInfo) -> bool:
        return (
            file_info.schema == self.schema
            and file_info.dialect == self.dialect
            and self.min_version <= file_info.version <= self.max_version
            and file_info.api_level <= self.target_api_level
        )


def filter_from_arguments(
    args: Arguments, version: int, api_level: int
) -> Filter:
    if args.has_explicit_api_level:
        target_api_level = args.api_level
    elif args.ignore_api_level:
        target_api_level = MAX_API_LEVEL
    else:
        target_api_level = api_level
    max_version = args.max_version if args.has_max_version else MAX_VERSION

    dialect = dialect_from_url(args.db_url)

    return Filter(args.schema, dialect, version, max_version, target_api_level)
