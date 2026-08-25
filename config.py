import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]

# Número de WhatsApp desde el que escribe el bot, con prefijo whatsapp:
# Ej: whatsapp:+14155238886 (Sandbox) o whatsapp:+503XXXXXXXX (producción)
TWILIO_WHATSAPP_FROM = os.environ["TWILIO_WHATSAPP_FROM"]
if not TWILIO_WHATSAPP_FROM.startswith("whatsapp:"):
    TWILIO_WHATSAPP_FROM = "whatsapp:" + TWILIO_WHATSAPP_FROM

from db import normalizar_telefono  # noqa: E402

ADMIN_PHONES = {
    normalizar_telefono(x)
    for x in os.environ.get("ADMIN_PHONES", "").split(",")
    if x.strip()
}

TIMEZONE = ZoneInfo(os.environ.get("TIMEZONE", "America/Santo_Domingo"))

MIDWEEK_DAY = int(os.environ.get("MIDWEEK_DAY", 2))
MIDWEEK_HOUR = int(os.environ.get("MIDWEEK_HOUR", 19))
MIDWEEK_MINUTE = int(os.environ.get("MIDWEEK_MINUTE", 0))

WEEKEND_DAY = int(os.environ.get("WEEKEND_DAY", 6))
WEEKEND_HOUR = int(os.environ.get("WEEKEND_HOUR", 10))
WEEKEND_MINUTE = int(os.environ.get("WEEKEND_MINUTE", 0))

REMINDER_DAYS_BEFORE = int(os.environ.get("REMINDER_DAYS_BEFORE", 2))

# Content SID (HXxxxx...) de las plantillas de WhatsApp aprobadas por Meta.
# Mientras estén vacías, el bot manda texto libre (solo funciona si la
# persona escribió en las últimas 24h).
CONTENT_SID_PREVIO = os.environ.get("CONTENT_SID_PREVIO") or None
CONTENT_SID_DIA = os.environ.get("CONTENT_SID_DIA") or None

TIPO_LABEL = {
    "entre_semana": "Reunión de entre semana (Vida y Ministerio)",
    "fin_de_semana": "Reunión de fin de semana (Público/Atalaya)",
}
