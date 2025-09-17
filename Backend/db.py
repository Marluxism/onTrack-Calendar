import sqlite3, os, datetime as dt

DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      start_dt TEXT NOT NULL,
      end_dt   TEXT NOT NULL,
      all_day INTEGER DEFAULT 0,
      color TEXT DEFAULT '#3b82f6',
      location TEXT
    );
    """)
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM events")
    if cur.fetchone()["c"] == 0:
        now = dt.datetime.utcnow().replace(microsecond=0)
        cur.execute("""INSERT INTO events (title, description, start_dt, end_dt, all_day, color, location)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("Project kickoff", "Calendar MVP", now.isoformat()+"Z",
                     (now+dt.timedelta(hours=1)).isoformat()+"Z", 0, "#22c55e", "Zoom"))
        cur.execute("""INSERT INTO events (title, description, start_dt, end_dt, all_day, color, location)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    ("All-day study", "Calc grind",
                     (now.date().isoformat()+"T00:00:00Z"),
                     (now.date().isoformat()+"T23:59:59Z"), 1, "#f59e0b", "Library"))
        conn.commit()
    conn.close()
