CREATE TABLE IF NOT EXISTS user_profile_notes (
    id TEXT PRIMARY KEY,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL,
    outdated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_conversation_notes (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Vector embeddings for semantic search over user_conversation_notes.
-- Kept in a sidecar table rather than as a column on user_conversation_notes:
-- init_db only ever runs CREATE TABLE IF NOT EXISTS, so a new column would
-- never reach an already-created investpal.db. It also makes re-embedding
-- under a different model a table-level operation.
-- The dimension matches repos.embeddings.EMBEDDING_DIMENSIONS; changing the
-- model means changing both and re-running the backfill.
CREATE TABLE IF NOT EXISTS user_conversation_note_embeddings (
    note_id TEXT PRIMARY KEY,
    embedding F32_BLOB(384) NOT NULL,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (note_id) REFERENCES user_conversation_notes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agent_reminders (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    due_date TEXT,
    created_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE TABLE IF NOT EXISTS agent_workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    schedule TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_run_at TEXT,
    next_run_at TEXT
);

CREATE TABLE IF NOT EXISTS workflow_results (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    workflow_name TEXT NOT NULL,
    output TEXT NOT NULL,
    ran_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- id is an INTEGER PRIMARY KEY so it is a rowid alias: it auto-assigns on insert
-- and ordering by it replays the conversation in the order messages arrived.
CREATE TABLE IF NOT EXISTS session_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT
);

-- What the client owns, whatever the origin. Holds positions no API can reach
-- (T-bills on a broker with no MCP server, bank cash, private equity) alongside
-- positions read from a connected broker, because an account may never be
-- connected and a connected one goes dark -- a portfolio review with the IB
-- gateway down still needs last-known share counts.
--
-- `source` and `as_of` are what make storing broker data safe rather than a
-- repeat of the free-text snapshot notes this table replaced: a row whose source
-- is a broker is a CACHE, refreshed from that broker whenever it is reachable and
-- quoted only with its as_of date when it is not. No prices, market values or
-- P&L live here; those are always fetched live.
--
-- One row per position per custodian: refreshing updates in place, it never
-- appends. Closing is the nullable closed_at soft delete, so an exited position
-- keeps its cost basis history.
CREATE TABLE IF NOT EXISTS holdings (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    ticker TEXT,
    quantity REAL,
    cost_basis REAL,
    amount REAL,
    currency TEXT,
    custodian TEXT,
    source TEXT NOT NULL,
    as_of TEXT NOT NULL,
    detail TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    closed_at TEXT
);

-- Why a name is interesting and what would make us act on it. Disjoint from
-- holdings and linked to it by ticker: holdings answers "what and how much",
-- this answers "why, and at what price would I act". A held name has a row in
-- both.
--
-- Keyed by ticker and updated in place on purpose. The free-text profile notes
-- this replaces were append-only, so every trigger reset spawned a new note and
-- retired the old one -- one name accumulated twenty rows, and a single
-- watchlist add was written three times in one day.
CREATE TABLE IF NOT EXISTS ticker_records (
    ticker TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    thesis TEXT,
    entry_trigger TEXT,
    falsifier TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_agent_workflows_due
    ON agent_workflows (status, next_run_at);

CREATE INDEX IF NOT EXISTS idx_holdings_open
    ON holdings (closed_at, custodian);

CREATE INDEX IF NOT EXISTS idx_ticker_records_status
    ON ticker_records (status);

CREATE INDEX IF NOT EXISTS idx_session_messages_session
    ON session_messages (session_id, id);

CREATE INDEX IF NOT EXISTS idx_workflow_results_ran_at
    ON workflow_results (ran_at DESC);
