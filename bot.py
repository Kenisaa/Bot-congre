import logging

from telegram.ext import Application, CommandHandler

import config
import db
from handlers.admin import ayuda_admin, cargar_finde, cargar_semana
from handlers.common import start
from handlers.user import miparte, programa
from scheduler import programar_revision_diaria

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def main():
    db.init_db()

    application = Application.builder().token(config.BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("miparte", miparte))
    application.add_handler(CommandHandler("programa", programa))
    application.add_handler(CommandHandler("cargar_semana", cargar_semana))
    application.add_handler(CommandHandler("cargar_finde", cargar_finde))
    application.add_handler(CommandHandler("ayuda_admin", ayuda_admin))

    programar_revision_diaria(application)

    application.run_polling()


if __name__ == "__main__":
    main()
