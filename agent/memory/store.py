import sqlite3
from pathlib import Path

class MemoryStore:
    def __init__(self, db_path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = db_path
        with sqlite3.connect(self.db) as con:
            con.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, key TEXT, value TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
            con.commit()

    def remember(self, key, value):
        with sqlite3.connect(self.db) as con:
            con.execute("INSERT INTO memories(key,value) VALUES(?,?)", (key, value))
            con.commit()

    def search(self, query, limit=8):
        q = f"%{query}%"
        with sqlite3.connect(self.db) as con:
            rows = con.execute("SELECT key,value,created_at FROM memories WHERE key LIKE ? OR value LIKE ? ORDER BY id DESC LIMIT ?", (q,q,limit)).fetchall()
        return [{"key":r[0],"value":r[1],"created_at":r[2]} for r in rows]

    def recent(self, limit=20):
        with sqlite3.connect(self.db) as con:
            rows = con.execute("SELECT key,value,created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{"key":r[0],"value":r[1],"created_at":r[2]} for r in rows]
