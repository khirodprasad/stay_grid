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
        """CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(120) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL, role ENUM('customer','admin') NOT NULL DEFAULT 'customer', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS hotels (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(160) NOT NULL, description TEXT NOT NULL, address VARCHAR(300) NOT NULL, city VARCHAR(100) NOT NULL, country VARCHAR(100) NOT NULL, contact VARCHAR(100) NOT NULL, rating DECIMAL(2,1) NOT NULL DEFAULT 0, amenities VARCHAR(1000) NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX idx_hotels_city_active(city,is_active)) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS room_types (id BIGINT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(100) NOT NULL, description TEXT NOT NULL, capacity INT NOT NULL, base_price DECIMAL(12,2) NOT NULL) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS rooms (id BIGINT PRIMARY KEY AUTO_INCREMENT, hotel_id BIGINT NOT NULL, room_type_id BIGINT NOT NULL, room_number VARCHAR(20) NOT NULL, floor INT NOT NULL DEFAULT 1, status ENUM('available','maintenance','inactive') NOT NULL DEFAULT 'available', price DECIMAL(12,2) NULL, UNIQUE KEY uq_room_number(hotel_id,room_number), FOREIGN KEY(hotel_id) REFERENCES hotels(id) ON DELETE CASCADE, FOREIGN KEY(room_type_id) REFERENCES room_types(id)) ENGINE=InnoDB""",
        """CREATE TABLE IF NOT EXISTS bookings (id BIGINT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT NOT NULL, room_id BIGINT NOT NULL, check_in DATE NOT NULL, check_out DATE NOT NULL, guests INT NOT NULL, total_amount DECIMAL(12,2) NOT NULL, status ENUM('confirmed','cancelled','completed') NOT NULL DEFAULT 'confirmed', created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(room_id) REFERENCES rooms(id), INDEX idx_bookings_room_dates(room_id,check_in,check_out,status)) ENGINE=InnoDB""",
    ]
    try:
        for statement in statements:
            db.execute(statement)
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(%s,%s,%s,'admin') ON DUPLICATE KEY UPDATE email=email", ("StayGrid Admin", ADMIN_EMAIL, hash_password(ADMIN_PASSWORD)))
        db.commit()
    finally:
        db.close()
