import sqlite3
import gpxpy
import os

DIR = "/home/makeworld/Phone Storage/gpslogger"

con = sqlite3.connect("points.db", autocommit=False)
cur = con.cursor()

cur.execute(
    """
CREATE TABLE IF NOT EXISTS points (
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    ele REAL NOT NULL,
    time INTEGER PRIMARY KEY
)
"""
)
cur.execute(
    """
CREATE TABLE IF NOT EXISTS files (
    name TEXT PRIMARY KEY,
    last_mod INTEGER NOT NULL
)
"""
)
con.commit()

for filename in sorted(os.listdir(DIR)):
    filepath = os.path.join(DIR, filename)
    mtime = int(os.path.getmtime(filepath))

    # Skip if already processed and not changed since then
    res = cur.execute(
        "SELECT EXISTS (SELECT 1 FROM files WHERE name = ? AND last_mod = ?)",
        (filename, mtime),
    )
    exists = res.fetchone()[0]
    if exists:
        print(f"Skipping {filename}")
        continue

    print(f"Processing {filename}...")
    with open(filepath, "r") as f:
        gpx = gpxpy.parse(f)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    time = point.time
                    assert time is not None
                    assert time.tzinfo is not None
                    time = int(time.timestamp())  # Convert to Unix time
                    cur.execute(
                        "INSERT INTO points VALUES (?,?,?,?) ON CONFLICT(time) DO NOTHING",
                        (point.latitude, point.longitude, point.elevation, time),
                    )

    cur.execute(
        # UPSERT
        "INSERT INTO files VALUES (?,?) ON CONFLICT(name) DO UPDATE SET last_mod = ?",
        (filename, mtime, mtime),
    )
    con.commit()

cur.close()
con.close()
