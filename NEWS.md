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
