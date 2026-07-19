import os
import turso
from config import settings

def init_db(db_path: str = settings.TURSO_DB_PATH):
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        with turso.connect(db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
