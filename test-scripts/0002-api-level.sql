-- Schema: dbupgrade
-- Dialect: sqlite
-- Version: 2
-- API-Level: 1

ALTER TABLE test ADD COLUMN foo VARCHAR(100) NOT NULL DEFAULT '';
