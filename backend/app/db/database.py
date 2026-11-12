"""MySQL persistence and schema initialization for StayGrid."""

import re
from typing import Iterator

import mysql.connector
from mysql.connector import Error

from app.core.config import ADMIN_EMAIL, ADMIN_PASSWORD, MYSQL_DATABASE, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_USER
from app.core.security import hash_password


class Row(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


class Cursor:
    def __init__(self, cursor):
        self._cursor = cursor
        self.lastrowid = cursor.lastrowid

    def fetchone(self):
        row = self._cursor.fetchone()
        return Row(row) if row else None

    def fetchall(self):
        return [Row(row) for row in self._cursor.fetchall()]

    def __iter__(self):
        return iter(self.fetchall())


class Connection:
    def __init__(self, raw):
        self.raw = raw

    @staticmethod
    def _convert(sql: str, params):
        sql = sql.replace("BEGIN IMMEDIATE", "START TRANSACTION")
        if isinstance(params, dict):
            names = []
            def replace(match):
                names.append(match.group(1))
                return "%s"
            return re.sub(r":([A-Za-z_]\w*)", replace, sql), tuple(params[name] for name in names)
        return sql.replace("?", "%s"), params

    def execute(self, sql, params=()):
        statement, values = self._convert(sql, params)
        cursor = self.raw.cursor(dictionary=True)
        cursor.execute(statement, values)
        return Cursor(cursor)

    def executemany(self, sql, params):
        statement, _ = self._convert(sql, params[0] if params else ())
        cursor = self.raw.cursor(dictionary=True)
        cursor.executemany(statement, params)
        return Cursor(cursor)

    def commit(self):
        self.raw.commit()

    def rollback(self):
        self.raw.rollback()

    def close(self):
        self.raw.close()


def _server_connection():
    return mysql.connector.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD)


def connect() -> Connection:
    raw = mysql.connector.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    return Connection(raw)


def get_db() -> Iterator[Connection]:
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
    server = _server_connection()
    try:
        cursor = server.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        server.commit()
    finally:
        server.close()

    db = connect()
    statements = [
        """CREATE TABLE IF NOT EXISTS roles (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(30) NOT NULL UNIQUE, description VARCHAR(255) NOT NULL DEFAULT '') ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(120) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, role ENUM('user','admin','hotel_admin') NOT NULL DEFAULT 'user', account_status ENUM('pending','active','suspended','blocked') NOT NULL DEFAULT 'active', approved_at DATETIME NULL, approved_by BIGINT NULL, business_name VARCHAR(180) NULL, phone VARCHAR(40) NULL, created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, created_by BIGINT NULL, updated_by BIGINT NULL) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS user_roles (user_id BIGINT NOT NULL, role_id BIGINT NOT NULL, assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(user_id,role_id), FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS hotels (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(160) NOT NULL, description TEXT NOT NULL, address VARCHAR(300) NOT NULL, city VARCHAR(100) NOT NULL, country VARCHAR(100) NOT NULL, contact VARCHAR(100) NOT NULL, rating DECIMAL(2,1) NOT NULL DEFAULT 0, amenities VARCHAR(1000) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX idx_hotels_city_active(city,is_active)) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS room_types (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, description TEXT NOT NULL, capacity INT NOT NULL, base_price DECIMAL(12,2) NOT NULL) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS rooms (id BIGINT PRIMARY KEY AUTO_INCREMENT, hotel_id BIGINT NOT NULL, room_type_id BIGINT NOT NULL, room_number VARCHAR(20) NOT NULL, floor INT NOT NULL DEFAULT 1, status ENUM('available','maintenance','inactive') NOT NULL DEFAULT 'available', price DECIMAL(12,2) NULL, UNIQUE KEY uq_room_number(hotel_id,room_number), FOREIGN KEY(hotel_id) REFERENCES hotels(id) ON DELETE CASCADE, FOREIGN KEY(room_type_id) REFERENCES room_types(id)) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS bookings (id BIGINT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT NOT NULL, room_id BIGINT NOT NULL, check_in DATE NOT NULL, check_out DATE NOT NULL, guests INT NOT NULL, total_amount DECIMAL(12,2) NOT NULL, status ENUM('confirmed','cancelled','completed') NOT NULL DEFAULT 'confirmed', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(room_id) REFERENCES rooms(id), INDEX idx_bookings_room_dates(room_id,check_in,check_out,status)) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS categories (id BIGINT PRIMARY KEY AUTO_INCREMENT, slug VARCHAR(50) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, description VARCHAR(255) NOT NULL, count_source ENUM('hotels','room_types','rooms','availability','bookings','guests','administration') NOT NULL, sort_order INT NOT NULL DEFAULT 0, is_active BOOLEAN NOT NULL DEFAULT TRUE) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS password_reset_tokens (id BIGINT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT NOT NULL, token_hash CHAR(64) NOT NULL UNIQUE, expires_at DATETIME NOT NULL, used_at DATETIME NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, INDEX idx_reset_user(user_id,expires_at)) ENGINE=InnoDB""",
    ]
    try:
        for statement in statements:
            db.execute(statement)
        db.executemany("INSERT INTO roles(name,description) VALUES(%s,%s) ON DUPLICATE KEY UPDATE description=VALUES(description)", [
            ("user", "Guest account for browsing and booking stays"),
            ("admin", "Administrator account for managing StayGrid"),
            ("hotel_admin", "Hotel operator awaiting or holding approval"),
        ])
        category_rows = [
            ("hotels", "Hotels", "Discover and manage StayGrid properties", "hotels", 1),
            ("room_types", "Room types", "Suites, rooms, capacity, and base pricing", "room_types", 2),
            ("rooms", "Rooms", "Physical rooms and inventory status", "rooms", 3),
            ("availability", "Availability", "Find rooms for dates and guest capacity", "availability", 4),
            ("bookings", "Bookings", "Reservations, cancellations, and stay status", "bookings", 5),
            ("guests", "Guests", "Customer accounts and booking profiles", "guests", 6),
            ("administration", "Administration", "Manage properties, rooms, and bookings", "administration", 7),
        ]
        db.executemany("INSERT INTO categories(slug,name,description,count_source,sort_order) VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),description=VALUES(description),count_source=VALUES(count_source),sort_order=VALUES(sort_order)", category_rows)
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            db.execute("INSERT INTO users(name,email,password_hash,role,account_status,approved_at) VALUES(%s,%s,%s,'admin','active',NOW()) ON DUPLICATE KEY UPDATE email=email", ("StayGrid Admin", ADMIN_EMAIL.lower(), hash_password(ADMIN_PASSWORD)))
        db.execute("INSERT IGNORE INTO user_roles(user_id,role_id) SELECT u.id,r.id FROM users u JOIN roles r ON r.name=u.role")
        db.execute("UPDATE users SET role='user' WHERE role='customer'")
        db.execute("ALTER TABLE users MODIFY role ENUM('user','admin','hotel_admin') NOT NULL DEFAULT 'user'")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS account_status ENUM('pending','active','suspended','blocked') NOT NULL DEFAULT 'active'")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_at DATETIME NULL")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS approved_by BIGINT NULL")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS business_name VARCHAR(180) NULL")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(40) NULL")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_by BIGINT NULL")
        db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_by BIGINT NULL")
        for table in ("hotels", "room_types", "rooms", "bookings", "categories", "password_reset_tokens"):
            db.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
            db.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
            db.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS created_by BIGINT NULL")
            db.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS updated_by BIGINT NULL")
        db.execute("DROP TABLE IF EXISTS admins")
        db.commit()
    finally:
        db.close()
