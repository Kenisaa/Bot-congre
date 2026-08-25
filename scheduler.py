import json
import logging
from datetime import datetime

from twilio.base.exceptions import TwilioRestException

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para

logger = logging.getLogger(__name__)

REUNIONES = [
    ("entre_semana", config.MIDWEEK_DAY),
    ("fin_de_semana", config.WEEKEND_DAY),
]


def _enviar_recordatorio(twilio_client, asignacion: dict, cuando: str):
    fecha_fmt = formatear_fecha(asignacion["fecha"])
    tipo_label = config.TIPO_LABEL[asignacion["tipo"]]

    content_sid = (
        config.CONTENT_SID_PREVIO if cuando == "previo" else config.CONTENT_SID_DIA
    )
    content_variables = json.dumps(
        {"1": asignacion["rol"], "2": tipo_label, "3": fecha_fmt}
    )

    destino = "whatsapp:" + asignacion["telefono"]
    try:
        if content_sid:
            twilio_client.messages.create(
                from_=config.TWILIO_WHATSAPP_FROM,
                to=destino,
                content_sid=content_sid,
                content_variables=content_variables,
            )
        else:
            # Sin plantilla configurada todavía: solo funciona si la
            # persona escribió al bot en las últimas 24h (modo pruebas).
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
            twilio_client.messages.create(
                from_=config.TWILIO_WHATSAPP_FROM, to=destino, body=texto
            )
    except TwilioRestException:
        logger.exception("Error enviando recordatorio a %s", asignacion["telefono"])


def revisar_recordatorios(twilio_client):
    hoy = datetime.now(config.TIMEZONE).date()

    for tipo, dia_semana in REUNIONES:
        fecha_reunion = proxima_fecha_para(dia_semana, desde=hoy)
        dias_hasta = (fecha_reunion - hoy).days

        if dias_hasta == config.REMINDER_DAYS_BEFORE:
            pendientes = db.obtener_asignaciones_pendientes(
                fecha_reunion.isoformat(), tipo, "recordatorio_previo_enviado"
            )
            for asignacion in pendientes:
                _enviar_recordatorio(twilio_client, asignacion, "previo")
                db.marcar_recordatorio_enviado(asignacion["id"], "recordatorio_previo_enviado")

        if dias_hasta == 0:
            pendientes = db.obtener_asignaciones_pendientes(
                fecha_reunion.isoformat(), tipo, "recordatorio_dia_enviado"
            )
            for asignacion in pendientes:
                _enviar_recordatorio(twilio_client, asignacion, "dia")
                db.marcar_recordatorio_enviado(asignacion["id"], "recordatorio_dia_enviado")
