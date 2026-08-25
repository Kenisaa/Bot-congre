from telegram import Update
from telegram.ext import ContextTypes

import config
import db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.registrar_usuario(user.id, user.username, user.full_name)
    if user.username:
        texto = (
            f"¡Hola {user.first_name}! Quedaste registrado como @{user.username}.\n\n"
            "Cuando el administrador te asigne una parte usando tu @usuario, "
            "te avisaré por aquí antes de la reunión.\n\n"
            "Comandos disponibles:\n"
            "/miparte - ver tus próximas partes\n"
            "/programa - ver el programa de la próxima reunión"
        )
    else:
        texto = (
            f"¡Hola {user.first_name}! No tienes un @username configurado en Telegram.\n"
            "Debes crear uno en Ajustes > Nombre de usuario para que el bot "
            "pueda identificarte y enviarte recordatorios."
        )
    await update.message.reply_text(texto)


def es_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS
