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

CREATE INDEX IF NOT EXISTS idx_agent_workflows_due
    ON agent_workflows (status, next_run_at);

CREATE INDEX IF NOT EXISTS idx_session_messages_session
    ON session_messages (session_id, id);

CREATE INDEX IF NOT EXISTS idx_workflow_results_ran_at
    ON workflow_results (ran_at DESC);
