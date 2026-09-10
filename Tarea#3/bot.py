import os
import sys
import time
import random
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests
from dotenv import load_dotenv

# Asegurar compatibilidad UTF-8 en consolas Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token de Telegram desde las variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "tu_token_aqui":
    print("❌ ERROR: TELEGRAM_TOKEN no configurado.")
    print("👉 Por favor crea un archivo .env en esta carpeta con el formato:")
    print("   TELEGRAM_TOKEN=tu_token_obtenido_de_botfather")
    sys.exit(1)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Datos del grupo e integrantes
INTEGRANTES = [
    {"nombre": "Jemima Chavajay", "carnet": "201801521"},
    {"nombre": "Pablo Schaart", "carnet": "201800951"},
    {"nombre": "Diego Vasquez", "carnet": "202300638"},
    {"nombre": "Jencer Hernández", "carnet": "202002141"},
    {"nombre": "Victor Abdiel Lux Juracán", "carnet": "201403946"},
]

INFO_CONTACTO = (
    "📬 <b>Información de Contacto del Grupo:</b>\n\n"
    "👤 <b>Diego Vásquez:</b> Alejandrovasq0803@gmail.com\n"
    "👤 <b>Jemima Chavajay:</b> jemima.chavajay@gmail.com\n"
    "👤 <b>Pablo Schaart:</b> pablo.schaart@gmail.com\n"
    "👤 <b>Jencer Hernández:</b> jencer.hernandez@gmail.com\n\n"
    "🌐 <b>Repositorio GitHub:</b>\n"
    "https://github.com/DiegVas/IA1_2026S2_Tareas_A\n\n"
    "💬 <i>Puedes contactar al equipo a través de este bot o los correos correspondientes.</i>"
)

# Factores de conversión de longitud (base: metros)
FACTORES_CONVERSION = {
    "cm": 0.01,
    "m": 1.0,
    "km": 1000.0,
    "mi": 1609.344,
    "ft": 0.3048,
}


def formatear_numero(valor: float) -> str:
    """Devuelve un número sin decimales innecesarios si es entero."""
    if valor.is_integer():
        return str(int(valor))
    return f"{valor:.4f}".rstrip("0").rstrip(".")


# ==========================================
# CLIENTE HTTP CONTRA LA API DE TELEGRAM
# (sin librerías de Telegram, solo "requests")
# ==========================================
def enviar_mensaje(chat_id, texto, reply_markup=None):
    """Envía un mensaje de texto a un chat usando el endpoint sendMessage."""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Error al enviar mensaje: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as exc:
        print(f"⚠️ Excepción al enviar mensaje: {exc}")


def responder_callback(callback_query_id, texto=None):
    """Confirma la recepción de un botón presionado (quita el 'reloj' del botón)."""
    url = f"{BASE_URL}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if texto:
        payload["text"] = texto

    try:
        requests.post(url, json=payload, timeout=15)
    except requests.exceptions.RequestException as exc:
        print(f"⚠️ Excepción al responder callback: {exc}")


def obtener_actualizaciones(offset=None):
    """Obtiene mensajes/eventos nuevos mediante long polling (getUpdates)."""
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 20}
    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=25)
    except requests.exceptions.RequestException as exc:
        print(f"⚠️ Excepción al obtener actualizaciones: {exc}")
        return []

    if response.status_code != 200:
        print(f"⚠️ Error al obtener actualizaciones: {response.status_code} {response.text}")
        return []

    return response.json().get("result", [])


def construir_teclado_menu():
    """Construye el menú interactivo con botones inline (JSON crudo de la API)."""
    return {
        "inline_keyboard": [
            [
                {"text": "👋 Saludo (/hola)", "callback_data": "cmd_hola"},
                {"text": "⏰ Fecha y Hora (/hora)", "callback_data": "cmd_hora"},
            ],
            [
                {"text": "👥 Integrantes (/integrantes)", "callback_data": "cmd_integrantes"},
                {"text": "📬 Contacto (/contacto)", "callback_data": "cmd_contacto"},
            ],
            [
                {"text": "🧮 Calculadora (/calcular)", "callback_data": "info_calcular"},
                {"text": "🔢 Multiplicar (/tabla)", "callback_data": "info_tabla"},
            ],
            [
                {"text": "📏 Conversor (/convertir)", "callback_data": "info_convertir"},
                {"text": "🎲 Aleatorio (/aleatorio)", "callback_data": "info_aleatorio"},
            ],
            [
                {"text": "ℹ️ Lista de Comandos (/ayuda)", "callback_data": "cmd_ayuda"},
            ],
        ]
    }


def texto_ayuda():
    return (
        "📖 <b>Guía de Comandos Disponibles:</b>\n\n"
        "🔹 <code>/hola</code> : Saluda al usuario utilizando su nombre de Telegram.\n"
        "🔹 <code>/hora</code> : Muestra la fecha y hora actual generada dinámicamente.\n"
        "🔹 <code>/contacto</code> : Muestra los canales de contacto del grupo.\n"
        "🔹 <code>/integrantes</code> : Despliega los nombres y carnets del equipo.\n"
        "🔹 <code>/menu</code> : Abre el menú interactivo con botones.\n"
        "🔹 <code>/ayuda</code> : Muestra esta guía de ayuda.\n\n"
        "<b>Comandos con Parámetros:</b>\n"
        "🔹 <code>/calcular &lt;num1&gt; &lt;op&gt; &lt;num2&gt;</code>\n"
        "   <i>Operaciones (+, -, *, /). Ej:</i> <code>/calcular 15 * 4</code>\n\n"
        "🔹 <code>/tabla &lt;numero&gt;</code>\n"
        "   <i>Muestra la tabla del 1 al 10. Ej:</i> <code>/tabla 7</code>\n\n"
        "🔹 <code>/convertir &lt;cantidad&gt; &lt;origen&gt; &lt;destino&gt;</code>\n"
        "   <i>Convierte unidades (cm, m, km, mi, ft). Ej:</i> <code>/convertir 100 cm m</code>\n\n"
        "🔹 <code>/aleatorio &lt;min&gt; &lt;max&gt;</code>\n"
        "   <i>Genera un entero entre min y max. Ej:</i> <code>/aleatorio 1 100</code>"
    )


def obtener_fecha_hora():
    try:
        tz = ZoneInfo("America/Guatemala")
        ahora = datetime.now(tz)
    except ZoneInfoNotFoundError:
        ahora = datetime.now()

    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%I:%M:%S %p")
    dia_nombre = dias_es.get(ahora.strftime("%A"), ahora.strftime("%A"))
    return fecha_str, hora_str, dia_nombre


# ==========================================
# COMANDO: /hola
# ==========================================
def cmd_hola(chat_id, nombre, apellido):
    nombre_completo = f"{nombre}{(' ' + apellido) if apellido else ''}"
    enviar_mensaje(chat_id, f"👋 ¡Hola, <b>{nombre_completo}</b>! Espero que estés teniendo un excelente día.")


# ==========================================
# COMANDO: /hora
# ==========================================
def cmd_hora(chat_id):
    fecha_str, hora_str, dia_nombre = obtener_fecha_hora()
    respuesta = (
        "⏰ <b>Fecha y Hora Actual (Dinámica):</b>\n\n"
        f"📅 <b>Fecha:</b> {dia_nombre}, {fecha_str}\n"
        f"🕒 <b>Hora:</b> {hora_str}\n"
        "🌐 <b>Zona horaria:</b> America/Guatemala (UTC-6)"
    )
    enviar_mensaje(chat_id, respuesta)


# ==========================================
# COMANDO: /contacto
# ==========================================
def cmd_contacto(chat_id):
    enviar_mensaje(chat_id, INFO_CONTACTO)


# ==========================================
# COMANDO: /integrantes
# ==========================================
def cmd_integrantes(chat_id):
    texto = "👥 <b>Integrantes del Grupo de Trabajo:</b>\n\n"
    for i, integrante in enumerate(INTEGRANTES, 1):
        texto += (
            f"<b>{i}. {integrante['nombre']}</b>\n"
            f"   • Carnet: <code>{integrante['carnet']}</code>\n\n"
        )
    enviar_mensaje(chat_id, texto)


# ==========================================
# COMANDO: /ayuda
# ==========================================
def cmd_ayuda(chat_id):
    enviar_mensaje(chat_id, texto_ayuda())


# ==========================================
# COMANDO: /start y /menu
# ==========================================
def cmd_start(chat_id, nombre):
    texto = (
        f"🤖 <b>¡Hola, {nombre}!</b>\n\n"
        "Bienvenido al bot interactivo de <b>Inteligencia Artificial 1 (USAC)</b>.\n"
        "Selecciona una opción del menú interactivo o utiliza los comandos directamente:"
    )
    enviar_mensaje(chat_id, texto, reply_markup=construir_teclado_menu())


def cmd_menu(chat_id):
    texto = "📋 <b>Menú Interactivo de Opciones:</b>\nPresiona cualquiera de los botones para interactuar:"
    enviar_mensaje(chat_id, texto, reply_markup=construir_teclado_menu())


# ==========================================
# COMANDO: /calcular <numero1> <operador> <numero2>
# ==========================================
def cmd_calcular(chat_id, args):
    if len(args) != 3:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error: Parámetros incorrectos o incompletos.</b>\n\n"
            "📌 <b>Formato correcto:</b>\n"
            "<code>/calcular &lt;numero1&gt; &lt;operador&gt; &lt;numero2&gt;</code>\n\n"
            "💡 <b>Ejemplos:</b>\n"
            "• <code>/calcular 25 + 10</code>\n"
            "• <code>/calcular 50 - 15</code>\n"
            "• <code>/calcular 8 * 9</code>\n"
            "• <code>/calcular 100 / 4</code>\n\n"
            "Operadores soportados: <code>+</code>, <code>-</code>, <code>*</code>, <code>x</code>, <code>/</code>"
        )
        return

    n1_str, operador, n2_str = args

    try:
        num1 = float(n1_str)
        num2 = float(n2_str)
    except ValueError:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error:</b> Ambos operandos deben ser números válidos.\n"
            f"Valores ingresados: <code>{n1_str}</code> y <code>{n2_str}</code>."
        )
        return

    operador = operador.lower()

    if operador == "+":
        resultado = num1 + num2
        op_symbol = "+"
    elif operador == "-":
        resultado = num1 - num2
        op_symbol = "-"
    elif operador in ["*", "x"]:
        resultado = num1 * num2
        op_symbol = "×"
    elif operador == "/":
        if num2 == 0:
            enviar_mensaje(
                chat_id,
                "❌ <b>Error matemático:</b> No es posible realizar una división entre cero (0)."
            )
            return
        resultado = num1 / num2
        op_symbol = "÷"
    else:
        enviar_mensaje(
            chat_id,
            f"❌ <b>Error: Operador '{operador}' no reconocido.</b>\n"
            "Los operadores permitidos son: <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>"
        )
        return

    enviar_mensaje(
        chat_id,
        f"🧮 <b>Resultado del cálculo:</b>\n\n"
        f"<code>{formatear_numero(num1)} {op_symbol} {formatear_numero(num2)} = {formatear_numero(resultado)}</code>"
    )


# ==========================================
# COMANDO: /tabla <numero>
# ==========================================
def cmd_tabla(chat_id, args):
    if len(args) != 1:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error: Parámetros incorrectos.</b>\n\n"
            "📌 <b>Formato correcto:</b>\n"
            "<code>/tabla &lt;numero&gt;</code>\n\n"
            "💡 <b>Ejemplo:</b>\n"
            "<code>/tabla 7</code>"
        )
        return

    try:
        numero = float(args[0])
    except ValueError:
        enviar_mensaje(chat_id, f"❌ <b>Error:</b> <code>'{args[0]}'</code> no es un número válido.")
        return

    num_formateado = formatear_numero(numero)
    lineas = [f"🔢 <b>Tabla de multiplicar del {num_formateado} (1 al 10):</b>\n"]

    for i in range(1, 11):
        producto = numero * i
        lineas.append(f"• <code>{num_formateado} × {i:2d} = {formatear_numero(producto)}</code>")

    enviar_mensaje(chat_id, "\n".join(lineas))


# ==========================================
# COMANDO: /convertir <cantidad> <unidad_origen> <unidad_destino>
# ==========================================
def cmd_convertir(chat_id, args):
    if len(args) != 3:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error: Parámetros incorrectos o incompletos.</b>\n\n"
            "📌 <b>Formato correcto:</b>\n"
            "<code>/convertir &lt;cantidad&gt; &lt;unidad_origen&gt; &lt;unidad_destino&gt;</code>\n\n"
            "📏 <b>Unidades disponibles:</b> <code>cm</code>, <code>m</code>, <code>km</code>, <code>mi</code>, <code>ft</code>\n\n"
            "💡 <b>Ejemplos:</b>\n"
            "• <code>/convertir 100 cm m</code>\n"
            "• <code>/convertir 5 km mi</code>\n"
            "• <code>/convertir 10 ft m</code>"
        )
        return

    cant_str, origen, destino = args
    origen = origen.lower()
    destino = destino.lower()

    try:
        cantidad = float(cant_str)
    except ValueError:
        enviar_mensaje(chat_id, f"❌ <b>Error:</b> La cantidad <code>'{cant_str}'</code> debe ser un número válido.")
        return

    unidades_validas = list(FACTORES_CONVERSION.keys())
    if origen not in FACTORES_CONVERSION:
        enviar_mensaje(
            chat_id,
            f"❌ <b>Error:</b> Unidad de origen <code>'{origen}'</code> no soportada.\n"
            f"Unidades válidas: <code>{', '.join(unidades_validas)}</code>"
        )
        return

    if destino not in FACTORES_CONVERSION:
        enviar_mensaje(
            chat_id,
            f"❌ <b>Error:</b> Unidad de destino <code>'{destino}'</code> no soportada.\n"
            f"Unidades válidas: <code>{', '.join(unidades_validas)}</code>"
        )
        return

    metros = cantidad * FACTORES_CONVERSION[origen]
    resultado = metros / FACTORES_CONVERSION[destino]

    enviar_mensaje(
        chat_id,
        "📏 <b>Conversión de Longitud:</b>\n\n"
        f"<b>Entrada:</b> <code>{formatear_numero(cantidad)} {origen}</code>\n"
        f"<b>Resultado:</b> <code>{formatear_numero(resultado)} {destino}</code>"
    )


# ==========================================
# COMANDO: /aleatorio <min> <max>
# ==========================================
def cmd_aleatorio(chat_id, args):
    if len(args) != 2:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error: Parámetros incorrectos o incompletos.</b>\n\n"
            "📌 <b>Formato correcto:</b>\n"
            "<code>/aleatorio &lt;min&gt; &lt;max&gt;</code>\n\n"
            "💡 <b>Ejemplos:</b>\n"
            "• <code>/aleatorio 1 10</code>\n"
            "• <code>/aleatorio 50 100</code>"
        )
        return

    min_str, max_str = args

    try:
        min_val = int(min_str)
        max_val = int(max_str)
    except ValueError:
        enviar_mensaje(
            chat_id,
            "❌ <b>Error:</b> Los valores <code>min</code> y <code>max</code> deben ser números enteros.\n"
            f"Valores ingresados: <code>{min_str}</code> y <code>{max_str}</code>"
        )
        return

    if min_val > max_val:
        enviar_mensaje(
            chat_id,
            f"❌ <b>Error de rango:</b> El valor mínimo (<code>{min_val}</code>) no puede ser mayor que el máximo (<code>{max_val}</code>)."
        )
        return

    numero_generado = random.randint(min_val, max_val)

    enviar_mensaje(
        chat_id,
        "🎲 <b>Generador de Número Aleatorio:</b>\n\n"
        f"• <b>Rango:</b> [<code>{min_val}</code> .. <code>{max_val}</code>]\n"
        f"👉 <b>Número obtenido:</b> <code>{numero_generado}</code>"
    )


# ==========================================
# ENRUTADOR DE MENSAJES DE TEXTO / COMANDOS
# ==========================================
def procesar_mensaje(chat_id, nombre, apellido, texto):
    partes = texto.strip().split()
    if not partes:
        return

    comando = partes[0].lower()
    # En grupos, Telegram puede mandar "/comando@nombre_del_bot"
    if "@" in comando:
        comando = comando.split("@")[0]
    args = partes[1:]

    if comando == "/start":
        cmd_start(chat_id, nombre)
    elif comando == "/menu":
        cmd_menu(chat_id)
    elif comando == "/hola":
        cmd_hola(chat_id, nombre, apellido)
    elif comando == "/hora":
        cmd_hora(chat_id)
    elif comando == "/contacto":
        cmd_contacto(chat_id)
    elif comando == "/integrantes":
        cmd_integrantes(chat_id)
    elif comando == "/ayuda":
        cmd_ayuda(chat_id)
    elif comando == "/calcular":
        cmd_calcular(chat_id, args)
    elif comando == "/tabla":
        cmd_tabla(chat_id, args)
    elif comando == "/convertir":
        cmd_convertir(chat_id, args)
    elif comando == "/aleatorio":
        cmd_aleatorio(chat_id, args)
    elif comando.startswith("/"):
        # MANEJO DE COMANDOS DESCONOCIDOS
        enviar_mensaje(
            chat_id,
            f"❌ <b>Comando no reconocido:</b> <code>{comando}</code>\n\n"
            "El comando ingresado no existe en el bot.\n"
            "👉 Escribe <code>/ayuda</code> para ver los comandos válidos o <code>/menu</code> para el menú interactivo."
        )
    else:
        # MENSAJES DE TEXTO REGULARES QUE NO SON COMANDOS
        enviar_mensaje(
            chat_id,
            "👋 ¡Hola! Para interactuar conmigo utiliza comandos que inicien con <code>/</code>.\n\n"
            "👉 Escribe <code>/menu</code> para ver las opciones disponibles o <code>/ayuda</code> para conocer la sintaxis de cada comando.",
            reply_markup=construir_teclado_menu()
        )


# ==========================================
# ENRUTADOR DE BOTONES INLINE (MENU)
# ==========================================
def procesar_callback(callback_query):
    data = callback_query.get("data", "")
    callback_id = callback_query.get("id")
    mensaje = callback_query.get("message") or {}
    chat_id = mensaje.get("chat", {}).get("id")
    usuario = callback_query.get("from", {})
    nombre = usuario.get("first_name") or "Usuario"

    responder_callback(callback_id)  # Confirmar recepción al cliente Telegram

    if chat_id is None:
        return

    if data == "cmd_hola":
        enviar_mensaje(chat_id, f"👋 ¡Hola, <b>{nombre}</b>! Un gusto saludarte.")
    elif data == "cmd_hora":
        cmd_hora(chat_id)
    elif data == "cmd_integrantes":
        cmd_integrantes(chat_id)
    elif data == "cmd_contacto":
        cmd_contacto(chat_id)
    elif data == "cmd_ayuda":
        cmd_ayuda(chat_id)
    elif data == "info_calcular":
        enviar_mensaje(
            chat_id,
            "🧮 <b>Calculadora interactiva:</b>\n"
            "Escribe tu operación utilizando el comando:\n"
            "<code>/calcular &lt;numero1&gt; &lt;operador&gt; &lt;numero2&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/calcular 45 * 2</code>"
        )
    elif data == "info_tabla":
        enviar_mensaje(
            chat_id,
            "🔢 <b>Tabla de multiplicar:</b>\n"
            "Genera la tabla del 1 al 10 con:\n"
            "<code>/tabla &lt;numero&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/tabla 9</code>"
        )
    elif data == "info_convertir":
        enviar_mensaje(
            chat_id,
            "📏 <b>Conversor de unidades de longitud:</b>\n"
            "Convierte entre <code>cm</code>, <code>m</code>, <code>km</code>, <code>mi</code> y <code>ft</code> con:\n"
            "<code>/convertir &lt;cantidad&gt; &lt;origen&gt; &lt;destino&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/convertir 1500 m km</code>"
        )
    elif data == "info_aleatorio":
        enviar_mensaje(
            chat_id,
            "🎲 <b>Generador de número aleatorio:</b>\n"
            "Genera un entero entre un rango con:\n"
            "<code>/aleatorio &lt;min&gt; &lt;max&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/aleatorio 1 50</code>"
        )


# ==========================================
# BUCLE PRINCIPAL (LONG POLLING MANUAL)
# ==========================================
def iniciar_bot():
    print("🚀 Bot de Telegram iniciado exitosamente.")
    print("🤖 Ignorando mensajes anteriores...")

    offset = None
    actualizaciones_previas = obtener_actualizaciones(offset)
    if actualizaciones_previas:
        offset = actualizaciones_previas[-1]["update_id"] + 1

    print("✅ Esperando mensajes nuevos...")

    while True:
        try:
            actualizaciones = obtener_actualizaciones(offset)

            for actualizacion in actualizaciones:
                offset = actualizacion["update_id"] + 1

                callback_query = actualizacion.get("callback_query")
                if callback_query is not None:
                    procesar_callback(callback_query)
                    continue

                mensaje = actualizacion.get("message") or actualizacion.get("edited_message")
                if mensaje is None:
                    continue  # Ignorar otro tipo de eventos (posts de canal, polls, etc.)

                texto = mensaje.get("text")
                if not texto:
                    continue  # Ignorar fotos, stickers, audios y demás contenido sin texto

                chat_id = mensaje.get("chat", {}).get("id")
                usuario = mensaje.get("from", {})
                nombre = usuario.get("first_name") or "Usuario"
                apellido = usuario.get("last_name") or ""

                procesar_mensaje(chat_id, nombre, apellido, texto)

        except Exception as exc:  # Nunca detener el bot por un error inesperado
            print(f"⚠️ Error inesperado en el bucle principal: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    try:
        iniciar_bot()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente.")
