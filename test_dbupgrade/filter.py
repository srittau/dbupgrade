from dbupgrade.files import FileInfo
from dbupgrade.filter import Filter
from dbupgrade.version import VersionMatcher


class TestFilter:
    def test_init(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        assert filter_.schema == "myschema"
        assert filter_.dialect == "postgres"
        assert filter_.version_info == VersionMatcher(5, 10, 3)

    def test_matches__version_matches_lower(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 5, 2)
        assert filter_.matches(file_info)

    def test_matches__version_in_between(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 7, 2)
        assert filter_.matches(file_info)

    def test_matches__version_matches_upper(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 10, 2)
        assert filter_.matches(file_info)

    def test_matches__api_level_match(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 7, 3)
        assert filter_.matches(file_info)

    def test_matches__wrong_schema(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "wrongschema", "postgres", 5, 2)
        assert not filter_.matches(file_info)

    def test_matches__wrong_dialect(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "mysql", 5, 2)
        assert not filter_.matches(file_info)

    def test_matches__min_version_too_small(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 4, 2)
        assert not filter_.matches(file_info)

    def test_matches__min_version_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 11, 2)
        assert not filter_.matches(file_info)

    def test_matches__api_level_too_large(self) -> None:
        filter_ = Filter("myschema", "postgres", VersionMatcher(5, 10, 3))
        file_info = FileInfo("", "myschema", "postgres", 7, 4)
        assert not filter_.matches(file_info)
