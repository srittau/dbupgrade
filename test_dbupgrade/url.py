from dbupgrade.url import dialect_from_url


class TestDialectFromURL:
    def test_without_lib(self) -> None:
        url = "postgres://localhost/foo"
        dialect = dialect_from_url(url)
        assert dialect == "postgres"

    def test_with_lib(self) -> None:
        url = "postgres+psycopg2://localhost/foo"
        dialect = dialect_from_url(url)
        assert dialect == "postgres"
