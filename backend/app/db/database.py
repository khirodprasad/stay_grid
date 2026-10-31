import sqlite3
from typing import Iterator

from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, DATABASE_PATH
from app.core.security import hash_password


def connect() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def get_db() -> Iterator[sqlite3.Connection]:
    connection = connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    db = connect()
    try:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer' CHECK(role IN ('customer','admin')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS hotels (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            address TEXT NOT NULL, city TEXT NOT NULL, country TEXT NOT NULL DEFAULT '',
            contact TEXT NOT NULL DEFAULT '', rating REAL NOT NULL DEFAULT 0 CHECK(rating BETWEEN 0 AND 5),
            amenities TEXT NOT NULL DEFAULT '', is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS room_types (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            capacity INTEGER NOT NULL CHECK(capacity > 0), base_price REAL NOT NULL CHECK(base_price >= 0)
        );
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY, hotel_id INTEGER NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
            room_type_id INTEGER NOT NULL REFERENCES room_types(id), room_number TEXT NOT NULL,
            floor INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT 'available'
                CHECK(status IN ('available','maintenance','inactive')),
            price REAL CHECK(price IS NULL OR price >= 0), UNIQUE(hotel_id, room_number)
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            room_id INTEGER NOT NULL REFERENCES rooms(id), check_in TEXT NOT NULL, check_out TEXT NOT NULL,
            guests INTEGER NOT NULL CHECK(guests > 0), total_amount REAL NOT NULL CHECK(total_amount >= 0),
            status TEXT NOT NULL DEFAULT 'confirmed' CHECK(status IN ('confirmed','cancelled','completed')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, CHECK(check_out > check_in)
        );
        CREATE INDEX IF NOT EXISTS idx_bookings_room_dates ON bookings(room_id, check_in, check_out, status);
        CREATE INDEX IF NOT EXISTS idx_hotels_city_active ON hotels(city, is_active);
        """)
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            db.execute("INSERT OR IGNORE INTO users(name,email,password_hash,role) VALUES(?,?,?,'admin')",
                       ("StayGrid Admin", ADMIN_EMAIL, hash_password(ADMIN_PASSWORD)))
        db.commit()
    finally:
        db.close()
