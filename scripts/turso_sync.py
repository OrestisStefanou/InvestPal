"""Move the local investpal database to and from a Turso Cloud database.

Cloud sync is off until TURSO_SYNC_URL is set, and it never runs on its own:
nothing here happens except when one of these is invoked.

    make turso_status       what state is this machine in, and what comes next
    make turso_first_push   seed an empty cloud database from this local file
    make turso_first_pull   create the local database by downloading the cloud one
    make turso_push         send local changes to the cloud
    make turso_pull         apply cloud changes locally
    make turso_verify       download the cloud database and compare row counts

Stop `make run_investpal` and `make run_investpal_mcp` before running anything
other than status, verify and push: the other commands rewrite WAL frames under
any connection the servers are holding.
"""

import argparse
import fcntl
import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from urllib.parse import urlparse

import turso

from config import settings
from repos.db import open_sync, sync_metadata_path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Copy order respects the one foreign key in schema.sql
# (user_conversation_note_embeddings.note_id -> user_conversation_notes.id).
APP_TABLES = [
    "user_profile_notes",
    "user_conversation_notes",
    "user_conversation_note_embeddings",
    "agent_reminders",
    "agent_workflows",
    "workflow_results",
    "sessions",
    "session_messages",
]

COPY_BATCH = 500

# 384 float32s: repos.embeddings.EMBEDDING_DIMENSIONS against schema.sql's F32_BLOB(384).
EMBEDDING_BLOB_BYTES = 384 * 4

# Everything that can sit next to the main file: the four the sync engine keeps,
# plus the -shm index any WAL reader builds. -shm is here so that moving or
# removing a database set leaves nothing of the old one behind for the new file
# to inherit.
SIDECAR_SUFFIXES = ("-info", "-changes", "-wal", "-wal-revert", "-shm")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def schema_sql() -> str:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql"
    )
    with open(path, "r") as f:
        return f.read()


def require_enabled() -> None:
    if not settings.turso_cloud_enabled:
        raise SystemExit(
            "TURSO_SYNC_URL is not set, so cloud sync is disabled and there is "
            "nothing to sync with. Set it in .env to enable it."
        )


def remote_host() -> str:
    """The remote, safe to print. The auth token never goes near a log line."""
    return urlparse(settings.turso_sync_url or "").netloc or "?"


def db_state(db_path: str) -> str:
    """Which of the four situations this machine is in. Decided purely from files."""
    db = os.path.exists(db_path)
    meta = os.path.exists(sync_metadata_path(db_path))
    if db and meta:
        return "synced"
    if db:
        return "local_only"
    if meta:
        return "broken"
    return "fresh"


STATE_HELP = {
    "fresh": "no local database yet -> run `make turso_first_pull`",
    "local_only": (
        "local database that has never been synced. Seed the cloud from it with "
        "`make turso_first_push`, or discard it and take the cloud copy with "
        "`make turso_first_pull FORCE=1` (which moves it aside rather than "
        "deleting it). The servers refuse to start until one of those has run"
    ),
    "synced": "synced database -> use `make turso_push` / `make turso_pull`",
    "broken": (
        "sync metadata without a database file -> run `make turso_first_pull`, "
        "which moves the leftover sidecars aside for you"
    ),
}


def require_state(db_path: str, expected: str) -> None:
    state = db_state(db_path)
    if state != expected:
        raise SystemExit(f"{db_path}: {STATE_HELP[state]}")


def confirm(message: str, assume_yes: bool) -> None:
    print(message)
    if assume_yes:
        print("--yes given, continuing.")
        return
    if not sys.stdin.isatty():
        raise SystemExit("Not a terminal and --yes was not given; refusing.")
    if input("Type 'yes' to continue: ").strip().lower() != "yes":
        raise SystemExit("Aborted.")


@contextmanager
def sync_lock(db_path: str):
    """Serialise sync commands against each other. Does not stop the servers."""
    lock_path = f"{db_path}.sync.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit(
                f"Another sync command holds {lock_path}. Wait for it to finish."
            )
        yield
    finally:
        os.close(fd)


@contextmanager
def read_only(db_path: str):
    """A plain connection for inspecting a file, closed on the way out.

    Not repos.db.connect: that routes through the sync engine whenever
    TURSO_SYNC_URL is set, which is exactly wrong for looking at a file that is
    not a sync database yet. turso's own context manager commits but does not
    close, hence the explicit close here.
    """
    conn = turso.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def table_counts(conn) -> dict[str, int | None]:
    """Row count per app table. None means the table is not there at all."""
    counts: dict[str, int | None] = {}
    for table in APP_TABLES:
        try:
            rows = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchall()
            counts[table] = rows[0][0]
        except Exception:
            counts[table] = None
    return counts


def print_counts(title: str, counts: dict[str, int | None]) -> None:
    print(f"\n{title}")
    for table, count in counts.items():
        print(f"  {table:38} {'missing' if count is None else count}")


def compare_counts(
    local: dict[str, int | None], remote: dict[str, int | None]
) -> bool:
    """Print a local vs remote table and say whether every row matched."""
    print(f"\n{'table':38} {'local':>8} {'remote':>8}")
    matched = True
    for table in APP_TABLES:
        lhs, rhs = local.get(table), remote.get(table)
        flag = "" if lhs == rhs else "   MISMATCH"
        if lhs != rhs:
            matched = False
        print(
            f"  {table:36} {('-' if lhs is None else lhs):>8} "
            f"{('-' if rhs is None else rhs):>8}{flag}"
        )
    return matched


def log_stats(conn, label: str) -> None:
    s = conn.stats()
    logger.info(
        "%s: revision=%s cdc_operations=%s main_wal=%sB revert_wal=%sB "
        "sent=%sB received=%s last_push=%s last_pull=%s",
        label,
        s.revision,
        s.cdc_operations,
        s.main_wal_size,
        s.revert_wal_size,
        s.network_sent_bytes,
        s.network_received_bytes,
        s.last_push_unix_time,
        s.last_pull_unix_time,
    )


def fetch_remote_counts(keep: bool = False) -> dict[str, int | None]:
    """Download the cloud database into a scratch copy and count its rows.

    Bootstrapping a throwaway file is the whole remote-inspection story: no HTTP
    client, no second driver. It pulls the entire database every time, which is
    nothing at this size but is not a habit to carry to a large one.
    """
    tmpdir = tempfile.mkdtemp(prefix="investpal-turso-verify-")
    path = os.path.join(tmpdir, "verify.db")
    logger.info("Downloading the cloud database from %s for inspection", remote_host())
    try:
        conn = open_sync(path, bootstrap_if_empty=True)
        try:
            return table_counts(conn)
        finally:
            conn.close()
    finally:
        if keep:
            logger.info("Scratch copy kept at %s", path)
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def move_with_wal(src: str, dst: str) -> None:
    os.rename(src, dst)
    if os.path.exists(f"{src}-wal"):
        os.rename(f"{src}-wal", f"{dst}-wal")


def move_db_set(src: str, dst: str) -> list[str]:
    """Move a database and every sidecar it happens to have, keeping all of them.

    Its own inverse: pass the two paths the other way round to undo it.
    """
    moved = []
    for suffix in ("", *SIDECAR_SUFFIXES):
        if os.path.exists(f"{src}{suffix}"):
            os.rename(f"{src}{suffix}", f"{dst}{suffix}")
            moved.append(os.path.basename(f"{src}{suffix}"))
    return moved


def set_aside(db_path: str) -> str:
    """Move the whole database set out of the way and return where it went.

    Nothing here deletes: the point is that a command needing the path free can
    take it without the client having to `rm` anything by hand.
    """
    dst = f"{db_path}.replaced-{timestamp()}"
    moved = move_db_set(db_path, dst)
    logger.info("Moved %s aside to %s*", ", ".join(moved), os.path.basename(dst))
    return dst


def is_empty(db_path: str) -> bool:
    """True when the file holds no application rows at all.

    A database the servers created on first start and nobody has written to is
    worth nothing, but is indistinguishable from a populated one by file
    existence — which is what db_state() decides on. Without this, a plain
    `make setup` followed by turning sync on left first-pull permanently
    unreachable, with a manual `rm` as the only way out.
    """
    with read_only(db_path) as conn:
        return not any(count for count in table_counts(conn).values())


def remove_db_files(db_path: str) -> None:
    for path in (db_path, *(f"{db_path}{s}" for s in SIDECAR_SUFFIXES)):
        if os.path.exists(path):
            os.remove(path)


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #


def cmd_status(args) -> None:
    db_path = args.db_path
    state = db_state(db_path)

    print(f"local database   {db_path}")
    print(f"cloud sync       {'enabled' if settings.turso_cloud_enabled else 'disabled'}")
    if settings.turso_cloud_enabled:
        print(f"remote           {remote_host()}")
        print(f"client name      {settings.turso_sync_client_name}")
        print(f"state            {STATE_HELP[state]}")
    else:
        print("state            local only. Set TURSO_SYNC_URL in .env to sync.")

    print("\nfiles")
    for path in (db_path, *(f"{db_path}{s}" for s in SIDECAR_SUFFIXES)):
        exists = os.path.exists(path)
        size = f"{os.path.getsize(path)}B" if exists else "-"
        print(f"  {os.path.basename(path):32} {size}")

    if not settings.turso_cloud_enabled and state == "synced":
        print(
            "\nWARNING: this is a sync database but TURSO_SYNC_URL is unset. Writes "
            "made in this state bypass change capture and can never be pushed. Set "
            "the URL back before writing anything you want in the cloud."
        )

    if os.path.exists(db_path):
        with read_only(db_path) as conn:
            print_counts("local rows", table_counts(conn))
            for table, label in (
                ("turso_cdc", "captured change rows"),
                ("turso_sync_last_change_id", "last pushed change per client"),
            ):
                try:
                    rows = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchall()
                    print(f"\n{label}: {rows[0][0]}")
                except Exception:
                    pass

    if args.remote:
        require_enabled()
        if state != "synced":
            raise SystemExit(f"{db_path}: {STATE_HELP[state]}")
        with read_only(db_path) as conn:
            local = table_counts(conn)
        compare_counts(local, fetch_remote_counts())


def cmd_verify(args) -> None:
    require_enabled()
    remote = fetch_remote_counts(keep=args.keep)
    if os.path.exists(args.db_path):
        with read_only(args.db_path) as conn:
            local = table_counts(conn)
        matched = compare_counts(local, remote)
        print("\nlocal and remote agree." if matched else "\nlocal and remote DIFFER.")
    else:
        print_counts("remote rows", remote)


def cmd_first_push(args) -> None:
    """Case 1: an existing populated local database, an empty cloud database.

    A plain push() would send nothing here. Change capture is per-connection and
    the rows in the file predate any sync connection, so none of them are in
    turso_cdc. They have to be replayed through a sync connection to exist as far
    as the cloud is concerned, which is what the copy below does.
    """
    require_enabled()
    db_path = args.db_path
    require_state(db_path, "local_only")

    with read_only(db_path) as conn:
        found = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_schema WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'turso_%'"
            ).fetchall()
        }
        local_counts = table_counts(conn)

    unknown = found - set(APP_TABLES)
    if unknown:
        raise SystemExit(
            f"{db_path} holds tables this script does not know how to copy: "
            f"{sorted(unknown)}. Add them to APP_TABLES in scripts/turso_sync.py "
            "(in foreign-key-safe order) and re-run."
        )

    if not args.skip_remote_check:
        remote = fetch_remote_counts()
        populated = {t: c for t, c in remote.items() if c}
        if populated and not args.allow_nonempty_remote:
            raise SystemExit(
                f"The cloud database at {remote_host()} already holds rows "
                f"({populated}). Seeding it from this file would collide with them. "
                "Create a fresh cloud database, or pass --allow-nonempty-remote if "
                "you are certain."
            )

    confirm(
        f"\nAbout to seed the cloud database at {remote_host()} from {db_path}.\n"
        f"  - {db_path} is backed up first and then rebuilt as a sync database\n"
        f"  - every row is copied into the rebuilt file and pushed\n"
        f"  - stop `make run_investpal` and `make run_investpal_mcp` first\n",
        args.yes,
    )

    ts = timestamp()
    backup = f"{db_path}.pre-sync-{ts}.bak"
    source = f"{db_path}.adopt-source-{ts}"

    shutil.copy2(db_path, backup)
    if os.path.exists(f"{db_path}-wal"):
        shutil.copy2(f"{db_path}-wal", f"{backup}-wal")
    logger.info("Backed up %s to %s", db_path, backup)

    move_with_wal(db_path, source)

    try:
        # No -info and no file at db_path, so this creates an empty sync database.
        # bootstrap_if_empty is False: there is nothing in the cloud to fetch and
        # nothing here that may be overwritten.
        dst = open_sync(db_path, bootstrap_if_empty=False)
        try:
            dst.executescript(schema_sql())
            dst.commit()
            logger.info("Applied schema.sql to the new sync database")

            src = turso.connect(source)
            try:
                for table in APP_TABLES:
                    columns = [
                        row[1]
                        for row in src.execute(f"PRAGMA table_info({table})").fetchall()
                    ]
                    if not columns:
                        logger.info("%s: not present in the source, skipped", table)
                        continue
                    insert = (
                        f"INSERT INTO {table} ({', '.join(columns)}) "
                        f"VALUES ({', '.join('?' * len(columns))})"
                    )
                    rows = src.execute(
                        f"SELECT {', '.join(columns)} FROM {table}"
                    ).fetchall()
                    for start in range(0, len(rows), COPY_BATCH):
                        dst.executemany(insert, rows[start : start + COPY_BATCH])
                        dst.commit()
                    logger.info("%s: copied %d row(s)", table, len(rows))
            finally:
                src.close()

            copied = table_counts(dst)
            if not compare_counts(local_counts, copied):
                raise RuntimeError("row counts changed during the copy")

            bad = dst.execute(
                "SELECT COUNT(*) FROM user_conversation_note_embeddings "
                f"WHERE length(embedding) != {EMBEDDING_BLOB_BYTES}"
            ).fetchall()[0][0]
            if bad:
                raise RuntimeError(
                    f"{bad} embedding(s) did not survive the copy at "
                    f"{EMBEDDING_BLOB_BYTES} bytes"
                )

            logger.info("Pushing to %s", remote_host())
            dst.push()
            dst.checkpoint()
            log_stats(dst, "after push")
        finally:
            dst.close()
    except Exception:
        logger.error("Seeding failed, restoring %s", db_path)
        remove_db_files(db_path)
        move_with_wal(source, db_path)
        logger.error("Restored. The backup at %s was never touched.", backup)
        raise

    print(f"\nBackup:       {backup}")
    print(f"Copy source:  {source}")
    print("Neither is deleted automatically. Remove them once you are satisfied.")

    if not args.skip_remote_check:
        if compare_counts(local_counts, fetch_remote_counts()):
            print("\nDone: the cloud database matches this one.")
        else:
            print(
                "\nFAILED: the cloud database does not match. Nothing local was lost "
                f"(this file and {backup} are both intact), but do not treat the "
                "cloud copy as good. If the remote came back with no tables at all, "
                "the schema did not travel with the push: create it in the cloud out "
                "of band and re-run with --allow-nonempty-remote."
            )


def cmd_first_pull(args) -> None:
    """Case 2: a device pulling the cloud database down for the first time.

    Not only a device with nothing local. The common way to arrive here is a
    machine that ran the servers once before sync was turned on and so has an
    empty file sitting in the way; that file is moved aside for you. One with
    rows in it is a real decision, so it needs --force, and is moved aside too.
    """
    require_enabled()
    db_path = args.db_path
    state = db_state(db_path)

    if state == "synced":
        raise SystemExit(f"{db_path}: {STATE_HELP[state]}")

    displaced = ""
    if state == "local_only":
        if is_empty(db_path):
            displaced = (
                f"  - {os.path.basename(db_path)} already exists but is empty; it is "
                "moved aside, not deleted\n"
            )
        elif args.force:
            displaced = (
                f"  - {os.path.basename(db_path)} HAS ROWS IN IT and is being "
                "replaced by the cloud copy. It is moved aside, not deleted\n"
            )
        else:
            with read_only(db_path) as conn:
                print_counts(f"rows in {db_path}", table_counts(conn))
            raise SystemExit(f"\n{db_path}: {STATE_HELP['local_only']}")
    elif state == "broken":
        displaced = (
            "  - the sidecars left behind by an earlier database are moved aside "
            "first\n"
        )

    confirm(
        f"\nAbout to create {db_path} by downloading the cloud database at "
        f"{remote_host()}.\n{displaced}"
        "  - stop `make run_investpal` and `make run_investpal_mcp` first\n",
        args.yes,
    )

    aside = set_aside(db_path) if state != "fresh" else None

    try:
        conn = open_sync(db_path, bootstrap_if_empty=True)
        try:
            # Covers a cloud database created before a table was added to schema.sql.
            conn.executescript(schema_sql())
            conn.commit()
            conn.checkpoint()
            log_stats(conn, "after bootstrap")
            print_counts(f"rows now in {db_path}", table_counts(conn))
        finally:
            conn.close()
    except Exception:
        if aside:
            logger.error("Download failed, putting the previous files back")
            remove_db_files(db_path)
            move_db_set(aside, db_path)
            logger.error("Restored %s as it was.", db_path)
        raise

    print(
        f"\n{db_path} is ready. Keep TURSO_SYNC_CLIENT_NAME distinct from your other "
        f"devices (currently {settings.turso_sync_client_name})."
    )
    if aside:
        print(f"Previous files: {aside}*  (not deleted; remove them when satisfied)")


def cmd_push(args) -> None:
    """Case 3."""
    require_enabled()
    require_state(args.db_path, "synced")

    logger.info(
        "Pushing %s to %s as %s",
        args.db_path,
        remote_host(),
        settings.turso_sync_client_name,
    )
    print(
        "The servers can stay up for a push: rows written while it runs are simply "
        "picked up by the next one."
    )

    conn = open_sync(args.db_path, bootstrap_if_empty=False)
    try:
        log_stats(conn, "before push")
        conn.push()
        # Not optional. Auto-checkpoint is off for sync databases and nothing else
        # in the app ever checkpoints, so the WAL only shrinks here.
        conn.checkpoint()
        log_stats(conn, "after push")
    finally:
        conn.close()
    print("Pushed.")


def cmd_pull(args) -> None:
    """Case 4."""
    require_enabled()
    require_state(args.db_path, "synced")

    confirm(
        f"\nAbout to pull {remote_host()} into {args.db_path}.\n"
        "  - local changes that have not been pushed are rolled back, the cloud "
        "changes are applied, then the local ones are replayed on top\n"
        "  - where both sides changed the same row, the last push wins\n"
        "  - push first (or pass --push-first) if this machine has newer work\n"
        "  - stop `make run_investpal` and `make run_investpal_mcp` first\n",
        args.yes,
    )

    conn = open_sync(args.db_path, bootstrap_if_empty=False)
    try:
        log_stats(conn, "before pull")
        if args.push_first:
            conn.push()
            logger.info("Pushed local changes before pulling")
        changed = conn.pull()
        conn.checkpoint()
        log_stats(conn, "after pull")
        print_counts(f"rows now in {args.db_path}", table_counts(conn))
    finally:
        conn.close()
    print("\nPulled new changes." if changed else "\nAlready up to date.")


# --------------------------------------------------------------------------- #
# entrypoint
# --------------------------------------------------------------------------- #


LOCKED_COMMANDS = {"first-push", "first-pull", "push", "pull"}


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db-path", default=settings.TURSO_DB_PATH)
    common.add_argument(
        "--yes", action="store_true", help="skip the interactive confirmation"
    )

    parser = argparse.ArgumentParser(
        prog="turso_sync",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser(
        "status", parents=[common], help="show the local sync state (no network)"
    )
    status.add_argument(
        "--remote", action="store_true", help="also compare against the cloud database"
    )
    status.set_defaults(func=cmd_status)

    verify = sub.add_parser(
        "verify", parents=[common], help="download the cloud database and compare rows"
    )
    verify.add_argument(
        "--keep", action="store_true", help="keep the downloaded scratch copy"
    )
    verify.set_defaults(func=cmd_verify)

    first_push = sub.add_parser(
        "first-push", parents=[common], help="seed an empty cloud database from this file"
    )
    first_push.add_argument("--allow-nonempty-remote", action="store_true")
    first_push.add_argument(
        "--skip-remote-check",
        action="store_true",
        help="do not download the cloud database before and after seeding",
    )
    first_push.set_defaults(func=cmd_first_push)

    first_pull = sub.add_parser(
        "first-pull", parents=[common], help="create the local database from the cloud one"
    )
    first_pull.add_argument(
        "--force",
        action="store_true",
        help="replace a local database that has rows in it (moved aside, not deleted). "
        "An empty one is moved aside without this.",
    )
    first_pull.set_defaults(func=cmd_first_pull)

    push = sub.add_parser("push", parents=[common], help="push local changes")
    push.set_defaults(func=cmd_push)

    pull = sub.add_parser("pull", parents=[common], help="apply cloud changes locally")
    pull.add_argument(
        "--push-first", action="store_true", help="push local changes before pulling"
    )
    pull.set_defaults(func=cmd_pull)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command in LOCKED_COMMANDS:
        with sync_lock(args.db_path):
            args.func(args)
    else:
        args.func(args)


if __name__ == "__main__":
    main()
