from datetime import date, datetime, timedelta

import config

DIAS_ES = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]


def formatear_fecha(fecha_str: str) -> str:
    d = date.fromisoformat(fecha_str)
    return f"{DIAS_ES[d.weekday()]} {d.day:02d}/{d.month:02d}/{d.year}"


def proxima_fecha_para(dia_semana: int, desde: date | None = None) -> date:
    """Próxima fecha (incluyendo hoy) que cae en dia_semana (0=lunes..6=domingo)."""
    desde = desde or datetime.now(config.TIMEZONE).date()
    delta = (dia_semana - desde.weekday()) % 7
    return desde + timedelta(days=delta)
