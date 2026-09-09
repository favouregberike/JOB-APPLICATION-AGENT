import sqlite3
from datetime import datetime, timezone

DB = "jobs.db"

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        id TEXT PRIMARY KEY,title TEXT,company TEXT,location TEXT,url TEXT,source TEXT,
        posted TEXT,description TEXT,salary_min REAL,salary_max REAL,currency TEXT,
        country TEXT,score REAL,status TEXT DEFAULT 'New',notes TEXT,
        tailored_cv TEXT,cover_letter TEXT,created_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,job_id TEXT,action TEXT,
        notes TEXT,created_at TEXT)""")
    c.commit()
    return c

def upsert_jobs(jobs):
    c = conn()
    for j in jobs:
        c.execute("""INSERT OR IGNORE INTO jobs
        (id,title,company,location,url,source,posted,description,salary_min,
         salary_max,currency,country,score,status,created_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (j["id"],j["title"],j["company"],j["location"],j["url"],j["source"],
         j["posted"],j["description"],j["salary_min"],j["salary_max"],
         j["currency"],j["country"],j["score"],"New",
         datetime.now(timezone.utc).isoformat()))
    c.commit()
    c.close()

def jobs():
    c = conn()
    rows = c.execute("SELECT * FROM jobs ORDER BY score DESC,posted DESC").fetchall()
    c.close()
    return rows

def status(job_id, value, notes=""):
    c = conn()
    c.execute("UPDATE jobs SET status=?,notes=? WHERE id=?", (value,notes,job_id))
    c.execute("INSERT INTO applications(job_id,action,notes,created_at) VALUES(?,?,?,?)",
              (job_id,value,notes,datetime.now(timezone.utc).isoformat()))
    c.commit()
    c.close()
