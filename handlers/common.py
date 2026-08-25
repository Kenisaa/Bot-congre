import config


def es_admin(telefono: str) -> bool:
    from db import normalizar_telefono

    return normalizar_telefono(telefono) in config.ADMIN_PHONES


def texto_bienvenida(nombre: str) -> str:
    return (
        f"¡Hola {nombre}! Quedaste registrado en el bot de recordatorios "
        "de la congregación.\n\n"
        "Cuando el administrador te asigne una parte, te avisaré por aquí "
        "antes de la reunión.\n\n"
        "Comandos disponibles:\n"
        "*miparte* - ver tus próximas partes\n"
        "*programa* - ver el programa de la próxima reunión de fin de semana\n"
        "*programa semana* - ver el programa de la próxima reunión entre semana"
    )
