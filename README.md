# Bot de recordatorios de la congregación

Bot de Telegram para llevar el programa de las reuniones (entre semana y fin
de semana) y recordarle a cada hermano/hermana su parte antes de la reunión.

## 1. Crear el bot en Telegram

1. Habla con [@BotFather](https://t.me/BotFather) → `/newbot` → guarda el
   token que te da.
2. Averigua tu ID de Telegram con [@userinfobot](https://t.me/userinfobot)
   (para configurarte como administrador).

## 2. Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env`:

- `BOT_TOKEN`: el token de BotFather.
- `ADMIN_IDS`: tu ID (y la de otros administradores), separados por coma.
- `GROUP_CHAT_ID`: opcional, no se usa en esta versión (los recordatorios son
  por mensaje privado).
- `TIMEZONE`, días/horas de reunión, y `REMINDER_DAYS_BEFORE`.

## 3. Ejecutar

```bash
python bot.py
```

Para dejarlo corriendo 24/7 en un VPS, usa `systemd`, `pm2` o `tmux`/`screen`.
Ejemplo con systemd: crea `/etc/systemd/system/bot-congre.service` apuntando
a `venv/bin/python bot.py` con `WorkingDirectory` en esta carpeta, y
`systemctl enable --now bot-congre`.

## 4. Cómo funciona

### Registro de cada persona

Cada hermano/hermana debe:
1. Tener un `@usuario` configurado en Telegram (Ajustes → Nombre de usuario).
2. Escribirle al bot `/start` una vez. Así el bot guarda su ID y puede
   enviarle mensajes privados más adelante.

### Cargar el programa (solo administradores)

En un mensaje al bot (puede ser por privado), escribe el comando y en las
líneas siguientes del mismo mensaje, una asignación por línea:

```
/cargar_semana
Presidente: @juanperez
Oración inicial: @carlosgomez
Tesoros de la Biblia: @juanperez
Perlas escondidas: @pedroramirez
Estudio bíblico de la congregación (conductor): @juanperez
Estudio bíblico de la congregación (lector): @miguelrosa
Oración final: @miguelrosa
```

```
/cargar_finde
Presidente: @juanperez
Discurso público: @pedroramirez
Lector de Atalaya: @miguelrosa
Oración inicial: @carlosgomez
Oración final: @juanperez
```

Por defecto usa la próxima fecha de ese tipo de reunión según `MIDWEEK_DAY` /
`WEEKEND_DAY` en `.env`. Si quieres cargar una fecha específica (por ejemplo
para adelantar varias semanas), agrégala después del comando:

```
/cargar_semana 2026-09-02
Presidente: @juanperez
...
```

Volver a cargar el programa de la misma fecha reemplaza las asignaciones
anteriores.

`/ayuda_admin` muestra este mismo formato dentro del bot.

### Consultas para todos

- `/miparte` — muestra las próximas partes asignadas al que escribe.
- `/programa` — muestra el programa de la próxima reunión de fin de semana.
- `/programa semana` — muestra el programa de la próxima reunión entre semana.

### Recordatorios automáticos

Todos los días a las 8:00 (hora `TIMEZONE`), el bot revisa si hay una
reunión en `REMINDER_DAYS_BEFORE` días o si es el mismo día de una reunión, y
envía por mensaje privado a cada persona con una parte asignada:

- Un recordatorio `REMINDER_DAYS_BEFORE` días antes.
- Un recordatorio la mañana del mismo día de la reunión.

Si la persona no ha hecho `/start` todavía, el bot no puede escribirle y lo
registra en el log del servidor — conviene recordarle que active el bot.

## 5. Estructura del proyecto

```
bot.py            Punto de entrada, registra handlers y el scheduler
config.py         Carga variables de entorno
db.py             Acceso a SQLite (usuarios, reuniones, asignaciones)
dates_util.py     Cálculo de próximas fechas y formato en español
scheduler.py      Job diario que envía los recordatorios
handlers/
  common.py       /start y verificación de admin
  admin.py        /cargar_semana, /cargar_finde, /ayuda_admin
  user.py         /miparte, /programa
```

La base de datos es un único archivo `congregacion.db` (SQLite) que se crea
automáticamente en la carpeta del proyecto la primera vez que corres el bot.
