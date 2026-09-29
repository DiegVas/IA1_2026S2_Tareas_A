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
