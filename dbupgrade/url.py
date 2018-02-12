def dialect_from_url(url: str) -> str:
    return url.split(":")[0].split("+")[0]
