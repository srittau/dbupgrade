from typing import Optional

from asserts import (
    assert_true,
    assert_false,
    assert_equal,
    assert_raises,
    assert_succeeds,
)

from dectest import TestCase, test

from dbupgrade.args import Arguments
from dbupgrade.files import FileInfo
from dbupgrade.filter import (
    Filter,
    filter_from_arguments,
    MAX_VERSION,
    MAX_API_LEVEL,
)


class FilterTest(TestCase):
    @test
    def init(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        assert_equal("myschema", filter_.schema)
        assert_equal("postgres", filter_.dialect)
        assert_equal(5, filter_.min_version)
        assert_equal(10, filter_.max_version)
        assert_equal(3, filter_.target_api_level)

    @test
    def init__max_version_equals_min_version(self) -> None:
        with assert_succeeds(ValueError):
            Filter("myschema", "postgres", 5, 5, 3)

    @test
    def init__max_version_smaller_than_min_version(self) -> None:
        with assert_raises(ValueError):
            Filter("myschema", "postgres", 5, 4, 3)

    @test
    def matches__version_matches_lower(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 5, 2)
        assert_true(filter_.matches(file_info))

    @test
    def matches__version_in_between(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 2)
        assert_true(filter_.matches(file_info))

    @test
    def matches__version_matches_upper(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 10, 2)
        assert_true(filter_.matches(file_info))

    @test
    def matches__api_level_match(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 3)
        assert_true(filter_.matches(file_info))

    @test
    def matches__wrong_schema(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "wrongschema", "postgres", 5, 2)
        assert_false(filter_.matches(file_info))

    @test
    def matches__wrong_dialect(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "mysql", 5, 2)
        assert_false(filter_.matches(file_info))

    @test
    def matches__min_version_too_small(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 4, 2)
        assert_false(filter_.matches(file_info))

    @test
    def matches__min_version_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 11, 2)
        assert_false(filter_.matches(file_info))

    @test
    def matches__api_level_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", 5, 10, 3)
        file_info = FileInfo("", "myschema", "postgres", 7, 4)
        assert_false(filter_.matches(file_info))


class FilterFromArgumentsTest(TestCase):
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

    @test
    def schema(self) -> None:
        args = self._create_arguments(schema="myschema")
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal("myschema", filter_.schema)

    @test
    def dialect(self) -> None:
        args = self._create_arguments(
            db_url="postgres+psycopg2://localhost/foo"
        )
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal("postgres", filter_.dialect)

    @test
    def min_version(self) -> None:
        args = self._create_arguments()
        filter_ = filter_from_arguments(args, 13, 0)
        assert_equal(13, filter_.min_version)

    @test
    def max_version_default(self) -> None:
        args = self._create_arguments(max_version=None)
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal(MAX_VERSION, filter_.max_version)

    @test
    def max_version_explicit(self) -> None:
        args = self._create_arguments(max_version=34)
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal(34, filter_.max_version)

    @test
    def target_api_level_default(self) -> None:
        args = self._create_arguments(
            max_api_level=None, ignore_api_level=False
        )
        filter_ = filter_from_arguments(args, 0, 12)
        assert_equal(12, filter_.target_api_level)

    @test
    def target_api_level_ignore(self) -> None:
        args = self._create_arguments(ignore_api_level=True)
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal(MAX_API_LEVEL, filter_.target_api_level)

    @test
    def target_api_level_explicit(self) -> None:
        args = self._create_arguments(max_api_level=12)
        filter_ = filter_from_arguments(args, 0, 0)
        assert_equal(12, filter_.target_api_level)
