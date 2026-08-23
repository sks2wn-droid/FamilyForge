"""
FamilyForge - Database module
SQLite schema and helpers for photo metadata, faces, people, etc.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

DB_PATH = Path("familyforge.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_path TEXT UNIQUE NOT NULL,
    original_scan_path TEXT,
    processed_path TEXT,
    master_path TEXT,
    filename TEXT,
    file_hash TEXT,
    perceptual_hash TEXT,
    width INTEGER,
    height INTEGER,
    scan_date TEXT,
    estimated_date TEXT,
    date_confidence REAL DEFAULT 0.0,
    decade TEXT,
    notes TEXT,
    front_ocr_text TEXT,
    back_ocr_text TEXT,
    processing_status TEXT DEFAULT 'raw',
    restoration_params TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    birth_year INTEGER,
    death_year INTEGER,
    notes TEXT,
    representative_face_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER NOT NULL REFERENCES photos(id) ON DELETE CASCADE,
    person_id INTEGER REFERENCES people(id),
    embedding BLOB,
    bbox TEXT,
    confidence REAL,
    landmarks TEXT,
    cluster_id INTEGER,
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS photo_tags (
    photo_id INTEGER REFERENCES photos(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (photo_id, tag_id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date_start TEXT,
    date_end TEXT,
    location TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS photo_events (
    photo_id INTEGER REFERENCES photos(id) ON DELETE CASCADE,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    PRIMARY KEY (photo_id, event_id)
);

CREATE TABLE IF NOT EXISTS processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    photo_id INTEGER REFERENCES photos(id) ON DELETE CASCADE,
    step TEXT NOT NULL,
    params TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_faces_photo ON faces(photo_id);
CREATE INDEX IF NOT EXISTS idx_faces_person ON faces(person_id);
CREATE INDEX IF NOT EXISTS idx_faces_cluster ON faces(cluster_id);
CREATE INDEX IF NOT EXISTS idx_photos_status ON photos(processing_status);
CREATE INDEX IF NOT EXISTS idx_photos_decade ON photos(decade);
CREATE INDEX IF NOT EXISTS idx_photos_hash ON photos(perceptual_hash);
"""

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path: Path = DB_PATH) -> None:
    """Create tables if they do not exist."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()

def add_photo(
    original_path: str,
    *,
    processed_path: Optional[str] = None,
    master_path: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    file_hash: Optional[str] = None,
    perceptual_hash: Optional[str] = None,
    original_scan_path: Optional[str] = None,
    status: str = "raw",
) -> int:
    filename = Path(original_path).name
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO photos (
                original_path, original_scan_path, processed_path, master_path,
                filename, file_hash, perceptual_hash, width, height, processing_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                original_path, original_scan_path, processed_path, master_path,
                filename, file_hash, perceptual_hash, width, height, status
            ),
        )
        conn.commit()
        return cur.lastrowid

def update_photo_status(photo_id: int, status: str, restoration_params: Optional[Dict] = None) -> None:
    params_json = json.dumps(restoration_params) if restoration_params else None
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE photos
            SET processing_status = ?, restoration_params = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, params_json, photo_id),
        )
        conn.commit()

def get_photo_by_path(path: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM photos WHERE original_path = ?", (path,)).fetchone()

def list_photos(status: Optional[str] = None, limit: int = 100) -> List[sqlite3.Row]:
    with get_connection() as conn:
        if status:
            return conn.execute(
                "SELECT * FROM photos WHERE processing_status = ? ORDER BY id DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        return conn.execute("SELECT * FROM photos ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

def count_photos(status: Optional[str] = None) -> int:
    with get_connection() as conn:
        if status:
            row = conn.execute("SELECT COUNT(*) as c FROM photos WHERE processing_status = ?", (status,)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) as c FROM photos").fetchone()
        return row["c"] if row else 0

def add_person(name: str, birth_year: Optional[int] = None, notes: Optional[str] = None) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO people (name, birth_year, notes) VALUES (?, ?, ?)",
            (name, birth_year, notes),
        )
        conn.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = conn.execute("SELECT id FROM people WHERE name = ?", (name,)).fetchone()
        return row["id"]

def count_people() -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM people").fetchone()
        return row["c"] if row else 0

def add_face(
    photo_id: int,
    bbox: List[float],
    confidence: float,
    embedding: Optional[bytes] = None,
    person_id: Optional[int] = None,
    cluster_id: Optional[int] = None,
    quality_score: Optional[float] = None,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO faces (photo_id, person_id, embedding, bbox, confidence, cluster_id, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                photo_id, person_id, embedding, json.dumps(bbox), confidence, cluster_id, quality_score
            ),
        )
        conn.commit()
        return cur.lastrowid

def get_face_clusters() -> Dict[int, List[sqlite3.Row]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM faces WHERE cluster_id IS NOT NULL ORDER BY cluster_id, confidence DESC"
        ).fetchall()
    clusters: Dict[int, List] = {}
    for r in rows:
        cid = r["cluster_id"]
        clusters.setdefault(cid, []).append(r)
    return clusters

def assign_person_to_cluster(cluster_id: int, person_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE faces SET person_id = ? WHERE cluster_id = ?",
            (person_id, cluster_id),
        )
        conn.commit()

def log_processing(photo_id: int, step: str, params: Optional[Dict] = None) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO processing_log (photo_id, step, params) VALUES (?, ?, ?)",
            (photo_id, step, json.dumps(params) if params else None),
        )
        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH.resolve())
