-- Schema: dbupgrade
-- Dialect: sqlite
-- Version: 1
-- API-Level: 0

CREATE TABLE modulo(
    id INTEGER PRIMARY KEY,
    duration INTEGER NOT NULL,
    CHECK (duration % 5 = 0 AND duration > 0)
);
