# News in dbupgrade 2023.10.0

Drop support for Python 3.7 and 3.8.

dbupgrade is now easier to use as a library:
  - `db_upgrade`, `VersionInfo`, `MAX_VERSION`, and `MAX_API_LEVEL` are now
    re-exported from `dbupgrade`.
  - Add a `py.typed` file to indicate that dbupgrade is a typed package.

# News in dbupgrade 2023.2.0

Switch to Calendar Versioning (CalVer).

- Fix percent characters when using SQLAlchemy 1 as well.

# News in dbupgrade 2.3.3

- Don't escape percent characters when using SQLAlchemy 2.

# News in dbupgrade 2.3.2

- Make compatible with SQLAlchemy 2.

# News in dbupgrade 2.3.1

- Improve forwards compatibility with SQLAlchemy 2.

# News in dbupgrade 2.3.0

- Add a `--json` option to print update information in JSON format.

# News in dbupgrade 2.2.0

- Return with exit code 1 when encountering an SQL error.

# News in dbupgrade 2.1.1

- Print proper error message, instead of a traceback when encountering
  an SQL error.

# News in dbupgrade 2.1.0

- Add `dbupgrade.__main__`. `dbupgrade` can now be executed using
  `python3 -m dbupgrade`.

# News in dbupgrade 2.0.1

## Bug Fixes

- Fix a warning about isolation_level when using `-- Transaction: no`.

# News in dbupgrade 2.0.0

## Incompatible Changes

- Drop support for Python 3.5 and 3.6.
- Use sqlparse to split SQL statements. While this will provide greater
  SQL compatibility overall, it may be incompatible with some existing
  SQL files.

# News in dbupgrade 1.0.0

## Improvements

- Add `--quiet` option.

# News in dbupgrade 0.2.2

## Improvements

- Relax type requirements for the `stream` arguments of
  `parse_sql_stream()`, `split_sql()`, and `execute_stream()`.

## Bug Fixes

- Fix escaping of percent signs.

# News in dbupgrade 0.2.1

- Python 3.5 compatibility.

# News in dbupgrade 0.2.0

## New Features

- Add a new file header `Transaction` to disable transaction handling
  for this file.
