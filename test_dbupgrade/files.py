from unittest import TestCase

from asserts import assert_true, assert_false, assert_raises, assert_equal

from dbupgrade.files import FileInfo


class FileInfoTest(TestCase):

    def test_lt(self) -> None:
        fi1 = FileInfo("schema", "postgres", 4, 0)
        fi2 = FileInfo("schema", "postgres", 5, 0)
        assert_true(fi1 < fi2)
        assert_false(fi2 < fi1)

    def test_lt__non_matching_schemas(self) -> None:
        fi1 = FileInfo("schema1", "postgres", 4, 0)
        fi2 = FileInfo("schema2", "postgres", 5, 0)
        with assert_raises(TypeError):
            fi1 < fi2

    def test_lt__non_matching_dialects(self) -> None:
        fi1 = FileInfo("schema", "postgres", 4, 0)
        fi2 = FileInfo("schema", "mysql", 5, 0)
        with assert_raises(TypeError):
            fi1 < fi2

    def test_repr(self) -> None:
        fi = FileInfo("myschema", "postgres", 123, 13)
        assert_equal("FileInfo('myschema', 'postgres', 123, 13)", repr(fi))
