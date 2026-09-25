from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        return {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        conn.close()


def set_value(key: str, value: str):
    conn = connect()
    try:
        conn.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()
