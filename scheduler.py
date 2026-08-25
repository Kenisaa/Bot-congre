import logging
from datetime import datetime, timedelta

from telegram.error import TelegramError
from telegram.ext import ContextTypes

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para

logger = logging.getLogger(__name__)

REUNIONES = [
    ("entre_semana", config.MIDWEEK_DAY),
    ("fin_de_semana", config.WEEKEND_DAY),
]


async def _enviar_recordatorio(context: ContextTypes.DEFAULT_TYPE, asignacion: dict, cuando: str):
    usuario = db.buscar_usuario_por_username(asignacion["username"])
    fecha_fmt = formatear_fecha(asignacion["fecha"])
    tipo_label = config.TIPO_LABEL[asignacion["tipo"]]

    if cuando == "previo":
        texto = (
            f"Recordatorio: tienes asignada la parte '{asignacion['rol']}' "
            f"en la {tipo_label} del {fecha_fmt}."
        )
    else:
        texto = (
            f"Hoy es tu parte: '{asignacion['rol']}' en la {tipo_label} "
            f"({fecha_fmt}). ¡Nos vemos en la reunión!"
        )

    if not usuario:
        logger.warning(
            "No se pudo notificar a @%s (no ha hecho /start): %s",
            asignacion["username"],
            asignacion["rol"],
        )
        return

    try:
        await context.bot.send_message(chat_id=usuario["telegram_id"], text=texto)
    except TelegramError:
        logger.exception("Error enviando recordatorio a @%s", asignacion["username"])


async def revisar_recordatorios(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.now(config.TIMEZONE).date()

    for tipo, dia_semana in REUNIONES:
        fecha_reunion = proxima_fecha_para(dia_semana, desde=hoy)

        dias_hasta = (fecha_reunion - hoy).days

        if dias_hasta == config.REMINDER_DAYS_BEFORE:
            pendientes = db.obtener_asignaciones_pendientes(
                fecha_reunion.isoformat(), tipo, "recordatorio_previo_enviado"
            )
            for asignacion in pendientes:
                await _enviar_recordatorio(context, asignacion, "previo")
                db.marcar_recordatorio_enviado(asignacion["id"], "recordatorio_previo_enviado")

        if dias_hasta == 0:
            pendientes = db.obtener_asignaciones_pendientes(
                fecha_reunion.isoformat(), tipo, "recordatorio_dia_enviado"
            )
            for asignacion in pendientes:
                await _enviar_recordatorio(context, asignacion, "dia")
                db.marcar_recordatorio_enviado(asignacion["id"], "recordatorio_dia_enviado")


def programar_revision_diaria(application):
    """Ejecuta la revisión de recordatorios todos los días a las 8:00 (hora local configurada)."""
    application.job_queue.run_daily(
        revisar_recordatorios,
        time=datetime.strptime("08:00", "%H:%M").time().replace(tzinfo=config.TIMEZONE),
        name="revision_diaria_recordatorios",
    )
