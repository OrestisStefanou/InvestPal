# Turso Cloud sync

Optional. Without `TURSO_SYNC_URL` InvestPal is exactly what it was: one local turso file, no sync engine, no network. With it set, that same file becomes a replica of a Turso Cloud database that you move up and down by hand.

Nothing here is automatic. There is no sync on startup, no sync on shutdown, no background timer. The database changes only when you run one of the commands below.

## Setup

Create the cloud database and a token:

```bash
turso db create investpal
turso db show investpal --url        # -> turso://investpal-<org>.turso.io
turso db tokens create investpal
```

Put them in `.env`:

```bash
TURSO_SYNC_URL=turso://investpal-<org>.turso.io
TURSO_SYNC_AUTH_TOKEN=<token>
TURSO_SYNC_CLIENT_NAME=laptop
```

`turso://`, `libsql://` and `https://` are all accepted; the URL is normalised in `config.py`.

`TURSO_SYNC_CLIENT_NAME` must be different on every device. The cloud database records the last change each client pushed, keyed by that name, so two devices claiming to be the same client lose each other's work. Unset, it defaults to `investpal-<hostname>`, which is usually distinct already but is worth setting explicitly.

## Commands

| Command | What it does |
|---|---|
| `make turso_status` | Where this machine stands and what to run next. No network. |
| `make turso_first_push` | Seed an empty cloud database from an existing local one. |
| `make turso_first_pull` | Create the local database by downloading the cloud one. |
| `make turso_push` | Send local changes up, then checkpoint. |
| `make turso_pull` | Apply cloud changes locally, then checkpoint. |
| `make turso_verify` | Download the cloud database into a scratch copy and compare row counts. |

Each is a subcommand of `scripts/turso_sync.py`, so `uv run python3 -m scripts.turso_sync pull --push-first` and friends work for the flags the Makefile does not pass. Every command takes `--db-path` (defaults to `TURSO_DB_PATH`) and `--yes` to skip the confirmation.

## The four states

Which commands are allowed depends only on which files exist:

| `investpal.db` | `investpal.db-info` | State | Do this |
|---|---|---|---|
| absent | absent | fresh device | `make turso_first_pull` |
| present | absent | local database, never synced | `make turso_first_push` |
| present | present | synced | `make turso_push` / `make turso_pull` |
| absent | present | leftover metadata | move the sidecars aside, then `make turso_first_pull` |

Anything you run in the wrong state refuses and names the right command. `make turso_status` prints the state and the row counts without touching the network.

## Why the first push is a separate command

Change capture is per connection. The sync engine sets `PRAGMA unstable_capture_data_changes_conn 'full'` on the connections it owns, and every insert, update and delete on those connections lands in a local `turso_cdc` table that `push()` drains. Two things follow.

**Every connection becomes a sync connection.** `repos/db.py::connect` switches from `turso.connect()` to `turso.sync.connect()` whenever `TURSO_SYNC_URL` is set. A write through a plain connection would not appear in `turso_cdc` and would never be pushed, so there is no such thing as a read-only shortcut here. The cost is small: roughly 0.15 ms per repo call becomes 0.29 ms, measured over 100 `get_sessions()` calls.

**Rows that predate sync are invisible.** They were written before any sync connection existed, so they are not in `turso_cdc` and a plain `push()` would send nothing. `make turso_first_push` therefore does not push the file, it rebuilds it:

1. Copies `investpal.db` to `investpal.db.pre-sync-<timestamp>.bak` and leaves that copy alone forever.
2. Moves the original aside to `investpal.db.adopt-source-<timestamp>`.
3. Creates a fresh, empty sync database at `investpal.db` and applies `schema.sql` to it.
4. Copies every row of every table across, in an order that respects the one foreign key.
5. Checks the row counts match and that every embedding is still 1536 bytes.
6. Pushes and checkpoints.
7. Downloads the cloud database again and prints a local-vs-remote count table.

If anything fails between steps 3 and 6 it deletes the half-built file, moves the original back, and re-raises. The `.bak` survives even a failed rollback. Neither the `.bak` nor the `.adopt-source-` copy is deleted automatically; remove them yourself once the count table looks right.

The first push refuses to run against a cloud database that already holds rows, since seeding into existing data would collide with it. Create a fresh one, or pass `--allow-nonempty-remote` if you know what you are doing.

## Conflicts

Last push wins. Both devices can write offline; whichever pushes last decides what the row looks like in the cloud.

`pull()` is rollback-and-replay: local changes that have not been pushed are rolled back, the cloud changes are applied, then the local changes are replayed on top. It is atomic, so a failure leaves the database as it was. Push before you pull when the local machine has newer work, or use `--push-first`.

## Running it safely

The REST API and the MCP server both hold the same file.

- `status` and `verify` are read-only. Safe any time.
- `push` drains change rows and advances a watermark. Rows written while it runs are simply picked up by the next push. The servers can stay up.
- `pull`, `first-push` and `first-pull` rewrite WAL frames underneath whatever connections exist. **Stop both servers first.** Each asks for confirmation.

Sync commands are also serialised against each other by a lock file (`investpal.db.sync.lock`), so two of them cannot overlap.

## Checkpoints and the WAL

Auto-checkpoint is disabled for sync databases and nothing in the app calls `checkpoint()`, so `investpal.db-wal` only ever grows between sync commands. `push` and `pull` both checkpoint when they finish, which is the only thing that shrinks it. If you enable sync and then never push, expect the WAL to keep growing; `make turso_status` prints its size.

## Files

Next to `investpal.db` the sync engine keeps:

| File | Purpose |
|---|---|
| `investpal.db-info` | Sync metadata. Its presence is what marks the file as a sync database. |
| `investpal.db-changes` | The change-data-capture file. |
| `investpal.db-wal` | The usual write-ahead log. |
| `investpal.db-wal-revert` | Used for the rollback half of a pull. |

Treat them as one unit. Deleting `-info` on its own makes the engine think the database has never synced, and the next connection with bootstrapping enabled would overwrite your local data with the cloud copy.

## Recovery

**A first push that went wrong.** The `.pre-sync-<timestamp>.bak` file is the database exactly as it was. Stop the servers, delete `investpal.db` and its four sidecars, copy the `.bak` back into place, and you are where you started.

**The cloud database came back empty.** If the count table after a first push shows tables missing remotely, the schema did not travel with the push. Create the tables in the cloud out of band by running `schema.sql` against it, restore from the `.bak`, and re-run with `--allow-nonempty-remote`.

**Sync was switched off and writes happened.** Anything written while `TURSO_SYNC_URL` was unset went through a plain connection, is not in `turso_cdc`, and can never be pushed. `make turso_status` warns when it sees a sync database with the URL unset. The only clean fix is a fresh cloud database and another `make turso_first_push`.

**Embeddings look wrong after a first push.** They are derived data. `make backfill_embeddings` rebuilds them.

## Rehearsing without a Turso account

`tursodb` serves the same sync protocol locally, so the whole thing can be exercised offline.

```bash
tursodb ./server.db --sync-server 127.0.0.1:8099
```

Then, against a copy rather than your real database:

```bash
cp investpal.db /tmp/testa.db
export TURSO_SYNC_URL=http://127.0.0.1:8099

TURSO_SYNC_CLIENT_NAME=device-a uv run python3 -m scripts.turso_sync status     --db-path /tmp/testa.db
TURSO_SYNC_CLIENT_NAME=device-a uv run python3 -m scripts.turso_sync first-push --db-path /tmp/testa.db

# a second device from the same checkout
TURSO_SYNC_CLIENT_NAME=device-b uv run python3 -m scripts.turso_sync first-pull --db-path /tmp/deviceb.db

# write on B through the app, push it, pull it on A
TURSO_SYNC_CLIENT_NAME=device-b TURSO_DB_PATH=/tmp/deviceb.db uv run python -c "
from repos.sessions import SessionsTable
SessionsTable().create_session('s-from-b', 'written on device b')"
TURSO_SYNC_CLIENT_NAME=device-b uv run python3 -m scripts.turso_sync push --db-path /tmp/deviceb.db
TURSO_SYNC_CLIENT_NAME=device-a uv run python3 -m scripts.turso_sync pull --db-path /tmp/testa.db
```

A good last check is `SELECT COUNT(*), MIN(length(embedding)), MAX(length(embedding)) FROM user_conversation_note_embeddings`: min and max must both be 1536, and `searchUserConversationNotes` must still return results.
