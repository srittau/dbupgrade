from asserts import assert_equal
from dectest import TestCase, test

from dbupgrade.url import dialect_from_url


class DialectFromURLTest(TestCase):
    @test
    def without_lib(self) -> None:
        url = "postgres://localhost/foo"
        dialect = dialect_from_url(url)
        assert_equal("postgres", dialect)

    @test
    def with_lib(self) -> None:
        url = "postgres+psycopg2://localhost/foo"
        dialect = dialect_from_url(url)
        assert_equal("postgres", dialect)
