# Changelog for dbupgrade

## [Unreleased]

### Added

- Add support for Python through 3.14.
- Re-export `UpgradeResult` and `VersionResult` from `dbupgrade`.
- Add `UpgradeResult.was_upgraded` property.

### Removed

- Drop support for Python 3.9.

## [2023.10.0]

### Added

- Make dbupgrade easier to use as a library:
  - `db_upgrade`, `VersionInfo`, `MAX_VERSION`, and `MAX_API_LEVEL` are now
    re-exported from `dbupgrade`.
  - Add a `py.typed` file to indicate that dbupgrade is a typed package.

### Removed

Drop support for Python 3.7 and 3.8.

## [2023.2.0]

Switch to Calendar Versioning (CalVer).

### Fixed

- Fix percent characters when using SQLAlchemy 1 as well.

## [2.3.3]

### Fixed

- Don't escape percent characters when using SQLAlchemy 2.

## [2.3.2]

### Added

- Make compatible with SQLAlchemy 2.

## [2.3.1]

### Changed

- Improve forwards compatibility with SQLAlchemy 2.

## [2.3.0]

### Added

- Add a `--json` option to print update information in JSON format.

## [2.2.0]

### Changed

- Return with exit code 1 when encountering an SQL error.

## [2.1.1]

### Fixed

- Print proper error message, instead of a traceback when encountering
  an SQL error.

## [2.1.0]

### Added

- Add `dbupgrade.__main__`. `dbupgrade` can now be executed using
  `python3 -m dbupgrade`.

## [2.0.1]

### Fixed

- Fix a warning about isolation_level when using `-- Transaction: no`.

## [2.0.0]

### Changed

- Use sqlparse to split SQL statements. While this will provide greater
  SQL compatibility overall, it may be incompatible with some existing
  SQL files.

### Removed

- Drop support for Python 3.5 and 3.6.

## [1.0.0]

### Added

- Add `--quiet` option.

## [0.2.2]

### Changed

- Relax type requirements for the `stream` arguments of
  `parse_sql_stream()`, `split_sql()`, and `execute_stream()`.

### Fixed

- Fix escaping of percent signs.

## [0.2.1]

### Added

- Python 3.5 compatibility.

## [0.2.0]

### Added

- Add a new file header `Transaction` to disable transaction handling
  for this file.
