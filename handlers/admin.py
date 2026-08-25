import re
from datetime import date

import config
import db
from dates_util import formatear_fecha, proxima_fecha_para

LINEA_RE = re.compile(r"^\s*([^:]+):\s*([\d+][\d\s+()-]{6,})\s*$")

AYUDA_CARGA = (
    "Para cargar el programa, envía un mensaje así (todo junto, cada línea "
    "con Shift+Enter):\n\n"
    "cargar semana\n"
    "Presidente: +50370001111\n"
    "Oración inicial: +50370002222\n"
    "Tesoros de la Biblia: +50370001111\n"
    "Perlas escondidas: +50370003333\n"
    "Estudio bíblico (conductor): +50370001111\n"
    "Estudio bíblico (lector): +50370004444\n"
    "Oración final: +50370004444\n\n"
    "O para el fin de semana:\n\n"
    "cargar finde\n"
    "Presidente: +50370001111\n"
    "Discurso público: +50370003333\n"
    "Lector de Atalaya: +50370004444\n"
    "Micrófono 1: +50370005555\n"
    "Micrófono 2: +50370006666\n"
    "Sonido: +50370007777\n"
    "Plataforma: +50370008888\n"
    "Oración inicial: +50370002222\n"
    "Oración final: +50370001111\n\n"
    "Usa el número completo con código de país (ej. +503 para El Salvador).\n"
    "Si no pones fecha después de 'cargar semana'/'cargar finde', se usa la "
    "próxima reunión de ese tipo. Para una fecha específica:\n"
    "cargar semana 2026-09-03"
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
        rol, telefono = m.group(1).strip(), m.group(2).strip()
        asignaciones.append((rol, telefono))
    return asignaciones, errores


def _cargar(texto: str, tipo: str, dia_default: int) -> str:
    lineas = texto.split("\n")
    primera = lineas[0]
    resto = lineas[1:]

    partes_comando = primera.split()
    fecha_str = partes_comando[2] if len(partes_comando) > 2 else None

    if fecha_str:
        try:
            fecha = date.fromisoformat(fecha_str)
        except ValueError:
            return "Fecha inválida, usa el formato YYYY-MM-DD.\n\n" + AYUDA_CARGA
    else:
        fecha = proxima_fecha_para(dia_default)

    asignaciones, errores = _parse_asignaciones(resto)

    if not asignaciones:
        return "No encontré asignaciones para cargar.\n\n" + AYUDA_CARGA

    reunion_id = db.crear_o_obtener_reunion(fecha.isoformat(), tipo)
    db.limpiar_asignaciones(reunion_id)
    for orden, (rol, telefono) in enumerate(asignaciones):
        db.agregar_asignacion(reunion_id, rol, telefono, orden)
        db.registrar_usuario(telefono)

    resumen = "\n".join(
        f"• {rol}: {db.normalizar_telefono(tel)}" for rol, tel in asignaciones
    )
    mensaje = (
        f"Programa cargado para {config.TIPO_LABEL[tipo]} "
        f"del {formatear_fecha(fecha.isoformat())}:\n\n{resumen}"
    )
    if errores:
        mensaje += "\n\nAtención, hubo líneas ignoradas:\n" + "\n".join(errores)
    return mensaje


def cargar_semana(texto: str) -> str:
    return _cargar(texto, "entre_semana", config.MIDWEEK_DAY)


def cargar_finde(texto: str) -> str:
    return _cargar(texto, "fin_de_semana", config.WEEKEND_DAY)
