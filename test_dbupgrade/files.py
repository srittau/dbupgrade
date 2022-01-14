import os.path
from unittest.mock import patch

import pytest

from dbupgrade.files import FileInfo, collect_sql_files


class TestFileInfo:
    def test_lt(self) -> None:
        fi1 = FileInfo("", "schema", "postgres", 4, 0)
        fi2 = FileInfo("", "schema", "postgres", 5, 0)
        assert fi1 < fi2
        assert not (fi2 < fi1)

    def test_lt__non_matching_schemas(self) -> None:
        fi1 = FileInfo("", "schema1", "postgres", 4, 0)
        fi2 = FileInfo("", "schema2", "postgres", 5, 0)
        with pytest.raises(TypeError):
            fi1 < fi2

    def test_lt__non_matching_dialects(self) -> None:
        fi1 = FileInfo("", "schema", "postgres", 4, 0)
        fi2 = FileInfo("", "schema", "mysql", 5, 0)
        with pytest.raises(TypeError):
            fi1 < fi2

    def test_repr(self) -> None:
        fi = FileInfo("/foo/bar", "myschema", "postgres", 123, 13)
        assert (
            repr(fi) == "FileInfo('/foo/bar', 'myschema', 'postgres', 123, 13)"
        )


class TestCollectSQLFiles:
    def test_filter_sql_files(self) -> None:
        with patch("dbupgrade.files.listdir") as listdir:
            listdir.return_value = ["foo", "bar.sql", "baz.sql"]
            files = collect_sql_files("tmp")
            listdir.assert_called_with("tmp")
        expected_files = [
            os.path.join("tmp", "bar.sql"),
            os.path.join("tmp", "baz.sql"),
        ]
        assert files == expected_files
