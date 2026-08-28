-- ============================================================
-- 01_extensions.sql
-- Enables Postgres extensions required by schema.sql.
-- Must run before 002_schema.sql.
-- ============================================================

-- gen_random_uuid() for UUID primary keys (avoids leaking
-- sequential/guessable IDs once this is exposed via the API)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Case-insensitive text type, used for ticker symbols so
-- "aapl" and "AAPL" are treated as the same instrument
CREATE EXTENSION IF NOT EXISTS citext;
