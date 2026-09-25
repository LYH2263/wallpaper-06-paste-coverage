from app.db import connect
from app.engines.paste_math import net_area_m2


def _with_net_area(wall: dict) -> dict:
    wall["net_area_m2"] = net_area_m2(
        wall["perimeter"], wall["height"], wall.get("door_area_m2") or 0.0
    )
    return wall


def list_walls():
    conn = connect()
    try:
        return [_with_net_area(dict(r)) for r in conn.execute("SELECT * FROM walls ORDER BY id").fetchall()]
    finally:
        conn.close()


def get_wall(wid: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM walls WHERE id=?", (wid,)).fetchone()
        return _with_net_area(dict(row)) if row else None
    finally:
        conn.close()
