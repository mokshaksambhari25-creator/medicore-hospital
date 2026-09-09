"""MediCore MySQL connection settings (SERVER/mysql.env)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / "SERVER" / "mysql.env"

DEFAULTS = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "medicore",
    "password": "MediCore24",
    "database": "medicore",
}


def load_mysql_cfg() -> dict:
    cfg = dict(DEFAULTS)
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip().upper()
            val = val.strip().strip('"').strip("'")
            if key == "MYSQL_HOST":
                cfg["host"] = val
            elif key == "MYSQL_PORT":
                cfg["port"] = int(val or 3306)
            elif key == "MYSQL_USER":
                cfg["user"] = val
            elif key == "MYSQL_PASSWORD":
                cfg["password"] = val
            elif key == "MYSQL_DATABASE":
                cfg["database"] = val
    cfg["host"] = os.environ.get("MYSQL_HOST", cfg["host"])
    cfg["port"] = int(os.environ.get("MYSQL_PORT", cfg["port"]))
    cfg["user"] = os.environ.get("MYSQL_USER", cfg["user"])
    cfg["password"] = os.environ.get("MYSQL_PASSWORD", cfg["password"])
    cfg["database"] = os.environ.get("MYSQL_DATABASE", cfg["database"])
    return cfg


STORE_FIELDS = {
    "doctors": ["id", "name", "department", "phone", "available", "login"],
    "patients": ["id", "name", "age", "gender", "phone", "email", "blood", "department", "doctorId", "status", "ward"],
    "appointments": ["id", "patient", "patientId", "phone", "doctorId", "department", "date", "time", "status"],
    "pharmacy": ["id", "name", "batch", "stock", "min", "unit", "dispensed"],
    "rooms": ["id", "type", "floor", "beds", "occupied", "tariff", "occupant", "status", "patients"],
    "invoices": ["id", "patient", "patientId", "department", "amount", "method", "date", "status", "notes"],
    "diagnostics": ["id", "patient", "patientId", "test", "slot", "date", "status"],
    "alerts": ["id", "to", "template", "time", "date", "status"],
    "handover": ["id", "text", "author", "authorId", "time", "date"],
}

BOOL_FIELDS = {"available", "login"}
JSON_FIELDS = {("rooms", "patients")}
INT_FIELDS = {"age", "stock", "min", "beds", "occupied", "tariff", "dispensed"}
FLOAT_FIELDS = {"amount"}

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(32) PRIMARY KEY,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(16) NOT NULL DEFAULT 'staff'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS doctors (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  name VARCHAR(120),
  department VARCHAR(80),
  phone VARCHAR(40),
  available TINYINT(1) NOT NULL DEFAULT 1,
  login TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS patients (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  name VARCHAR(120),
  age INT,
  gender VARCHAR(20),
  phone VARCHAR(40),
  email VARCHAR(120),
  blood VARCHAR(16),
  department VARCHAR(80),
  doctorId VARCHAR(32),
  status VARCHAR(40),
  ward VARCHAR(40)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS appointments (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  patient VARCHAR(120),
  patientId VARCHAR(32),
  phone VARCHAR(40),
  doctorId VARCHAR(32),
  department VARCHAR(80),
  date VARCHAR(16),
  time VARCHAR(24),
  status VARCHAR(40)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pharmacy (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  name VARCHAR(120),
  batch VARCHAR(40),
  stock INT,
  min INT,
  unit VARCHAR(32),
  dispensed INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS rooms (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  type VARCHAR(40),
  floor VARCHAR(16),
  beds INT,
  occupied INT,
  tariff INT,
  occupant VARCHAR(120),
  status VARCHAR(40),
  patients JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS invoices (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  patient VARCHAR(120),
  patientId VARCHAR(32),
  department VARCHAR(80),
  amount DECIMAL(12,2),
  method VARCHAR(40),
  date VARCHAR(16),
  status VARCHAR(40),
  notes TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS diagnostics (
  pos INT NOT NULL,
  id VARCHAR(32) PRIMARY KEY,
  patient VARCHAR(120),
  patientId VARCHAR(32),
  test VARCHAR(80),
  slot VARCHAR(24),
  date VARCHAR(16),
  status VARCHAR(40)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS alerts (
  pos INT NOT NULL,
  id VARCHAR(64) PRIMARY KEY,
  `to` VARCHAR(120),
  template VARCHAR(120),
  time VARCHAR(16),
  date VARCHAR(16),
  status VARCHAR(40)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS handover (
  pos INT NOT NULL,
  id VARCHAR(64) PRIMARY KEY,
  text TEXT,
  author VARCHAR(120),
  authorId VARCHAR(32),
  time VARCHAR(16),
  date VARCHAR(16)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS otps (
  id VARCHAR(64) PRIMARY KEY,
  uid VARCHAR(32) NOT NULL,
  purpose VARCHAR(32) NOT NULL,
  channel VARCHAR(16) NOT NULL,
  code_hash VARCHAR(255) NOT NULL,
  expires_at VARCHAR(40) NOT NULL,
  used TINYINT(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
