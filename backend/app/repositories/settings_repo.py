from app.db import connect


def get_all() -> dict:
    conn = connect()
    try:
        return {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM settings").fetchall()}
    finally:
        conn.close()


def set_pairs(pairs: dict) -> None:
    conn = connect()
    try:
        conn.executemany(
            "INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)",
            [(str(k), str(v)) for k, v in pairs.items()],
        )
        conn.commit()
    finally:
        conn.close()
