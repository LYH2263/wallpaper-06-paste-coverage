from app.db import connect

DEFAULT_COVERAGE_M2_PER_L = "5"


def init_db():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS walls(
            id INTEGER PRIMARY KEY, name TEXT, perimeter REAL, height REAL,
            door_area_m2 REAL NOT NULL DEFAULT 0,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS rolls(
            id INTEGER PRIMARY KEY, name TEXT, width REAL, length REAL, pattern_cm REAL,
            data_quality TEXT DEFAULT 'clean', note TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS calc_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, wall_id INTEGER, roll_id INTEGER,
            result_json TEXT, note TEXT, created_at TEXT
        );
        """
    )
    # Idempotent migration for databases created before door_area_m2 existed.
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(walls)").fetchall()]
    if "door_area_m2" not in cols:
        conn.execute("ALTER TABLE walls ADD COLUMN door_area_m2 REAL NOT NULL DEFAULT 0")
    if conn.execute("SELECT COUNT(*) c FROM walls").fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO walls(name,perimeter,height,door_area_m2,data_quality,note) VALUES (?,?,?,?,?,?)",
            [
                ("主卧一圈", 16.0, 2.7, 1.9, "clean", ""),
                ("大花匹配", 20.0, 2.8, 2.4, "clean", "需对花"),
                ("脏数据-零周长", 0.0, 2.7, 0.0, "dirty", "周长为0"),
                ("门洞超扣演示", 4.0, 2.5, 12.0, "clean", "门洞面积大于毛面积"),
            ],
        )
        conn.executemany(
            "INSERT INTO rolls(name,width,length,pattern_cm,data_quality,note) VALUES (?,?,?,?,?,?)",
            [
                ("素色53", 0.53, 10.0, 0, "clean", ""),
                ("大花64", 0.53, 10.0, 64, "clean", ""),
                ("脏数据-零宽", 0.0, 10.0, 0, "dirty", ""),
            ],
        )
        conn.execute("INSERT INTO settings(key,value) VALUES ('unit','roll')")
    conn.execute(
        "INSERT OR IGNORE INTO settings(key,value) VALUES ('paste_coverage_m2_per_l',?)",
        (DEFAULT_COVERAGE_M2_PER_L,),
    )
    conn.commit()
    conn.close()
