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
"""

import os

# =============================================================================
# 1. PARÁMETROS DE CAPTURA LOCAL (COMPATIBILIDAD OBLIGATORIA)
# =============================================================================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
CAMERA_INDEX = 0

# =============================================================================
# 2. CONFIGURACIÓN DE MEDIAPIPE POSE (REGLA: MODELO LITE)
# =============================================================================
# model_complexity=0 es OBLIGATORIO para garantizar rendimiento en procesadores ARM
POSE_MODEL_COMPLEXITY = 0
POSE_MIN_DETECTION_CONFIDENCE = 0.5
POSE_MIN_TRACKING_CONFIDENCE = 0.5

# Ruta al modelo local Lite para versiones recientes de MediaPipe (Tasks API)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_LITE_PATH = os.path.join(BASE_DIR, "models", "pose_landmarker_lite.task")
MODEL_LITE_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"

# Cantidad de cuadros sin detección para confirmar "Persona desaparece"
DISAPPEAR_TIMEOUT_FRAMES = 8

# Cuadros de retención para "Persona aparece" (aprox 1.5 seg a 30 FPS para visualización clara)
APPEARANCE_HOLD_FRAMES = 45

# Umbral de distancia euclidiana normalizada entre hombros para "Persona se acerca"
# d = sqrt((x_l - x_r)^2 + (y_l - y_r)^2)
PROXIMITY_SHOULDER_RATIO_MIN = 0.35

# Brazos cruzados: factor de tolerancia del ancho de muñecas respecto a codos
# Las muñecas deben estar más juntas que los codos: dist(muñecas) < factor * dist(codos)
CROSSED_ARMS_RATIO_MAX = 0.65

# =============================================================================
# 4. EVENTOS ASIGNADOS AL INTEGRANTE 1
# =============================================================================
EVENT_PERSONA_APARECE    = "Persona aparece"
EVENT_PERSONA_DESAPARECE = "Persona desaparece"
EVENT_PERSONA_SE_ACERCA  = "Persona se acerca"
EVENT_BRAZOS_CRUZADOS    = "Brazos cruzados"
EVENT_NINGUNO            = "En espera"

# Interpretación contextual de cada evento
EVENT_INTERPRETATIONS = {
    EVENT_PERSONA_APARECE:    "Presencia detectada: el usuario ha ingresado al campo visual.",
    EVENT_PERSONA_DESAPARECE: "Ausencia detectada: el usuario se ha retirado del campo visual.",
    EVENT_PERSONA_SE_ACERCA:  "Proximidad detectada: el usuario se encuentra a corta distancia.",
    EVENT_BRAZOS_CRUZADOS:    "Postura de espera: el usuario mantiene los brazos cruzados sobre el pecho.",
    EVENT_NINGUNO:            "Monitoreando postura corporal del usuario..."
}

# =============================================================================
# 5. INTEGRANTE 2: EXTREMIDADES Y MANOS (POSE + HANDS)
# =============================================================================
# Todas las distancias se miden en píxeles del frame 640x480 y se normalizan
# por el ancho de hombros (W_h), así los umbrales no dependen de la distancia
# del usuario a la cámara.

# Visibilidad mínima de un landmark de Pose para usarlo en un gesto
LIMB_MIN_VISIBILITY = 0.5

# Mano levantada: la muñeca debe quedar por encima de la nariz al menos
# RAISED_HAND_MARGIN * W_h  (y_nariz - y_muñeca >= 0.10 * W_h)
RAISED_HAND_MARGIN = 0.10

# Señalar: brazo extendido, casi horizontal y con el codo recto
# |x_muñeca - x_hombro| >= POINT_MIN_EXTENSION * W_h
POINT_MIN_EXTENSION = 1.0
# Ángulo del antebrazo-brazo respecto a la horizontal <= POINT_MAX_TILT_DEG
POINT_MAX_TILT_DEG = 30.0
# Ángulo interno del codo (hombro-codo-muñeca) >= POINT_MIN_ELBOW_DEG
POINT_MIN_ELBOW_DEG = 140.0

# MediaPipe Hands (se ejecuta SOLO si Pose indica una mano en zona de pulgar)
HANDS_MODEL_COMPLEXITY = 0
HANDS_MAX_NUM = 2
HANDS_MIN_DETECTION_CONFIDENCE = 0.5
HANDS_MIN_TRACKING_CONFIDENCE = 0.5
HAND_MODEL_PATH = os.path.join(BASE_DIR, "models", "hand_landmarker.task")
HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"

# Pulgar: longitud mínima del pulgar (MCP->punta) respecto al tamaño de palma
# (muñeca->MCP medio) y ángulo máximo respecto a la vertical
THUMB_MIN_LENGTH_RATIO = 0.55
THUMB_MAX_TILT_DEG = 45.0

# Persistencia temporal: cuadros consecutivos para confirmar un gesto
GESTURE_CONFIRM_FRAMES = 3

EVENT_MANO_LEVANTADA    = "Mano levantada"
EVENT_SENALAR_IZQUIERDA = "Senalar izquierda"
EVENT_SENALAR_DERECHA   = "Senalar derecha"
EVENT_PULGAR_ARRIBA     = "Pulgar arriba"
EVENT_PULGAR_ABAJO      = "Pulgar abajo"

# Interpretación y respuesta según la tabla del Módulo 1 del enunciado (Proyecto 2)
EVENT_INTERPRETATIONS.update({
    EVENT_MANO_LEVANTADA:    "Saludo",
    EVENT_SENALAR_IZQUIERDA: "Direccion",
    EVENT_SENALAR_DERECHA:   "Direccion",
    EVENT_PULGAR_ARRIBA:     "Aprobacion",
    EVENT_PULGAR_ABAJO:      "Rechazo",
})

EVENT_RESPONSES = {
    EVENT_MANO_LEVANTADA:    "Responder",
    EVENT_SENALAR_IZQUIERDA: "Mostrar opcion izquierda",
    EVENT_SENALAR_DERECHA:   "Mostrar opcion derecha",
    EVENT_PULGAR_ARRIBA:     "Confirmar",
    EVENT_PULGAR_ABAJO:      "Cambiar respuesta",
}
