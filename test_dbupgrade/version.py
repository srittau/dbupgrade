from __future__ import annotations

import pytest

from dbupgrade.files import FileInfo
from dbupgrade.version import (
    MAX_VERSION,
    VersionInfo,
    VersionMatcher,
    create_version_matcher,
)


class TestVersionMatcher:
    def test_init__max_version_equals_min_version(self) -> None:
        VersionMatcher(5, 5, 3)

    def test_init__max_version_smaller_than_min_version(self) -> None:
        with pytest.raises(ValueError):
            VersionMatcher(5, 4, 3)

    def test_matches__version_matches_lower(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 5, 2)
        assert matcher.matches(file_info)

    def test_matches__version_in_between(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 7, 2)
        assert matcher.matches(file_info)

    def test_matches__version_matches_upper(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 10, 2)
        assert matcher.matches(file_info)

    def test_matches__api_level_match(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 7, 3)
        assert matcher.matches(file_info)

    def test_matches__min_version_too_small(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 4, 2)
        assert not matcher.matches(file_info)

    def test_matches__min_version_too_large(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 11, 2)
        assert not matcher.matches(file_info)

    def test_matches__api_level_too_large(self) -> None:
        matcher = VersionMatcher(5, 10, 3)
        file_info = FileInfo("", "", "", 7, 4)
        assert not matcher.matches(file_info)


class TestCreateVersionMatcher:
    def test_min_version(self) -> None:
        matcher = create_version_matcher(VersionInfo(), 13, 12)
        assert matcher.min_version == 13

    def test_max_version_default(self) -> None:
        matcher = create_version_matcher(VersionInfo(), 0, 12)
        assert matcher.max_version == MAX_VERSION

    def test_max_version(self) -> None:
        matcher = create_version_matcher(VersionInfo(55), 0, 12)
        assert matcher.max_version == 55

    def test_target_api_level_none(self) -> None:
        matcher = create_version_matcher(VersionInfo(api_level=None), 0, 34)
        assert matcher.target_api_level == 34

    def test_target_api_level(self) -> None:
        matcher = create_version_matcher(VersionInfo(api_level=44), 0, 34)
        assert matcher.target_api_level == 44
