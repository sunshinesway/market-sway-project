-- ============================================================
-- 02_schema.sql
-- Core schema for the Portfolio & Market Risk Tracker.
-- Safe to re-run: every statement uses IF NOT EXISTS.
--
-- Sections:
--   1. Reference data      (instruments)
--   2. Market data          (prices)               <- Stage 1, in progress now
--   3. Pipeline observability (ingestion_runs)
--   4. Portfolio structure  (portfolios, transactions)  <- Stage 2+
--   5. Computed metrics     (portfolio_metrics_daily)   <- Stage 3+
-- ============================================================

-- ------------------------------------------------------------
-- 1. Reference data
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instruments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol      CITEXT NOT NULL UNIQUE,          -- e.g. AAPL
    name        TEXT,                            -- e.g. Apple Inc.
    asset_class TEXT NOT NULL DEFAULT 'equity',   -- equity, etf, etc.
    currency    TEXT NOT NULL DEFAULT 'USD',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ------------------------------------------------------------
-- 2. Market data — what you're building right now
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prices (
    id             BIGSERIAL PRIMARY KEY,
    instrument_id  UUID NOT NULL REFERENCES instruments(id) ON DELETE CASCADE,
    price_date     DATE NOT NULL,
    open           NUMERIC(18,6),
    high           NUMERIC(18,6),
    low            NUMERIC(18,6),
    close          NUMERIC(18,6) NOT NULL,
    adjusted_close NUMERIC(18,6),
    volume         BIGINT,
    source         TEXT NOT NULL DEFAULT 'yfinance',
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Prevents duplicate rows if the ingestion job re-runs or
    -- re-pulls a date range — makes the job safely re-runnable.
    UNIQUE (instrument_id, price_date)
);

CREATE INDEX IF NOT EXISTS idx_prices_instrument_date
    ON prices (instrument_id, price_date DESC);

-- ------------------------------------------------------------
-- 3. Pipeline observability
-- Track each ingestion run: useful for debugging, and a good
-- talking point in interviews (shows you thought about reliability).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ingestion_runs (
    id            BIGSERIAL PRIMARY KEY,
    source        TEXT NOT NULL,
    started_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at   TIMESTAMPTZ,
    rows_ingested INTEGER,
    status        TEXT NOT NULL DEFAULT 'running',  -- running | success | failed
    error_message TEXT
);

-- ------------------------------------------------------------
-- 4. Portfolio structure — needed starting Stage 2
-- Defined now so the DB doesn't need a breaking migration later;
-- these tables just won't be populated until you get here.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolios (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    base_currency TEXT NOT NULL DEFAULT 'USD',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transactions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id  UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    instrument_id UUID NOT NULL REFERENCES instruments(id),
    txn_date      DATE NOT NULL,
    txn_type      TEXT NOT NULL CHECK (txn_type IN ('buy','sell','dividend','deposit','withdrawal')),
    quantity      NUMERIC(18,6),
    price         NUMERIC(18,6),
    amount        NUMERIC(18,6),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_transactions_portfolio_date
    ON transactions (portfolio_id, txn_date);

-- ------------------------------------------------------------
-- 5. Computed metrics — populated by the transform layer, Stage 3
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS portfolio_metrics_daily (
    id                BIGSERIAL PRIMARY KEY,
    portfolio_id      UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    metric_date       DATE NOT NULL,
    total_value       NUMERIC(18,6),
    daily_return      NUMERIC(12,8),
    cumulative_return NUMERIC(12,8),
    volatility_30d    NUMERIC(12,8),
    sharpe_ratio_30d  NUMERIC(12,8),
    max_drawdown      NUMERIC(12,8),
    computed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (portfolio_id, metric_date)
);
