CREATE TABLE IF NOT EXISTS user_profile_notes (
    id TEXT PRIMARY KEY,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL,
    outdated INTEGER NOT NULL DEFAULT 0
);
