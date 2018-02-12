class FileInfo:

    def __init__(self, schema: str, dialect: str, version: int,
                 api_level: int) -> None:
        self.schema = schema
        self.dialect = dialect
        self.version = version
        self.api_level = api_level
