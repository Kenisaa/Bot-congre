import re
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para
from handlers.common import es_admin

LINEA_RE = re.compile(r"^\s*([^:]+):\s*@?(\w+)\s*$")

AYUDA_CARGA = (
    "Uso:\n"
    "/cargar_semana [YYYY-MM-DD]\n"
    "/cargar_finde [YYYY-MM-DD]\n\n"
    "Luego, en la(s) línea(s) siguiente(s) del mismo mensaje, pon una asignación "
    "por línea con el formato:\n"
    "Rol: @usuario\n\n"
    "Ejemplo:\n"
    "/cargar_semana\n"
    "Presidente: @juanperez\n"
    "Oración inicial: @carlosgomez\n"
    "Tesoros de la Biblia: @juanperez\n"
    "Perlas escondidas: @pedroramirez\n"
    "Estudio bíblico de la congregación (conductor): @juanperez\n"
    "Estudio bíblico de la congregación (lector): @miguelrosa\n"
    "Oración final: @miguelrosa\n\n"
    "Si no pones fecha, se usa la próxima reunión de ese tipo según la configuración."
)


def _parse_asignaciones(texto_lineas: list[str]):
    asignaciones = []
    errores = []
    for i, linea in enumerate(texto_lineas, start=1):
        if not linea.strip():
            continue
        m = LINEA_RE.match(linea)
        if not m:
            errores.append(f"Línea {i} no entendida: '{linea}'")
            continue
        rol, username = m.group(1).strip(), m.group(2).strip()
        asignaciones.append((rol, username))
    return asignaciones, errores


async def _cargar(update: Update, context: ContextTypes.DEFAULT_TYPE, tipo: str, dia_default: int):
    user = update.effective_user
    if not es_admin(user.id):
        await update.message.reply_text("Solo un administrador puede cargar el programa.")
        return

    lineas = update.message.text.split("\n")
    primera = lineas[0]
    resto = lineas[1:]

    partes_comando = primera.split()
    fecha_str = None
    if len(partes_comando) > 1:
        fecha_str = partes_comando[1]

    if fecha_str:
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            await update.message.reply_text(
                "Fecha inválida, usa el formato YYYY-MM-DD.\n\n" + AYUDA_CARGA
            )
            return
    else:
        fecha = proxima_fecha_para(dia_default)

    asignaciones, errores = _parse_asignaciones(resto)

    if not asignaciones:
        await update.message.reply_text(
            "No encontré asignaciones para cargar.\n\n" + AYUDA_CARGA
        )
        return

    reunion_id = db.crear_o_obtener_reunion(fecha.isoformat(), tipo)
    db.limpiar_asignaciones(reunion_id)
    for orden, (rol, username) in enumerate(asignaciones):
        db.agregar_asignacion(reunion_id, rol, username, orden)

    resumen = "\n".join(f"• {rol}: @{u}" for rol, u in asignaciones)
    mensaje = (
        f"Programa cargado para {config.TIPO_LABEL[tipo]} "
        f"del {formatear_fecha(fecha.isoformat())}:\n\n{resumen}"
    )
    if errores:
        mensaje += "\n\nAtención, hubo líneas ignoradas:\n" + "\n".join(errores)
    await update.message.reply_text(mensaje)


async def cargar_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _cargar(update, context, "entre_semana", config.MIDWEEK_DAY)


async def cargar_finde(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _cargar(update, context, "fin_de_semana", config.WEEKEND_DAY)


async def ayuda_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not es_admin(user.id):
        await update.message.reply_text("Solo un administrador puede ver esto.")
        return
    await update.message.reply_text(AYUDA_CARGA)
