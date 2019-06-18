import os.path
from unittest.mock import patch

from asserts import assert_true, assert_false, assert_raises, assert_equal

from dectest import TestCase, test

from dbupgrade.files import FileInfo, collect_sql_files


class FileInfoTest(TestCase):
    @test
    def lt(self) -> None:
        fi1 = FileInfo("", "schema", "postgres", 4, 0)
        fi2 = FileInfo("", "schema", "postgres", 5, 0)
        assert_true(fi1 < fi2)
        assert_false(fi2 < fi1)

    @test
    def lt__non_matching_schemas(self) -> None:
        fi1 = FileInfo("", "schema1", "postgres", 4, 0)
        fi2 = FileInfo("", "schema2", "postgres", 5, 0)
        with assert_raises(TypeError):
            fi1 < fi2

    @test
    def lt__non_matching_dialects(self) -> None:
        fi1 = FileInfo("", "schema", "postgres", 4, 0)
        fi2 = FileInfo("", "schema", "mysql", 5, 0)
        with assert_raises(TypeError):
            fi1 < fi2

    @test
    def repr(self) -> None:
        fi = FileInfo("/foo/bar", "myschema", "postgres", 123, 13)
        assert_equal(
            "FileInfo('/foo/bar', 'myschema', 'postgres', 123, 13)", repr(fi)
        )


class CollectSQLFilesTest(TestCase):
    @test
    def filter_sql_files(self) -> None:
        with patch("dbupgrade.files.listdir") as listdir:
            listdir.return_value = ["foo", "bar.sql", "baz.sql"]
            files = collect_sql_files("tmp")
            listdir.assert_called_with("tmp")
        expected_files = [
            os.path.join("tmp", "bar.sql"),
            os.path.join("tmp", "baz.sql"),
        ]
        assert_equal(expected_files, files)
