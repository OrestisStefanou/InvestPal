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

CREATE TABLE IF NOT EXISTS agent_reminders (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    due_date TEXT,
    created_at TEXT NOT NULL,
    deleted_at TEXT
);
