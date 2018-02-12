from unittest import TestCase

from asserts import assert_equal

from dbupgrade.url import dialect_from_url


class DialectFromURLTest(TestCase):

    def test_without_lib(self) -> None:
        url = "postgres://localhost/foo"
        dialect = dialect_from_url(url)
        assert_equal("postgres", dialect)

    def test_with_lib(self) -> None:
        url = "postgres+psycopg2://localhost/foo"
        dialect = dialect_from_url(url)
        assert_equal("postgres", dialect)
