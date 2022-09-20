# dbupgrade

Database Migration Tool

[![Python](https://img.shields.io/pypi/pyversions/dbupgrade.svg)](https://pypi.python.org/pyversions/dbupgrade/)
[![MIT License](https://img.shields.io/pypi/l/dbupgrade.svg)](https://pypi.python.org/pypi/dbupgrade/)
[![GitHub](https://img.shields.io/github/release/srittau/dbupgrade/all.svg)](https://github.com/srittau/dbupgrade/releases/)
[![pypi](https://img.shields.io/pypi/v/dbupgrade.svg)](https://pypi.python.org/pypi/dbupgrade/)
[![GitHub Actions](https://img.shields.io/github/workflow/status/srittau/dbupgrade/Test%20and%20lint)](https://github.com/srittau/dbupgrade/actions)

## Basic Usage

Usage: `dbupgrade [OPTIONS] [-l API_LEVEL|-L] DBNAME SCHEMA DIRECTORY`

Upgrade the given `SCHEMA` in the database specified as `DBNAME` with SQL
scripts from `DIRECTORY`. `DIRECTORY` is searched for all files with the
`.sql` suffix. These files are SQL scripts with a special header sections:

```sql
-- Schema: my-db-schema
-- Version: 25
-- API-Level: 3
-- Dialect: postgres

CREATE TABLE ...
```

The following headers are required:

- **Schema**  
   Name of the schema to update.
- **Dialect**  
   Database dialect of this script. Use SQLalchemy's database
  URL scheme identifier, e.g. `postgres` or `sqlite`.
- **Version**  
   The new version of the schema after this script was applied.
  It is an error if two scripts have the same schema, dialect, and version.
- **API-Level**  
   The new API level of the schema after this script was applied.
  For a given schema, the API level of a subsequent version must either be
  equal or higher by one than the API level of the preceding version. For
  example, if script version 44 has API level 3, script version 45 must
  have API level 3 or 4.
- **Transaction** _(optional)_  
   Possible values are `yes` (default) and `no`. When this
  header is yes, all statements of a single upgrade file and the
  corresponding version upgrade statements are executed within a single
  transaction. Otherwise each statement is executed separately. The former
  is usually preferable so that all changes will be rolled back if a
  script fails to apply, but the latter is required in some cases.

The database must contain a table `db_config` with three columns: `schema`,
`version`, and `api_level`. If this table does not exist, it is created.
This table must contain exactly one row for the given schema. If this row
does not exist, it is created with version and api_level initially set to 0.

The current version and API level of the schema are requested from the
database and all scripts with a higher version number are applied, in order.
If there are any version numbers missing, the script will stop after the
last version before the missing version.

Unless the `-l` or `-L` option is supplied, only scripts that do not
increase the API level will be applied. If the `-l` option is given, all
scripts up to the given API level will be applied. `-L` will apply all
scripts without regard to the API level.

Each script is executed in a seperate transaction. If a script fails, all
changes in that script will be rolled back and the script will stop with
an error message and a non-zero return status.

## JSON Output

When supplying the `--json` option, `dbupgrade` will information about the
applied scripts as JSON to the standard output. Sample output:

```json
{
  "success": true,
  "oldVersion": {
    "version": 123,
    "apiLevel": 15
  },
  "newVersion": {
    "version": 125,
    "apiLevel": 16
  },
  "appliedScripts": [
    {
      "filename": "0124-create-foo.sql",
      "version": 124,
      "apiLevel": 15
    },
    {
      "filename": "0125-delete-bar-sql",
      "version": 125,
      "apiLevel": 16
    }
  ],
  "failedScript": {
    "filename": "0126-change-stuff.sql",
    "version": 126,
    "apiLevel": 16
  }
}
```

`success` is `true` if all scripts were applied successfully or no scripts
were to be applied. In this case, the `failedScript` key is not defined.
The `appliedScripts` key is always defined. In case no scripts were applied,
it's an empty array.
