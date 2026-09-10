# Tarea 03 — Bot Interactivo de Telegram
**Universidad de San Carlos de Guatemala (USAC)**  
**Facultad de Ingeniería — Escuela de Ciencias y Sistemas**  
**Curso:** Inteligencia Artificial 1  
**Semestre:** Segundo Semestre 2026  

---

## 👥 Integrantes del Grupo

| Nombre | Carnet |
| :--- | :---: |
| Jemima Chavajay | 201801521 |
| Pablo Schaart | 201800951 |
| Diego Vasquez | 202300638 |
| Jencer Hernández | 202002141 |
| Victor Abdiel Lux Juracán | 201403946 |

---

## 🔗 Enlace al Bot de Telegram

- **Link directo del bot / chat:** [https://t.me/IA1_G11_Bot](https://t.me/IA1_G11_Bot)
- **Usuario de Telegram:** `@IA1_G11_Bot`

---

## 📖 Descripción del Bot

Este proyecto consiste en un **Bot interactivo de Telegram** desarrollado en **Python puro**, sin utilizar ninguna librería o framework de Telegram (nada de `python-telegram-bot`, `pyTelegramBotAPI`, `aiogram`, etc.). Toda la comunicación con Telegram se implementa a mano mediante peticiones HTTP directas (librería `requests`) contra los endpoints REST de la API de Telegram (`sendMessage`, `getUpdates`, `answerCallbackQuery`), con un bucle propio de *long polling* que administra el `offset` para no reprocesar mensajes antiguos.

El bot permite a los usuarios interactuar a través de comandos con parámetros, acceder a un menú interactivo con botones inline (construidos como JSON crudo de la API), realizar cálculos aritméticos, generar tablas de multiplicar, convertir unidades de longitud, generar números aleatorios y consultar información dinámica de fecha/hora, contacto e integrantes.

El sistema cuenta con validaciones estrictas en cada comando para manejar adecuadamente entradas erróneas, argumentos incompletos y comandos desconocidos sin detener el servicio. Además, el token de autenticación se gestiona de forma segura mediante variables de entorno (`.env`), garantizando que las credenciales no se expongan en el repositorio.

---

## 🛠️ Comandos Implementados y Sintaxis

### 1. Comandos Básicos e Informativos
| Comando | Descripción | Ejemplo de Uso |
| :--- | :--- | :--- |
| `/start` | Inicia la conversación con el bot y despliega el menú interactivo con botones. | `/start` |
| `/hola` | Saluda al usuario de forma personalizada utilizando su nombre de Telegram. | `/hola` |
| `/hora` | Muestra la fecha y hora actual generada dinámicamente en zona horaria local (`America/Guatemala`). | `/hora` |
| `/contacto` | Muestra los canales de contacto de los administradores y enlace al repositorio. | `/contacto` |
| `/integrantes` | Lista los nombres, carnets y porcentajes de trabajo de los integrantes del grupo. | `/integrantes` |
| `/menu` | Despliega un menú interactivo con botones inline de Telegram para acceder a todas las opciones. | `/menu` |
| `/ayuda` | Presenta la lista detallada de comandos disponibles y su forma de invocación. | `/ayuda` |

### 2. Comandos con Parámetros y Operaciones
| Comando | Descripción | Validaciones | Ejemplo de Uso |
| :--- | :--- | :--- | :--- |
| `/calcular <n1> <op> <n2>` | Ejecuta operaciones aritméticas de suma (`+`), resta (`-`), multiplicación (`*`, `x`) y división (`/`). | Valida que sean 3 argumentos, números válidos, operador soportado y previene división entre cero. | `/calcular 45 * 3`<br>`/calcular 100 / 4` |
| `/tabla <numero>` | Genera la tabla de multiplicar del número ingresado del 1 al 10. | Valida argumento único y que el valor sea numérico. | `/tabla 8` |
| `/convertir <cantidad> <origen> <destino>` | Realiza conversiones entre unidades de longitud. Soporta: `cm`, `m`, `km`, `mi` y `ft`. | Valida cantidad numérica positiva y que ambas unidades pertenezcan a la lista soportada. | `/convertir 100 cm m`<br>`/convertir 5 km mi` |
| `/aleatorio <min> <max>` | Genera un número entero aleatorio dentro del rango `[min, max]`. | Valida 2 argumentos enteros y que `min <= max`. | `/aleatorio 1 50` |

### 3. Manejo de Errores y Comandos Inválidos
- **Comandos no existentes:** Si el usuario ingresa un comando no reconocido (ej. `/test`), el bot responde notificando el error e indicando el uso de `/ayuda` o `/menu`.
- **Mensajes de texto planos:** Si el usuario escribe texto regular sin formato de comando, el bot le ofrece ayuda y despliega nuevamente el teclado interactivo.

---

## 📋 Detalle de Aportes de los Integrantes

La planificación, diseño e implementación de la tarea fue dividida equitativamente entre los integrantes:

| Integrante | Carnet | Aportes Realizados |
| :--- | :---: | :--- |
| **Diego Vasquez** | 202300638 | • Configuración inicial del repositorio, entorno virtual y estructura de archivos (`requirements.txt`, `.env.example`, `.gitignore`).<br>• Implementación de comandos básicos (`/start`, `/hola`, `/hora`) con zona horaria dinámica.<br>• Pruebas de integración y despliegue del bot. |
| **Jemima Chavajay** | 201801521 | • Diseño e implementación del menú interactivo mediante botones inline (`InlineKeyboardMarkup`) y manejo de callbacks (`/menu`).<br>• Implementación del comando de información del equipo (`/integrantes`) y canales de soporte (`/contacto`).<br>• Elaboración y revisión de la documentación en `README.md`. |
| **Pablo Schaart** | 201800951 | • Desarrollo de la lógica del comando matemático `/calcular` con manejo de excepciones (división entre cero, operadores válidos).<br>• Implementación del generador de tablas de multiplicar (`/tabla`) y formateo dinámico de salida numérica.<br>• Creación del comando de ayuda (`/ayuda`). |
| **Jencer Hernández** | 202002141 | • Implementación del conversor de unidades de longitud (`/convertir`) con matriz de factores métricos e imperiales (`cm`, `m`, `km`, `mi`, `ft`).<br>• Desarrollo del generador pseudoaleatorio (`/aleatorio`) con validación de rangos enteros.<br>• Manejador global de excepciones y comandos inexistentes. |
| **Victor Abdiel Lux Juracán** | 201403946 | • Pruebas de integración, verificación de comandos interactivos y validación de casos borde.<br>• Apoyo en la documentación y revisión general del bot. |

---

## 🚀 Instrucciones de Instalación y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/DiegVas/IA1_2026S2_Tareas_A.git
cd IA1_2026S2_Tareas_A/Tarea#3
```

### 2. Crear y activar un entorno virtual (opcional pero recomendado)
- **En Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno
Crea un archivo llamado `.env` en la carpeta `Tarea#3` copiando la plantilla:
```bash
cp .env.example .env
```
Abre `.env` y coloca el token proporcionado por [@BotFather](https://t.me/BotFather):
```env
TELEGRAM_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
```

### 5. Ejecutar el bot
```bash
python bot.py
```
Verás en consola:
```text
🚀 Bot de Telegram iniciado exitosamente.
🤖 Esperando mensajes...
```

---

## ☁️ Guía de Despliegue en la Nube (Hosting Gratuito 24/7)

Para cumplir con el requerimiento de disponibilidad durante la evaluación, el bot puede desplegarse en servicios en la nube gratuitos como **Render** o **Railway**:

### Despliegue en Render (Recomendado)
1. Crea una cuenta gratuita en [Render.com](https://render.com/).
2. Haz clic en **New +** y selecciona **Background Worker** (o **Web Service**).
3. Conecta tu repositorio de GitHub `IA1_2026S2_Tareas_A`.
4. Configura los parámetros:
   - **Root Directory:** `Tarea#3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
5. En la sección **Environment Variables**, añade:
   - `TELEGRAM_TOKEN`: *(Pega tu token de BotFather aquí)*
6. Haz clic en **Create Service**. ¡El bot permanecerá en línea automáticamente!
