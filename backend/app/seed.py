from app.db import connect

DEFAULT_PASTE_COVERAGE = "5"  # m² per liter


def init_db():
    conn = connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS walls(
            id INTEGER PRIMARY KEY, name TEXT, perimeter REAL, height REAL,
            door_area REAL NOT NULL DEFAULT 0,
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
    # Migrate pre-paste databases: registered door openings live on the wall.
    wall_cols = [r["name"] for r in conn.execute("PRAGMA table_info(walls)").fetchall()]
    if "door_area" not in wall_cols:
        conn.execute("ALTER TABLE walls ADD COLUMN door_area REAL NOT NULL DEFAULT 0")
    # Default paste coverage exists even for databases seeded before paste.
    conn.execute(
        "INSERT OR IGNORE INTO settings(key,value) VALUES ('paste_coverage',?)",
        (DEFAULT_PASTE_COVERAGE,),
    )
    if conn.execute("SELECT COUNT(*) c FROM walls").fetchone()["c"] == 0:
        conn.executemany(
            "INSERT INTO walls(name,perimeter,height,door_area,data_quality,note) VALUES (?,?,?,?,?,?)",
            [
                ("主卧一圈", 16.0, 2.7, 1.8, "clean", ""),
                ("大花匹配", 20.0, 2.8, 1.8, "clean", "需对花"),
                ("脏数据-零周长", 0.0, 2.7, 0.0, "dirty", "周长为0"),
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
    conn.commit()
    conn.close()
