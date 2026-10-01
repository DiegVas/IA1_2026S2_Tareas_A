"""
=============================================================================
INTEGRANTE 1: MÓDULO BASE DE DETECCIÓN CORPORAL (POSE)
CONFIGURACIÓN Y PARÁMETROS GEOMÉTRICOS
=============================================================================
Parámetros de captura, constantes de MediaPipe Pose y umbrales geométricos
para los 4 eventos asignados al Integrante 1:
  1. Persona aparece
  2. Persona desaparece
  3. Persona se acerca
  4. Brazos cruzados

Incluye parámetros de manos, interpretaciones y respuestas del agente.
"""

import os

# =============================================================================
# 1. PARÁMETROS DE CAPTURA LOCAL
# =============================================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_INDEX = 0

# =============================================================================
# 2. CONFIGURACIÓN DE MEDIAPIPE POSE
# =============================================================================
# Modelo Lite seleccionado para reducir el consumo de recursos.
POSE_MODEL_COMPLEXITY = 0
POSE_MIN_DETECTION_CONFIDENCE = 0.5
POSE_MIN_TRACKING_CONFIDENCE = 0.5

# Ruta al modelo local Lite para versiones recientes de MediaPipe (Tasks API).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_LITE_PATH = os.path.join(
    BASE_DIR,
    "models",
    "pose_landmarker_lite.task"
)

MODEL_LITE_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/"
    "pose_landmarker_lite.task"
)

# Cantidad de cuadros sin detección para confirmar "Persona desaparece".
DISAPPEAR_TIMEOUT_FRAMES = 8

# Cuadros de retención para "Persona aparece".
# Equivale aproximadamente a 1.5 segundos cuando se ejecuta a 30 FPS.
APPEARANCE_HOLD_FRAMES = 45

# Umbral de distancia euclidiana normalizada entre hombros.
# d = sqrt((x_l - x_r)^2 + (y_l - y_r)^2)
PROXIMITY_SHOULDER_RATIO_MIN = 0.35

# Brazos cruzados: factor de tolerancia del ancho de muñecas respecto a codos.
# dist(muñecas) < factor * dist(codos)
CROSSED_ARMS_RATIO_MAX = 0.65

# =============================================================================
# 4. EVENTOS ASIGNADOS AL INTEGRANTE 1
# =============================================================================
EVENT_PERSONA_APARECE = "Persona aparece"
EVENT_PERSONA_DESAPARECE = "Persona desaparece"
EVENT_PERSONA_SE_ACERCA = "Persona se acerca"
EVENT_BRAZOS_CRUZADOS = "Brazos cruzados"
EVENT_NINGUNO = "En espera"

# Interpretación contextual de cada evento.
EVENT_INTERPRETATIONS = {
    EVENT_PERSONA_APARECE: (
        "Usuario presente: ha ingresado al campo visual."
    ),
    EVENT_PERSONA_DESAPARECE: (
        "Fin de interaccion: el usuario se ha retirado."
    ),
    EVENT_PERSONA_SE_ACERCA: (
        "Proximidad detectada: el usuario esta a corta distancia."
    ),
    EVENT_BRAZOS_CRUZADOS: (
        "Comando definido: reiniciar seleccion."
    ),
    EVENT_NINGUNO: (
        "Monitoreando postura corporal del usuario..."
    ),
}

# =============================================================================
# 5. INTEGRANTE 2: EXTREMIDADES Y MANOS (POSE + HANDS)
# =============================================================================
# Las distancias se calculan en píxeles del frame y se normalizan
# por el ancho de hombros (W_h).

# Visibilidad mínima de un landmark de Pose para usarlo en un gesto.
LIMB_MIN_VISIBILITY = 0.5

# Mano levantada: muñeca por encima de la nariz.
# y_nariz - y_muñeca >= RAISED_HAND_MARGIN * W_h
RAISED_HAND_MARGIN = 0.10

# Señalar: brazo extendido, casi horizontal y con el codo recto.
# |x_muñeca - x_hombro| >= POINT_MIN_EXTENSION * W_h
POINT_MIN_EXTENSION = 1.0

# Ángulo del brazo respecto a la horizontal.
POINT_MAX_TILT_DEG = 30.0

# Ángulo interno del codo (hombro-codo-muñeca).
POINT_MIN_ELBOW_DEG = 140.0

# MediaPipe Hands se ejecuta cuando Pose indica una mano en zona de pulgar.
HANDS_MODEL_COMPLEXITY = 0
HANDS_MAX_NUM = 2
HANDS_MIN_DETECTION_CONFIDENCE = 0.5
HANDS_MIN_TRACKING_CONFIDENCE = 0.5

HAND_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "hand_landmarker.task"
)

HAND_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/"
    "hand_landmarker.task"
)

# Longitud mínima del pulgar respecto al tamaño de palma.
THUMB_MIN_LENGTH_RATIO = 0.55

# Ángulo máximo del pulgar respecto a la vertical.
THUMB_MAX_TILT_DEG = 45.0

# Cuadros consecutivos para confirmar un gesto.
GESTURE_CONFIRM_FRAMES = 3

EVENT_MANO_LEVANTADA = "Mano levantada"
EVENT_SENALAR_IZQUIERDA = "Senalar izquierda"
EVENT_SENALAR_DERECHA = "Senalar derecha"
EVENT_PULGAR_ARRIBA = "Pulgar arriba"
EVENT_PULGAR_ABAJO = "Pulgar abajo"

EVENT_INTERPRETATIONS.update({
    EVENT_MANO_LEVANTADA: "Saludo",
    EVENT_SENALAR_IZQUIERDA: "Direccion",
    EVENT_SENALAR_DERECHA: "Direccion",
    EVENT_PULGAR_ARRIBA: "Aprobacion",
    EVENT_PULGAR_ABAJO: "Rechazo",
})

# =============================================================================
# 6. RESPUESTAS PARA EL HUD Y EL ROBOT VIRTUAL 2D
# =============================================================================
# Incluye los nueve eventos y el estado de espera.
# Para este avance, brazos cruzados ejecuta el comando local
# de reiniciar la selección.

EVENT_RESPONSES = {
    EVENT_MANO_LEVANTADA: "Responder",
    EVENT_SENALAR_IZQUIERDA: "Mostrar opcion izquierda",
    EVENT_SENALAR_DERECHA: "Mostrar opcion derecha",
    EVENT_PULGAR_ARRIBA: "Confirmar",
    EVENT_PULGAR_ABAJO: "Cambiar respuesta",
}

EVENT_RESPONSES.update({
    EVENT_PERSONA_APARECE: "Saludar",
    EVENT_PERSONA_DESAPARECE: "Despedirse",
    EVENT_PERSONA_SE_ACERCA: "Activar interaccion",
    EVENT_BRAZOS_CRUZADOS: "Ejecutar accion: reiniciar seleccion",
    EVENT_NINGUNO: "Esperar una nueva interaccion",
})