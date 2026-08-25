# Bot de recordatorios de la congregación (WhatsApp / Twilio)

Bot de WhatsApp para llevar el programa de las reuniones (entre semana y fin
de semana) y recordarle a cada hermano/hermana su parte antes de la reunión.

Funciona con la API de WhatsApp de Twilio: Twilio te avisa por un webhook
HTTP cada vez que alguien le escribe al número del bot.

## 1. Cuenta de Twilio y WhatsApp Sandbox (pruebas)

1. En [console.twilio.com](https://console.twilio.com), ve a
   **Messaging → Try it out → Send a WhatsApp message** para activar el
   Sandbox de pruebas (gratis, número compartido tipo `+1 415 523 8886`).
2. Cada persona que vaya a usar el bot debe enviarle **una vez** el código
   `join palabra-clave` que te dio el Sandbox, desde su propio WhatsApp.
   Esto autoriza que el bot le pueda escribir (reemplaza el `/start` de
   otros bots).
3. Anota tu **Account SID** y **Auth Token** (Console → parte superior,
   "Account Info").

Cuando quieras pasar a producción con tu propio número de WhatsApp Business
verificado, solo cambias la variable `TWILIO_WHATSAPP_FROM` — el código no
cambia.

## 2. Instalación local (opcional, para probar antes de subir)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` con tus credenciales de Twilio y la configuración de reuniones
(ver comentarios dentro del archivo).

```bash
python app.py
```

Para que Twilio te pueda llamar desde internet mientras pruebas localmente,
usa una herramienta como `ngrok`:

```bash
ngrok http 5000
```

Y configura esa URL (`https://xxxx.ngrok.app/webhook`) en el Sandbox de
Twilio (Messaging → Sandbox Settings → "WHEN A MESSAGE COMES IN").

## 3. Desplegar en Railway

1. Sube este proyecto a un repo de GitHub y conéctalo en Railway
   (**New Project → Deploy from GitHub repo**).
2. En **Variables**, agrega:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_FROM` (ej. `whatsapp:+14155238886` para el Sandbox)
   - `ADMIN_PHONES` (tu número con código de país, ej. `+50370001111`)
   - `TIMEZONE` (ej. `America/El_Salvador`)
   - `MIDWEEK_DAY`, `MIDWEEK_HOUR`, `MIDWEEK_MINUTE`
   - `WEEKEND_DAY`, `WEEKEND_HOUR`, `WEEKEND_MINUTE`
   - `REMINDER_DAYS_BEFORE`
   - `DB_PATH=/data/congregacion.db`
3. En **Volumes**, crea uno con mount path `/data` (para que el programa
   cargado no se pierda en cada deploy).
4. Railway detecta el `Procfile` (`web: gunicorn app:app ...`) y expone una
   URL pública tipo `https://tu-proyecto.up.railway.app`.
5. En Twilio → Sandbox Settings (o tu número de producción) → **"WHEN A
   MESSAGE COMES IN"**, pega: `https://tu-proyecto.up.railway.app/webhook`
   con método `HTTP POST`.

## 4. Cómo funciona

### Registro de cada persona

Cada hermano/hermana debe:
1. Unirse al Sandbox una vez (paso 1.2), o —en producción— simplemente
   escribirle al número del bot.
2. Con eso el bot ya guarda su número y puede escribirle recordatorios.

### Cargar el programa (solo administradores)

Los administradores son los números listados en `ADMIN_PHONES`. Se carga
enviando un mensaje de WhatsApp que empieza con el comando y, en las líneas
siguientes del mismo mensaje (usa el salto de línea normal del teclado de
WhatsApp), una asignación por línea con `Rol: +numero`:

```
cargar finde
Presidente: +50370001111
Discurso público: +50370003333
Lector de Atalaya: +50370004444
Micrófono 1: +50370005555
Micrófono 2: +50370006666
Sonido: +50370007777
Plataforma: +50370008888
Oración inicial: +50370002222
Oración final: +50370001111
```

```
cargar semana
Presidente: +50370001111
Oración inicial: +50370002222
Tesoros de la Biblia: +50370001111
Perlas escondidas: +50370003333
Estudio bíblico (conductor): +50370001111
Estudio bíblico (lector): +50370004444
Oración final: +50370004444
```

Usa siempre el número completo con código de país. Por defecto toma la
próxima fecha de ese tipo de reunión según `MIDWEEK_DAY`/`WEEKEND_DAY`. Para
una fecha específica:

```
cargar semana 2026-09-03
Presidente: +50370001111
...
```

Volver a cargar el programa de la misma fecha reemplaza las asignaciones
anteriores. Escribe `ayuda` (siendo admin) para ver este formato desde el
propio WhatsApp.

### Consultas para todos

- `miparte` — muestra las próximas partes asignadas al número que escribe.
- `programa` — programa de la próxima reunión de fin de semana.
- `programa semana` — programa de la próxima reunión entre semana.

### Recordatorios automáticos

Todos los días a las 8:00 (hora `TIMEZONE`), el bot revisa si hay una
reunión en `REMINDER_DAYS_BEFORE` días o si es el mismo día de una reunión,
y envía por WhatsApp a cada número con una parte asignada:

- Un recordatorio `REMINDER_DAYS_BEFORE` días antes.
- Un recordatorio la mañana del mismo día de la reunión.

**Importante sobre plantillas de WhatsApp:** mientras uses el Sandbox de
pruebas, los recordatorios funcionan como mensajes libres. Al pasar a un
número de WhatsApp Business en producción, Meta exige que cualquier mensaje
enviado fuera de una ventana de 24 horas desde el último mensaje del usuario
use una **plantilla pre-aprobada**. Si notas que los recordatorios dejan de
llegar en producción, hay que registrar una plantilla en Twilio/Meta para
ese texto (toma de horas a 1-2 días la aprobación).

## 5. Estructura del proyecto

```
app.py             Servidor Flask: webhook de Twilio, rutas, scheduler
config.py          Carga variables de entorno
db.py              Acceso a SQLite (usuarios, reuniones, asignaciones)
dates_util.py       Cálculo de próximas fechas y formato en español
scheduler.py        Lógica de qué recordatorios tocan enviar hoy
handlers/
  common.py         Verificación de admin y texto de bienvenida
  admin.py           Parseo y carga de "cargar semana" / "cargar finde"
  user.py             "miparte", "programa"
```

La base de datos es un único archivo `congregacion.db` (SQLite) que se crea
automáticamente en la carpeta del proyecto (o en `DB_PATH`) la primera vez
que corre el servidor.
