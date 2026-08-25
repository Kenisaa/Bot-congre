import os
import sqlite3
from contextlib import contextmanager
from datetime import date

DB_PATH = os.environ.get("DB_PATH", "congregacion.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    nombre TEXT
);

CREATE TABLE IF NOT EXISTS reuniones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('entre_semana', 'fin_de_semana')),
    UNIQUE(fecha, tipo)
);

CREATE TABLE IF NOT EXISTS asignaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reunion_id INTEGER NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    rol TEXT NOT NULL,
    username TEXT NOT NULL,
    orden INTEGER NOT NULL DEFAULT 0,
    recordatorio_previo_enviado INTEGER NOT NULL DEFAULT 0,
    recordatorio_dia_enviado INTEGER NOT NULL DEFAULT 0
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def registrar_usuario(telegram_id: int, username: str | None, nombre: str):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO usuarios (telegram_id, username, nombre)
               VALUES (?, ?, ?)
               ON CONFLICT(telegram_id) DO UPDATE SET
                 username=excluded.username, nombre=excluded.nombre""",
            (telegram_id, (username or "").lower() or None, nombre),
        )


def buscar_usuario_por_username(username: str):
    username = username.lstrip("@").lower()
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE username = ?", (username,)
        ).fetchone()
        return dict(row) if row else None


def crear_o_obtener_reunion(fecha: str, tipo: str) -> int:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO reuniones (fecha, tipo) VALUES (?, ?)",
            (fecha, tipo),
        )
        row = conn.execute(
            "SELECT id FROM reuniones WHERE fecha = ? AND tipo = ?", (fecha, tipo)
        ).fetchone()
        return row["id"]


def limpiar_asignaciones(reunion_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM asignaciones WHERE reunion_id = ?", (reunion_id,))


def agregar_asignacion(reunion_id: int, rol: str, username: str, orden: int = 0):
    username = username.lstrip("@").lower()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO asignaciones (reunion_id, rol, username, orden)
               VALUES (?, ?, ?, ?)""",
            (reunion_id, rol, username, orden),
        )


def obtener_programa(fecha: str, tipo: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM reuniones WHERE fecha = ? AND tipo = ?", (fecha, tipo)
        ).fetchone()
        if not row:
            return []
        asignaciones = conn.execute(
            """SELECT rol, username FROM asignaciones
               WHERE reunion_id = ? ORDER BY orden, id""",
            (row["id"],),
        ).fetchall()
        return [dict(a) for a in asignaciones]


def obtener_partes_de_usuario(username: str, desde_fecha: str):
    username = username.lstrip("@").lower()
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT r.fecha, r.tipo, a.rol
               FROM asignaciones a
               JOIN reuniones r ON r.id = a.reunion_id
               WHERE a.username = ? AND r.fecha >= ?
               ORDER BY r.fecha""",
            (username, desde_fecha),
        ).fetchall()
        return [dict(r) for r in rows]


def obtener_asignaciones_pendientes(fecha: str, tipo: str, campo_recordatorio: str):
    """campo_recordatorio: 'recordatorio_previo_enviado' o 'recordatorio_dia_enviado'"""
    assert campo_recordatorio in (
        "recordatorio_previo_enviado",
        "recordatorio_dia_enviado",
    )
    with get_conn() as conn:
        rows = conn.execute(
            f"""SELECT a.id, a.rol, a.username, r.fecha, r.tipo
                FROM asignaciones a
                JOIN reuniones r ON r.id = a.reunion_id
                WHERE r.fecha = ? AND r.tipo = ? AND a.{campo_recordatorio} = 0""",
            (fecha, tipo),
        ).fetchall()
        return [dict(r) for r in rows]


def marcar_recordatorio_enviado(asignacion_id: int, campo_recordatorio: str):
    assert campo_recordatorio in (
        "recordatorio_previo_enviado",
        "recordatorio_dia_enviado",
    )
    with get_conn() as conn:
        conn.execute(
            f"UPDATE asignaciones SET {campo_recordatorio} = 1 WHERE id = ?",
            (asignacion_id,),
        )
