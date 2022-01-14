from typing import Optional

import pytest

from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.filter import (
    MAX_API_LEVEL,
    MAX_VERSION,
    Filter,
    filter_from_arguments,
)


class TestFilter:
    def test_init(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        assert filter_.schema == "myschema"
        assert filter_.dialect == "postgres"
        assert filter_.min_version == 5
        assert filter_.max_version == 10
        assert filter_.target_api_level == 3

    def test_init__max_version_equals_min_version(self) -> None:
        Filter("myschema", "postgres", 5, 5, 3)

    def test_init__max_version_smaller_than_min_version(self) -> None:
        with pytest.raises(ValueError):
            Filter("myschema", "postgres", 5, 4, 3)

    def test_matches__version_matches_lower(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 5, 2)
        assert filter_.matches(file_info)

    def test_matches__version_in_between(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 2)
        assert filter_.matches(file_info)

    def test_matches__version_matches_upper(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 10, 2)
        assert filter_.matches(file_info)

    def test_matches__api_level_match(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 3)
        assert filter_.matches(file_info)

    def test_matches__wrong_schema(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "wrongschema", "postgres", 5, 2)
        assert not filter_.matches(file_info)

    def test_matches__wrong_dialect(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "mysql", 5, 2)
        assert not filter_.matches(file_info)

    def test_matches__min_version_too_small(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 4, 2)
        assert not filter_.matches(file_info)

    def test_matches__min_version_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 11, 2)
        assert not filter_.matches(file_info)

    def test_matches__api_level_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 4)
        assert not filter_.matches(file_info)


class TestFilterFromArguments:
    def _create_arguments(
        self,
        *,
        schema: str = "testschema",
        db_url: str = "postgres://localhost/foo",
        max_api_level: Optional[int] = None,
        max_version: Optional[int] = None,
        ignore_api_level: bool = False
    ) -> Arguments:
        return Arguments(
            schema,
            db_url,
            "/tmp",
            max_api_level,
            max_version,
            ignore_api_level=ignore_api_level,
        )

    def test_schema(self) -> None:
        args = self._create_arguments(schema="myschema")
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.schema == "myschema"

    def test_dialect(self) -> None:
        args = self._create_arguments(
            db_url="postgres+psycopg2://localhost/foo"
        )
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.dialect == "postgres"

    def test_min_version(self) -> None:
        args = self._create_arguments()
        filter_ = filter_from_arguments(args, 13, 0)
        assert filter_.min_version == 13

    def test_max_version_default(self) -> None:
        args = self._create_arguments(max_version=None)
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.max_version == MAX_VERSION

    def test_max_version_explicit(self) -> None:
        args = self._create_arguments(max_version=34)
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.max_version == 34

    def test_target_api_level_default(self) -> None:
        args = self._create_arguments(
            max_api_level=None, ignore_api_level=False
        )
        filter_ = filter_from_arguments(args, 0, 12)
        assert filter_.target_api_level == 12

    def test_target_api_level_ignore(self) -> None:
        args = self._create_arguments(ignore_api_level=True)
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.target_api_level == MAX_API_LEVEL

    def test_target_api_level_explicit(self) -> None:
        args = self._create_arguments(max_api_level=12)
        filter_ = filter_from_arguments(args, 0, 0)
        assert filter_.target_api_level == 12
