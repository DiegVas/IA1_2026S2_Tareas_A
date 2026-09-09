import os
import sys
import random
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv
import telebot
from telebot import types

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
    exit(1)

# Inicializar instancia del Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="HTML")

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


def construir_teclado_menu() -> types.InlineKeyboardMarkup:
    """Construye el menú interactivo con botones inline de Telegram."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_hola = types.InlineKeyboardButton("👋 Saludo (/hola)", callback_data="cmd_hola")
    btn_hora = types.InlineKeyboardButton("⏰ Fecha y Hora (/hora)", callback_data="cmd_hora")
    btn_integrantes = types.InlineKeyboardButton("👥 Integrantes (/integrantes)", callback_data="cmd_integrantes")
    btn_contacto = types.InlineKeyboardButton("📬 Contacto (/contacto)", callback_data="cmd_contacto")
    btn_calc = types.InlineKeyboardButton("🧮 Calculadora (/calcular)", callback_data="info_calcular")
    btn_tabla = types.InlineKeyboardButton("🔢 Multiplicar (/tabla)", callback_data="info_tabla")
    btn_conv = types.InlineKeyboardButton("📏 Conversor (/convertir)", callback_data="info_convertir")
    btn_azar = types.InlineKeyboardButton("🎲 Aleatorio (/aleatorio)", callback_data="info_aleatorio")
    btn_ayuda = types.InlineKeyboardButton("ℹ️ Lista de Comandos (/ayuda)", callback_data="cmd_ayuda")

    markup.add(btn_hola, btn_hora)
    markup.add(btn_integrantes, btn_contacto)
    markup.add(btn_calc, btn_tabla)
    markup.add(btn_conv, btn_azar)
    markup.add(btn_ayuda)
    return markup


# ==========================================
# COMANDO: /start y /menu
# ==========================================
@bot.message_handler(commands=["start"])
def cmd_start(message):
    nombre = message.from_user.first_name or "Usuario"
    texto = (
        f"🤖 <b>¡Hola, {nombre}!</b>\n\n"
        "Bienvenido al bot interactivo de <b>Inteligencia Artificial 1 (USAC)</b>.\n"
        "Selecciona una opción del menú interactivo o utiliza los comandos directamente:"
    )
    bot.reply_to(message, texto, reply_markup=construir_teclado_menu())


@bot.message_handler(commands=["menu"])
def cmd_menu(message):
    texto = "📋 <b>Menú Interactivo de Opciones:</b>\nPresiona cualquiera de los botones para interactuar:"
    bot.reply_to(message, texto, reply_markup=construir_teclado_menu())


# ==========================================
# COMANDO: /hola
# ==========================================
@bot.message_handler(commands=["hola"])
def cmd_hola(message):
    nombre = message.from_user.first_name or "Estimado usuario"
    apellido = f" {message.from_user.last_name}" if message.from_user.last_name else ""
    nombre_completo = f"{nombre}{apellido}"
    bot.reply_to(message, f"👋 ¡Hola, <b>{nombre_completo}</b>! Espero que estés teniendo un excelente día.")


# ==========================================
# COMANDO: /hora
# ==========================================
@bot.message_handler(commands=["hora"])
def cmd_hora(message):
    try:
        tz = ZoneInfo("America/Guatemala")
        ahora = datetime.now(tz)
    except ZoneInfoNotFoundError:
        ahora = datetime.now()

    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%I:%M:%S %p")
    dia_str = ahora.strftime("%A")

    dias_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    dia_nombre = dias_es.get(dia_str, dia_str)

    respuesta = (
        "⏰ <b>Fecha y Hora Actual (Dinámica):</b>\n\n"
        f"📅 <b>Fecha:</b> {dia_nombre}, {fecha_str}\n"
        f"🕒 <b>Hora:</b> {hora_str}\n"
        "🌐 <b>Zona horaria:</b> America/Guatemala (UTC-6)"
    )
    bot.reply_to(message, respuesta)


# ==========================================
# COMANDO: /contacto
# ==========================================
@bot.message_handler(commands=["contacto"])
def cmd_contacto(message):
    bot.reply_to(message, INFO_CONTACTO, disable_web_page_preview=True)


# ==========================================
# COMANDO: /integrantes
# ==========================================
@bot.message_handler(commands=["integrantes"])
def cmd_integrantes(message):
    texto = "👥 <b>Integrantes del Grupo de Trabajo:</b>\n\n"
    for i, integrante in enumerate(INTEGRANTES, 1):
        texto += (
            f"<b>{i}. {integrante['nombre']}</b>\n"
            f"   • Carnet: <code>{integrante['carnet']}</code>\n\n"
        )
    bot.reply_to(message, texto)


# ==========================================
# COMANDO: /ayuda
# ==========================================
@bot.message_handler(commands=["ayuda"])
def cmd_ayuda(message):
    texto = (
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
    bot.reply_to(message, texto)


# ==========================================
# COMANDO: /calcular <numero1> <operador> <numero2>
# ==========================================
@bot.message_handler(commands=["calcular"])
def cmd_calcular(message):
    args = message.text.split()[1:]

    if len(args) != 3:
        bot.reply_to(
            message,
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

    # Validar que los operandos sean numéricos
    try:
        num1 = float(n1_str)
        num2 = float(n2_str)
    except ValueError:
        bot.reply_to(
            message,
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
            bot.reply_to(
                message,
                "❌ <b>Error matemático:</b> No es posible realizar una división entre cero (0)."
            )
            return
        resultado = num1 / num2
        op_symbol = "÷"
    else:
        bot.reply_to(
            message,
            f"❌ <b>Error: Operador '{operador}' no reconocido.</b>\n"
            "Los operadores permitidos son: <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>"
        )
        return

    bot.reply_to(
        message,
        f"🧮 <b>Resultado del cálculo:</b>\n\n"
        f"<code>{formatear_numero(num1)} {op_symbol} {formatear_numero(num2)} = {formatear_numero(resultado)}</code>"
    )


# ==========================================
# COMANDO: /tabla <numero>
# ==========================================
@bot.message_handler(commands=["tabla"])
def cmd_tabla(message):
    args = message.text.split()[1:]

    if len(args) != 1:
        bot.reply_to(
            message,
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
        bot.reply_to(
            message,
            f"❌ <b>Error:</b> <code>'{args[0]}'</code> no es un número válido."
        )
        return

    num_formateado = formatear_numero(numero)
    lineas = [f"🔢 <b>Tabla de multiplicar del {num_formateado} (1 al 10):</b>\n"]

    for i in range(1, 11):
        producto = numero * i
        lineas.append(f"• <code>{num_formateado} × {i:2d} = {formatear_numero(producto)}</code>")

    bot.reply_to(message, "\n".join(lineas))


# ==========================================
# COMANDO: /convertir <cantidad> <unidad_origen> <unidad_destino>
# ==========================================
@bot.message_handler(commands=["convertir"])
def cmd_convertir(message):
    args = message.text.split()[1:]

    if len(args) != 3:
        bot.reply_to(
            message,
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

    # Validar cantidad numérica
    try:
        cantidad = float(cant_str)
    except ValueError:
        bot.reply_to(
            message,
            f"❌ <b>Error:</b> La cantidad <code>'{cant_str}'</code> debe ser un número válido."
        )
        return

    # Validar unidades soportadas
    unidades_validas = list(FACTORES_CONVERSION.keys())
    if origen not in FACTORES_CONVERSION:
        bot.reply_to(
            message,
            f"❌ <b>Error:</b> Unidad de origen <code>'{origen}'</code> no soportada.\n"
            f"Unidades válidas: <code>{', '.join(unidades_validas)}</code>"
        )
        return

    if destino not in FACTORES_CONVERSION:
        bot.reply_to(
            message,
            f"❌ <b>Error:</b> Unidad de destino <code>'{destino}'</code> no soportada.\n"
            f"Unidades válidas: <code>{', '.join(unidades_validas)}</code>"
        )
        return

    # Realizar conversión a través de la unidad base (metro)
    metros = cantidad * FACTORES_CONVERSION[origen]
    resultado = metros / FACTORES_CONVERSION[destino]

    bot.reply_to(
        message,
        "📏 <b>Conversión de Longitud:</b>\n\n"
        f"<b>Entrada:</b> <code>{formatear_numero(cantidad)} {origen}</code>\n"
        f"<b>Resultado:</b> <code>{formatear_numero(resultado)} {destino}</code>"
    )


# ==========================================
# COMANDO: /aleatorio <min> <max>
# ==========================================
@bot.message_handler(commands=["aleatorio"])
def cmd_aleatorio(message):
    args = message.text.split()[1:]

    if len(args) != 2:
        bot.reply_to(
            message,
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
        bot.reply_to(
            message,
            "❌ <b>Error:</b> Los valores <code>min</code> y <code>max</code> deben ser números enteros.\n"
            f"Valores ingresados: <code>{min_str}</code> y <code>{max_str}</code>"
        )
        return

    if min_val > max_val:
        bot.reply_to(
            message,
            f"❌ <b>Error de rango:</b> El valor mínimo (<code>{min_val}</code>) no puede ser mayor que el máximo (<code>{max_val}</code>)."
        )
        return

    numero_generado = random.randint(min_val, max_val)

    bot.reply_to(
        message,
        "🎲 <b>Generador de Número Aleatorio:</b>\n\n"
        f"• <b>Rango:</b> [<code>{min_val}</code> .. <code>{max_val}</code>]\n"
        f"👉 <b>Número obtenido:</b> <code>{numero_generado}</code>"
    )


# ==========================================
# MANEJADOR DE EVENTOS DE BOTONES INLINE (MENU)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    try:
        bot.answer_callback_query(call.id)  # Confirmar recepción al cliente Telegram
    except Exception:
        pass

    if data == "cmd_hola":
        nombre = call.from_user.first_name or "Usuario"
        bot.send_message(call.message.chat.id, f"👋 ¡Hola, <b>{nombre}</b>! Un gusto saludarte.")
    elif data == "cmd_hora":
        try:
            tz = ZoneInfo("America/Guatemala")
            ahora = datetime.now(tz)
        except ZoneInfoNotFoundError:
            ahora = datetime.now()
        fecha_str = ahora.strftime("%d/%m/%Y")
        hora_str = ahora.strftime("%I:%M:%S %p")
        bot.send_message(
            call.message.chat.id,
            f"⏰ <b>Fecha y Hora Actual:</b>\n📅 {fecha_str} | 🕒 {hora_str}\n🌐 America/Guatemala"
        )
    elif data == "cmd_integrantes":
        texto = "👥 <b>Integrantes del Grupo:</b>\n\n"
        for i, integrante in enumerate(INTEGRANTES, 1):
            texto += f"{i}. <b>{integrante['nombre']}</b> — Carnet: <code>{integrante['carnet']}</code>\n"
        bot.send_message(call.message.chat.id, texto)
    elif data == "cmd_contacto":
        bot.send_message(call.message.chat.id, INFO_CONTACTO, disable_web_page_preview=True)
    elif data == "cmd_ayuda":
        cmd_ayuda(call.message)
    elif data == "info_calcular":
        bot.send_message(
            call.message.chat.id,
            "🧮 <b>Calculadora interactiva:</b>\n"
            "Escribe tu operación utilizando el comando:\n"
            "<code>/calcular &lt;numero1&gt; &lt;operador&gt; &lt;numero2&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/calcular 45 * 2</code>"
        )
    elif data == "info_tabla":
        bot.send_message(
            call.message.chat.id,
            "🔢 <b>Tabla de multiplicar:</b>\n"
            "Genera la tabla del 1 al 10 con:\n"
            "<code>/tabla &lt;numero&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/tabla 9</code>"
        )
    elif data == "info_convertir":
        bot.send_message(
            call.message.chat.id,
            "📏 <b>Conversor de unidades de longitud:</b>\n"
            "Convierte entre <code>cm</code>, <code>m</code>, <code>km</code>, <code>mi</code> y <code>ft</code> con:\n"
            "<code>/convertir &lt;cantidad&gt; &lt;origen&gt; &lt;destino&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/convertir 1500 m km</code>"
        )
    elif data == "info_aleatorio":
        bot.send_message(
            call.message.chat.id,
            "🎲 <b>Generador de número aleatorio:</b>\n"
            "Genera un entero entre un rango con:\n"
            "<code>/aleatorio &lt;min&gt; &lt;max&gt;</code>\n\n"
            "💡 <i>Ejemplo:</i> Copia y envía: <code>/aleatorio 1 50</code>"
        )


# ==========================================
# MANEJO DE COMANDOS DESCONOCIDOS / ENTRADAS INVÁLIDAS
# ==========================================
@bot.message_handler(func=lambda message: message.text and message.text.startswith("/"))
def comando_desconocido(message):
    comando = message.text.split()[0]
    bot.reply_to(
        message,
        f"❌ <b>Comando no reconocido:</b> <code>{comando}</code>\n\n"
        "El comando ingresado no existe en el bot.\n"
        "👉 Escribe <code>/ayuda</code> para ver los comandos válidos o <code>/menu</code> para el menú interactivo."
    )


# Manejo de mensajes de texto regulares que no sean comandos
@bot.message_handler(func=lambda message: True)
def mensaje_no_comando(message):
    bot.reply_to(
        message,
        "👋 ¡Hola! Para interactuar conmigo utiliza comandos que inicien con <code>/</code>.\n\n"
        "👉 Escribe <code>/menu</code> para ver las opciones disponibles o <code>/ayuda</code> para conocer la sintaxis de cada comando.",
        reply_markup=construir_teclado_menu()
    )


# ==========================================
# INICIO DEL SERVICIO (POLLING)
# ==========================================
if __name__ == "__main__":
    print("🚀 Bot de Telegram iniciado exitosamente.")
    print("🤖 Esperando mensajes...")
    # non_stop=True garantiza que ante cualquier fallo transitorio de red el bot no se detenga
    bot.infinity_polling(timeout=20, long_polling_timeout=20)
