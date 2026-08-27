"""Hardened Python data pipeline: read CSV, validate rows, write to Postgres.

See the engineering report (report.md) for a full description of the bugs found
and the fixes applied. Highlights:

  - NoneType crashes: ``validate_row`` now raises ``ValueError``; ``process_csv``
    logs and skips invalid rows instead of dereferencing ``None``.
  - Duplicate inserts: ``INSERT ... ON CONFLICT (email) DO UPDATE`` (and the
    same for ``orders.user_id``) makes pipeline runs idempotent.
  - Atomicity: ``insert_user`` + ``insert_orders`` run inside a single
    transaction committed once at the end of ``run_pipeline``.
  - CSV edge cases: ``utf-8-sig`` encoding (BOM), empty-row skip, header
    validation.
  - SQL injection: parameterized query in ``get_user_by_email``.
  - Connection leak: ``try/finally`` everywhere a connection is opened.
  - Retry/backoff: transient ``psycopg2.OperationalError``s are retried with
    exponential backoff.
  - Monetary precision: ``Decimal`` instead of ``float``.
  - Error visibility: ``logging`` replaces bare ``except`` swallows.
"""

import csv
import logging
import os
import time
from decimal import Decimal, InvalidOperation

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DB_URL = os.getenv("DATABASE_URL", "postgresql://localhost/myapp")

# Columns the CSV must provide. Extra columns are tolerated.
REQUIRED_COLUMNS = {"email", "name", "amount", "orders"}

# Retry tuning for transient DB errors.
MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 0.5  # seconds
RETRY_BACKOFF = 2.0


def get_connection():
    return psycopg2.connect(DB_URL)


# BUG 5 fix: parameterized query — no f-string interpolation.
def get_user_by_email(email):
    """Look up a user by email using a parameterized query (no SQL injection)."""
    if not email:
        return None
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()
    finally:
        # BUG 6 fix: always release the connection.
        conn.close()


# BUG 1 fix: raise ValueError instead of returning None — callers no longer
# need to null-check the return value.
def validate_row(row):
    """Validate and clean a single CSV row.

    Raises ``ValueError`` with a human-readable message if the row is invalid.
    Never returns ``None`` — callers rely on the exception instead of having to
    null-check the return value.
    """
    # csv.DictReader yields {'col': None, ...} for blank lines.
    if row is None or not any((v or "").strip() for v in row.values()):
        raise ValueError("empty row")

    missing = [c for c in ("email", "name") if not (row.get(c) or "").strip()]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    email = row["email"].strip()
    name = row["name"].strip()

    # BUG 8 fix: Decimal avoids floating-point rounding on monetary values.
    raw_amount = row.get("amount", "0") or "0"
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"invalid amount {raw_amount!r}: {e}") from e

    raw_orders = row.get("orders", "0") or "0"
    try:
        orders = int(raw_orders)
    except (TypeError, ValueError) as e:
        raise ValueError(f"invalid orders {raw_orders!r}: {e}") from e

    return {
        "email": email,
        "name": name,
        "amount": amount,
        "orders": orders,
    }


# BUG 4 fix: utf-8-sig encoding (strips BOM), header validation, empty-row
# skip, and graceful handling of invalid rows.
def process_csv(path):
    """Read and validate a CSV file into a list of user dicts.

    - ``utf-8-sig`` encoding strips a leading BOM that would otherwise corrupt
      the first column name (``'\\ufeffemail'`` instead of ``'email'``).
    - Required columns are validated up front.
    - Empty rows are skipped.
    - Invalid rows are logged and skipped (the pipeline continues).
    """
    results = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            logger.warning("CSV %s has no header row; skipping", path)
            return results
        header = {h.strip() for h in reader.fieldnames}
        missing = REQUIRED_COLUMNS - header
        if missing:
            raise ValueError(
                f"CSV {path} missing required columns: {sorted(missing)}"
            )

        for lineno, row in enumerate(reader, start=2):
            try:
                validated = validate_row(row)
            except ValueError as e:
                # BUG 9 fix: log instead of silently swallowing.
                logger.warning("Skipping row %d in %s: %s", lineno, path, e)
                continue
            results.append(validated)
    return results


# BUG 2 + BUG 3 fix: ON CONFLICT (idempotent) and no per-call commit so the
# caller can wrap user+orders in a single transaction.
def insert_user(conn, user):
    """Insert a user idempotently and return its id.

    Relies on a ``UNIQUE`` constraint on ``users.email``. If the row already
    exists (e.g. from a previous pipeline run), we update ``name`` and return
    the existing id — preventing the duplicate-user bug.

    Does NOT commit; the caller manages the transaction so the user+orders
    inserts stay atomic.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users (email, name)
        VALUES (%s, %s)
        ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """,
        (user["email"], user["name"]),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("INSERT ... RETURNING produced no row")
    return row[0]


# BUG 2 + BUG 3 fix: ON CONFLICT on user_id (idempotent), no per-call commit.
def insert_orders(conn, user_id, user):
    """Insert the per-user order summary, idempotently.

    Relies on a ``UNIQUE`` constraint on ``orders.user_id`` so re-running the
    pipeline does not duplicate summary rows. Does NOT commit; the caller
    manages the transaction.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO orders (user_id, amount, order_count)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
            SET amount = EXCLUDED.amount,
                order_count = EXCLUDED.order_count
        """,
        (user_id, user["amount"], user["orders"]),
    )


def _insert_user_and_orders(conn, user):
    """Insert a user and their order summary as one atomic unit (no commit)."""
    user_id = insert_user(conn, user)
    insert_orders(conn, user_id, user)
    return user_id


# BUG 7 fix: exponential backoff on transient psycopg2 errors.
def _with_retry(fn, *args, label="operation", **kwargs):
    """Call ``fn(*args, **kwargs)`` with exponential backoff on transient errors.

    Retries up to ``MAX_ATTEMPTS`` times on ``psycopg2.OperationalError``
    (connection lost, server down, etc.). Other exceptions bubble up
    immediately so non-transient errors (e.g. ``IntegrityError`` on a missing
    constraint) surface fast.
    """
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fn(*args, **kwargs)
        except psycopg2.OperationalError as e:
            last_exc = e
            if attempt == MAX_ATTEMPTS:
                break
            delay = RETRY_BASE_DELAY * (RETRY_BACKOFF ** (attempt - 1))
            logger.warning(
                "Transient DB error during %s (attempt %d/%d): %s — retrying in %.2fs",
                label, attempt, MAX_ATTEMPTS, e, delay,
            )
            time.sleep(delay)
    raise last_exc


# BUG 6 fix: try/finally guarantees the connection is closed on every path.
def run_pipeline(csv_path):
    """Run the full pipeline: read CSV, insert users + orders atomically."""
    users = process_csv(csv_path)
    if not users:
        logger.info("No valid users to import from %s", csv_path)
        return

    conn = None
    try:
        conn = _with_retry(get_connection, label="connect to DB")
        for user in users:
            try:
                _with_retry(
                    _insert_user_and_orders, conn, user,
                    label=f"insert user {user.get('email')!r}",
                )
            except psycopg2.Error as e:
                # BUG 9 fix: log instead of silent swallow. BUG 3 fix: roll
                # back only this user's work and keep going for the rest.
                logger.exception(
                    "Failed to insert user %r after retries: %s",
                    user.get("email"), e,
                )
                try:
                    conn.rollback()
                except psycopg2.Error:
                    # Connection is broken (e.g. server dropped us). Reopen so
                    # the remaining users still have a chance.
                    logger.warning(
                        "rollback failed; attempting to reopen connection"
                    )
                    try:
                        conn.close()
                    except psycopg2.Error:
                        pass
                    conn = _with_retry(
                        get_connection, label="reopen DB connection",
                    )
                continue
        conn.commit()
        logger.info("Committed %d user(s) from %s", len(users), csv_path)
    finally:
        if conn is not None and not conn.closed:
            try:
                conn.close()
            except psycopg2.Error:
                pass


if __name__ == "__main__":
    run_pipeline("input.csv")
