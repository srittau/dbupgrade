from __future__ import annotations

from dataclasses import dataclass

from .files import FileInfo

from dbupgrade.args import Arguments

MAX_VERSION = 999999
MAX_API_LEVEL = 999999


@dataclass
class VersionInfo:
    max_version: int = MAX_API_LEVEL
    api_level: int | None = None


def version_info_from_args(args: Arguments) -> VersionInfo:
    if args.ignore_api_level and args.api_level is not None:
        raise ValueError(
            "ignore_api_level and api_level are mutually exclusive"
        )

    return VersionInfo(
        args.max_version if args.max_version is not None else MAX_VERSION,
        MAX_API_LEVEL if args.ignore_api_level else args.api_level,
    )


class VersionMatcher:
    def __init__(
        self, min_version: int, max_version: int, target_api_level: int
    ) -> None:
        self.min_version = min_version
        self.max_version = max_version
        self.target_api_level = target_api_level

        if self.max_version < self.min_version:
            raise ValueError("max_version smaller than min_version")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionMatcher):
            return NotImplemented
        return (self.min_version, self.max_version, self.target_api_level) == (
            other.min_version,
            other.max_version,
            other.target_api_level,
        )

    def matches(self, file_info: FileInfo) -> bool:
        return (
            self.min_version <= file_info.version <= self.max_version
            and file_info.api_level <= self.target_api_level
        )


def create_version_matcher(
    info: VersionInfo, min_version: int, api_level: int
) -> VersionMatcher:
    if info.api_level is not None:
        target_api_level = info.api_level
    else:
        target_api_level = api_level

    return VersionMatcher(min_version, info.max_version, target_api_level)
