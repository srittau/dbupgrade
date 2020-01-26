News in dbupgrade 2.1.0
=======================

Improvements
------------

News in dbupgrade 2.0.0
=======================

Incompatible Changes
--------------------

* Drop support for Python 3.5 and 3.6.
* Use sqlparse to split SQL statements. While this will provide greater
  SQL compatibility overall, it may be incompatible with some existing
  SQL files.

News in dbupgrade 1.0.0
=======================

Improvements
------------

* Add `--quiet` option.

News in dbupgrade 0.2.2
=======================

Improvements
------------

* Relax type requirements for the `stream` arguments of
  `parse_sql_stream()`, `split_sql()`, and `execute_stream()`.

Bug Fixes
---------

* Fix escaping of percent signs.

News in dbupgrade 0.2.1
=======================

* Python 3.5 compatibility.

News in dbupgrade 0.2.0
=======================

New Features
------------

* Add a new file header `Transaction` to disable transaction handling
  for this file.
