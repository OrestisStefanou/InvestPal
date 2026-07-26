import os
from contextlib import contextmanager

import turso

from config import settings


@contextmanager
def connect(db_path: str = settings.TURSO_DB_PATH):
    """Open a connection that commits on success, rolls back on error, always closes.

    turso's own `with turso.connect(...)` is a transaction manager, not a closer: it
    commits or rolls back on exit but leaves the connection open, so the connection
    and the lock it holds are only released when the object is garbage collected.
    Every repo goes through this instead.
    """
    conn = turso.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def first_row(cursor):
    """Read a single row from a RETURNING statement, or None.

    Must drain with fetchall rather than fetchone: turso leaves an
    `UPDATE ... RETURNING` statement un-finalized after fetchone, and the next
    commit on that connection then fails with "database is locked".
    """
    rows = cursor.fetchall()
    return rows[0] if rows else None


def init_db(db_path: str = settings.TURSO_DB_PATH):
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql"
    )
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        with connect(db_path) as conn:
            conn.executescript(schema_sql)
