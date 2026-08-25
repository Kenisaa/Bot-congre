import logging
from datetime import datetime, time

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

import config
import db
from dates_util import formatear_fecha
from handlers.admin import cargar_finde, cargar_semana, AYUDA_CARGA
from handlers.common import es_admin, texto_bienvenida
from handlers.user import miparte, programa
from scheduler import revisar_recordatorios

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

db.init_db()

twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
validator = RequestValidator(config.TWILIO_AUTH_TOKEN)

app = Flask(__name__)


def procesar_mensaje(telefono: str, nombre: str, texto: str) -> str:
    texto_norm = texto.strip()
    texto_lower = texto_norm.lower()
    primera_linea = texto_lower.split("\n", 1)[0].strip()

    ya_existia = db.buscar_usuario(telefono) is not None
    db.registrar_usuario(telefono, nombre)

    if primera_linea in ("hola", "start", "inicio", "menu", "menú") or not ya_existia:
        return texto_bienvenida(nombre)

    if primera_linea == "miparte":
        return miparte(telefono)

    if primera_linea.startswith("programa"):
        argumentos = primera_linea.split()[1:]
        return programa(argumentos)

    if primera_linea.startswith("cargar semana") or primera_linea.startswith("cargar_semana"):
        if not es_admin(telefono):
            return "Solo un administrador puede cargar el programa."
        return cargar_semana(texto_norm)

    if primera_linea.startswith("cargar finde") or primera_linea.startswith("cargar_finde"):
        if not es_admin(telefono):
            return "Solo un administrador puede cargar el programa."
        return cargar_finde(texto_norm)

    if primera_linea in ("ayuda", "ayuda admin", "help"):
        if es_admin(telefono):
            return AYUDA_CARGA
        return texto_bienvenida(nombre)

    return (
        "No entendí ese mensaje. Escribe *ayuda* para ver los comandos "
        "disponibles, o *miparte* / *programa*."
    )


@app.post("/webhook")
def webhook():
    url = request.url
    signature = request.headers.get("X-Twilio-Signature", "")
    if not validator.validate(url, request.form, signature):
        logger.warning("Firma de Twilio inválida, request rechazado")
        return ("Forbidden", 403)

    telefono = request.form.get("From", "")
    nombre = request.form.get("ProfileName", "") or "hermano/a"
    texto = request.form.get("Body", "")

    respuesta_texto = procesar_mensaje(telefono, nombre, texto)

    respuesta = MessagingResponse()
    respuesta.message(respuesta_texto)
    return str(respuesta), 200, {"Content-Type": "text/xml"}


@app.get("/")
def health():
    return "Bot de recordatorios activo", 200


def job_recordatorios():
    revisar_recordatorios(twilio_client)


scheduler = BackgroundScheduler(timezone=config.TIMEZONE)
scheduler.add_job(
    job_recordatorios,
    "cron",
    hour=8,
    minute=0,
    id="revision_diaria_recordatorios",
)
scheduler.start()


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
