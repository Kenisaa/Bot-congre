from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para

TIPO_CORTO = {
    "entre_semana": "Entre semana",
    "fin_de_semana": "Fin de semana",
}


async def miparte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.registrar_usuario(user.id, user.username, user.full_name)

    if not user.username:
        await update.message.reply_text(
            "No tienes un @username configurado en Telegram. "
            "Créalo en Ajustes > Nombre de usuario para que pueda encontrarte."
        )
        return

    hoy = datetime.now(config.TIMEZONE).date().isoformat()
    partes = db.obtener_partes_de_usuario(user.username, hoy)

    if not partes:
        await update.message.reply_text("No tienes partes asignadas próximamente.")
        return

    lineas = [
        f"• {formatear_fecha(p['fecha'])} ({TIPO_CORTO[p['tipo']]}): {p['rol']}"
        for p in partes
    ]
    await update.message.reply_text("Tus próximas partes:\n\n" + "\n".join(lineas))


async def programa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    tipo = "fin_de_semana"
    if args and args[0].lower() in ("semana", "entre_semana", "entresemana"):
        tipo = "entre_semana"

    dia_default = config.MIDWEEK_DAY if tipo == "entre_semana" else config.WEEKEND_DAY
    fecha = proxima_fecha_para(dia_default)
    asignaciones = db.obtener_programa(fecha.isoformat(), tipo)

    if not asignaciones:
        await update.message.reply_text(
            f"Aún no hay programa cargado para {config.TIPO_LABEL[tipo]} "
            f"del {formatear_fecha(fecha.isoformat())}."
        )
        return

    lineas = [f"• {a['rol']}: @{a['username']}" for a in asignaciones]
    texto = (
        f"{config.TIPO_LABEL[tipo]} — {formatear_fecha(fecha.isoformat())}\n\n"
        + "\n".join(lineas)
    )
    await update.message.reply_text(texto)
