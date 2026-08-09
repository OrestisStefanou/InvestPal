import os
from contextlib import contextmanager

import turso
import turso.sync

from config import settings


class TursoSyncNotInitialized(RuntimeError):
    """Cloud sync is switched on but the local file is not a sync database yet."""


def sync_metadata_path(db_path: str = settings.TURSO_DB_PATH) -> str:
    """The sidecar whose existence marks a file as a sync database."""
    return f"{db_path}-info"


def open_sync(db_path: str = settings.TURSO_DB_PATH, *, bootstrap_if_empty: bool = False):
    """Open a raw sync connection. Only this module and scripts/turso_sync.py call it.

    `bootstrap_if_empty=True` downloads the remote over the local file, truncating
    whatever was there. "Empty" means "no -info sidecar", not "no rows", so it is
    only ever passed by an explicit CLI subcommand that has already checked.
    """
    return turso.sync.connect(
        db_path,
        settings.turso_sync_url,
        auth_token=settings.TURSO_SYNC_AUTH_TOKEN,
        client_name=settings.turso_sync_client_name,
        bootstrap_if_empty=bootstrap_if_empty,
    )


def _open(db_path: str):
    """Pick the connection kind. Every read and write in the process comes through here.

    Change capture is per-connection: the sync engine sets
    `PRAGMA unstable_capture_data_changes_conn 'full'` on the connections it owns and
    push() drains the resulting `turso_cdc` table. A write made through a plain
    turso.connect() is invisible to that table and would never reach the cloud, so
    with sync on there is no such thing as a shortcut connection - all of them sync.
    """
    if not settings.turso_cloud_enabled:
        return turso.connect(db_path)

    if not os.path.exists(sync_metadata_path(db_path)):
        raise TursoSyncNotInitialized(
            f"TURSO_SYNC_URL is set but {db_path} is not a sync database "
            f"({sync_metadata_path(db_path)} is missing). Writes made now would never "
            "be pushed. Run `make turso_first_push` to seed the cloud database from "
            "this file, or `make turso_first_pull` on a device that has no local "
            "database yet. Run `make turso_status` to see the current state."
        )

    return open_sync(db_path, bootstrap_if_empty=False)


@contextmanager
def connect(db_path: str = settings.TURSO_DB_PATH):
    """Open a connection that commits on success, rolls back on error, always closes.

    turso's own `with turso.connect(...)` is a transaction manager, not a closer: it
    commits or rolls back on exit but leaves the connection open, so the connection
    and the lock it holds are only released when the object is garbage collected.
    Every repo goes through this instead.

    With TURSO_SYNC_URL set this hands back a sync connection instead of a plain one
    (see `_open`). ConnectionSync subclasses the ordinary connection, so the commit /
    rollback / close contract and the `first_row` workaround below are unchanged.
    """
    conn = _open(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def connection(db_path: str = settings.TURSO_DB_PATH, existing=None):
    """Join a caller's open transaction, or own a fresh one.

    Lets a repo method be called either standalone or as one step of a larger
    transaction spanning several tables. When `existing` is passed the caller
    owns the commit, so the connection is yielded untouched; otherwise this
    behaves exactly like `connect`.

    Forgetting to thread `existing` through fails loudly rather than silently
    splitting the work in two: opening a second connection while the first
    holds the write lock raises "database is locked".
    """
    if existing is not None:
        yield existing
        return

    with connect(db_path) as conn:
        yield conn


def first_row(cursor):
    """Read a single row from a RETURNING statement, or None.

    Must drain with fetchall rather than fetchone: turso leaves an
    `UPDATE ... RETURNING` statement un-finalized after fetchone, and the next
    commit on that connection then fails with "database is locked".
    """
    rows = cursor.fetchall()
    return rows[0] if rows else None


def init_db(db_path: str = settings.TURSO_DB_PATH):
    """Apply schema.sql. Called from every entrypoint's startup.

    With cloud sync on this doubles as the startup gate: `connect` raises
    TursoSyncNotInitialized before the file is touched, so a server cannot come up
    against a database whose writes would never be pushed. Once the tables exist the
    CREATE TABLE IF NOT EXISTS script is a no-op that changes no schema and produces
    no CDC rows, so nothing is pushed on every boot.
    """
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql"
    )
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        with connect(db_path) as conn:
            conn.executescript(schema_sql)
