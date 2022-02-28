from __future__ import annotations

from dataclasses import dataclass

from .files import FileInfo


@dataclass
class UpgradeResult:
    old_version: VersionResult
    new_version: VersionResult
    applied_scripts: list[FileInfo]
    failed_script: FileInfo | None = None

    @property
    def success(self) -> bool:
        return self.failed_script is None


@dataclass
class VersionResult:
    version: int
    api_level: int
