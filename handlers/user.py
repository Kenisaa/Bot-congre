from datetime import datetime

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para

TIPO_CORTO = {
    "entre_semana": "Entre semana",
    "fin_de_semana": "Fin de semana",
}


def miparte(telefono: str) -> str:
    hoy = datetime.now(config.TIMEZONE).date().isoformat()
    partes = db.obtener_partes_de_usuario(telefono, hoy)

    if not partes:
        return "No tienes partes asignadas próximamente."

    lineas = [
        f"• {formatear_fecha(p['fecha'])} ({TIPO_CORTO[p['tipo']]}): {p['rol']}"
        for p in partes
    ]
    return "Tus próximas partes:\n\n" + "\n".join(lineas)


def programa(argumentos: list[str]) -> str:
    tipo = "fin_de_semana"
    if argumentos and argumentos[0].lower() in ("semana", "entre_semana", "entresemana"):
        tipo = "entre_semana"

    dia_default = config.MIDWEEK_DAY if tipo == "entre_semana" else config.WEEKEND_DAY
    fecha = proxima_fecha_para(dia_default)
    asignaciones = db.obtener_programa(fecha.isoformat(), tipo)

    if not asignaciones:
        return (
            f"Aún no hay programa cargado para {config.TIPO_LABEL[tipo]} "
            f"del {formatear_fecha(fecha.isoformat())}."
        )

    lineas = [f"• {a['rol']}: {a['telefono']}" for a in asignaciones]
    return (
        f"{config.TIPO_LABEL[tipo]} — {formatear_fecha(fecha.isoformat())}\n\n"
        + "\n".join(lineas)
    )
