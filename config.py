import os
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]

ADMIN_IDS = {
    int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip()
}

GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID") or None

TIMEZONE = ZoneInfo(os.environ.get("TIMEZONE", "America/Santo_Domingo"))

MIDWEEK_DAY = int(os.environ.get("MIDWEEK_DAY", 2))
MIDWEEK_HOUR = int(os.environ.get("MIDWEEK_HOUR", 19))
MIDWEEK_MINUTE = int(os.environ.get("MIDWEEK_MINUTE", 0))

WEEKEND_DAY = int(os.environ.get("WEEKEND_DAY", 6))
WEEKEND_HOUR = int(os.environ.get("WEEKEND_HOUR", 10))
WEEKEND_MINUTE = int(os.environ.get("WEEKEND_MINUTE", 0))

REMINDER_DAYS_BEFORE = int(os.environ.get("REMINDER_DAYS_BEFORE", 2))

TIPO_LABEL = {
    "entre_semana": "Reunión de entre semana (Vida y Ministerio)",
    "fin_de_semana": "Reunión de fin de semana (Público/Atalaya)",
}
