"""
=============================================================================
INTEGRANTE 1: MÓDULO BASE DE DETECCIÓN CORPORAL (POSE)
CLASE MEDIAPIPE POSE Y LÓGICA GEOMÉTRICA MULTIVERSION
=============================================================================
Soporta tanto la API clásica (mp.solutions.pose en Raspberry Pi OS / Python <= 3.11)
como la API moderna (mediapipe.tasks.vision.PoseLandmarker en Python 3.12+ / PC).

Responsabilidades del Integrante 1:
  - Desarrollar en local la clase de MediaPipe Pose (model_complexity=0 Lite).
  - Implementar la lógica para:
      1. Persona aparece
      2. Persona desaparece
      3. Persona se acerca
      4. Brazos cruzados
  - Documentar la formulación geométrica y umbrales utilizados para el informe.
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import urllib.request
import config

class PoseDetector:
    """
    Detector y analizador geométrico de postura corporal.
    Garantiza compatibilidad dual:
      - mp.solutions.pose (Raspberry Pi OS / Debian)
      - mediapipe.tasks.vision (PC / Python 3.12+)
    """

    def __init__(self,
                 model_complexity=config.POSE_MODEL_COMPLEXITY,
                 min_detection_confidence=config.POSE_MIN_DETECTION_CONFIDENCE,
                 min_tracking_confidence=config.POSE_MIN_TRACKING_CONFIDENCE):
        """
        Detecta el backend disponible e inicializa el modelo Lite correspondiente.
        """
        self.person_present = False
        self.consecutive_misses = 0
        self.appearance_counter = 0
        self.current_landmarks = None
        self.last_shoulder_distance = 0.0

        # Conexiones anatómicas principales para dibujado del esqueleto
        self.POSE_CONNECTIONS = [
            (11, 12), (11, 13), (13, 15), # Brazo izquierdo
            (12, 14), (14, 16),           # Brazo derecho
            (11, 23), (12, 24), (23, 24), # Torso
            (0, 1), (1, 2), (2, 3), (3, 7), # Cabeza izquierda
            (0, 4), (4, 5), (5, 6), (6, 8), # Cabeza derecha
            (9, 10), (0, 11), (0, 12)     # Cuello
        ]

        # Verificar si la versión de MediaPipe cuenta con 'solutions' (API Clásica)
        if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'pose'):
            self.backend = "solutions"
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                model_complexity=model_complexity,
                enable_segmentation=False,
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence
            )
            print("[PoseDetector] Backend activo: MediaPipe Solutions (Clásico RPi)")
        else:
            self.backend = "tasks"
            self._init_tasks_backend(min_detection_confidence)
            print("[PoseDetector] Backend activo: MediaPipe Tasks Lite (Moderno PC)")

    def _init_tasks_backend(self, min_confidence):
        """Inicializa MediaPipe Tasks con el modelo local pose_landmarker_lite."""
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python import BaseOptions

        model_path = config.MODEL_LITE_PATH
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            print(f"[PoseDetector] Descargando modelo Lite desde {config.MODEL_LITE_URL}...")
            urllib.request.urlretrieve(config.MODEL_LITE_URL, model_path)
            print(f"[PoseDetector] Modelo descargado en: {model_path}")

        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE,
            min_pose_detection_confidence=min_confidence,
            min_pose_presence_confidence=min_confidence,
            min_tracking_confidence=min_confidence,
            num_poses=1
        )
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def process(self, frame_bgr):
        """
        Procesa el cuadro de video y extrae los landmarks corporales.
        Retorna (results, detected_event, shoulder_distance)
        """
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        landmarks = None
        if self.backend == "solutions":
            frame_rgb.flags.writeable = False
            results = self.pose.process(frame_rgb)
            frame_rgb.flags.writeable = True
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            result = self.landmarker.detect(mp_image)
            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = result.pose_landmarks[0]

        self.current_landmarks = landmarks
        detected_event = self._evaluate_events(landmarks)

        return landmarks, detected_event, self.last_shoulder_distance

    def _evaluate_events(self, landmarks):
        """
        Evalúa los 4 eventos geométricos corporales:
          1. Persona aparece
          2. Persona desaparece
          3. Persona se acerca
          4. Brazos cruzados
        """
        # ---------------------------------------------------------------------
        # 1. AUSENCIA / DESAPARICIÓN DE LA PERSONA
        # ---------------------------------------------------------------------
        if landmarks is None or len(landmarks) == 0:
            self.consecutive_misses += 1
            self.appearance_counter = 0

            # Si ya transcurrió el timeout de ausencia, se declara y sostiene "Persona desaparece"
            if self.consecutive_misses >= config.DISAPPEAR_TIMEOUT_FRAMES:
                self.person_present = False
                self.last_shoulder_distance = 0.0
                return config.EVENT_PERSONA_DESAPARECE

            # Si ya estaba ausente previamente, mantener el estado de desaparición
            if not self.person_present and self.consecutive_misses >= 3:
                return config.EVENT_PERSONA_DESAPARECE

            return config.EVENT_NINGUNO

        # ---------------------------------------------------------------------
        # 2. CUANDO HAY LANDMARKS DETECTADOS
        # ---------------------------------------------------------------------
        self.consecutive_misses = 0

        # Transición: la persona acaba de aparecer en el campo visual
        if not self.person_present:
            self.person_present = True
            self.appearance_counter = config.APPEARANCE_HOLD_FRAMES
            return config.EVENT_PERSONA_APARECE

        # Landmarks clave (índices estándar de MediaPipe Pose)
        l_shoulder = landmarks[11]
        r_shoulder = landmarks[12]
        l_elbow    = landmarks[13]
        r_elbow    = landmarks[14]
        l_wrist    = landmarks[15]
        r_wrist    = landmarks[16]
        l_hip      = landmarks[23]
        r_hip      = landmarks[24]

        # Calcular distancia entre hombros (métrica de proximidad)
        dx = l_shoulder.x - r_shoulder.x
        dy = l_shoulder.y - r_shoulder.y
        self.last_shoulder_distance = float(np.sqrt(dx * dx + dy * dy))

        # ---------------------------------------------------------------------
        # 3. EVALUACIÓN DE POSTURAS ACTIVAS (Prioridad sobre 'Persona aparece')
        # ---------------------------------------------------------------------
        # Si el usuario cruza los brazos, este gesto tiene prioridad inmediata
        if self._check_crossed_arms(l_shoulder, r_shoulder, l_elbow, r_elbow,
                                    l_wrist, r_wrist, l_hip, r_hip):
            self.appearance_counter = 0
            return config.EVENT_BRAZOS_CRUZADOS

        # ---------------------------------------------------------------------
        # 4. RETENCIÓN VISUAL DE 'PERSONA APARECE'
        # Mantiene visible el evento durante un intervalo para apreciación y captura
        # ---------------------------------------------------------------------
        if self.appearance_counter > 0:
            self.appearance_counter -= 1
            return config.EVENT_PERSONA_APARECE

        # ---------------------------------------------------------------------
        # 5. EVALUACIÓN: Persona se Acerca
        # ---------------------------------------------------------------------
        if self.last_shoulder_distance >= config.PROXIMITY_SHOULDER_RATIO_MIN:
            return config.EVENT_PERSONA_SE_ACERCA

        return config.EVENT_NINGUNO

    def _check_crossed_arms(self, l_sh, r_sh, l_el, r_el, l_wr, r_wr, l_hip, r_hip):
        """
        Comprobación geométrica rigurosa de brazos cruzados.
        """
        # Validar visibilidad
        l_vis = getattr(l_wr, 'visibility', 1.0)
        r_vis = getattr(r_wr, 'visibility', 1.0)
        if l_vis < 0.35 or r_vis < 0.35:
            return False

        # Altura en el torso (entre hombros y caderas)
        top_y = min(l_sh.y, r_sh.y) - 0.05
        bottom_y = max(l_hip.y, r_hip.y) + 0.05
        if not (top_y < l_wr.y < bottom_y and top_y < r_wr.y < bottom_y):
            return False

        # Eje medio horizontal del torso
        center_x = (l_sh.x + r_sh.x) / 2.0

        # Cruce contralateral
        crossed_center = (
            (l_wr.x > center_x and r_wr.x < center_x) or
            (l_wr.x < center_x and r_wr.x > center_x)
        )

        # Distancia reducida entre muñecas respecto a codos
        elbow_dist = abs(l_el.x - r_el.x)
        wrist_dist = abs(l_wr.x - r_wr.x)
        narrow_wrists = wrist_dist < (elbow_dist * config.CROSSED_ARMS_RATIO_MAX)

        return crossed_center and narrow_wrists

    def draw_landmarks(self, frame_bgr):
        """
        Dibuja el esqueleto anatómico y los nodos clave sobre el cuadro de video.
        """
        if not self.current_landmarks:
            return

        h, w, _ = frame_bgr.shape
        lm = self.current_landmarks

        # 1. Dibujar líneas de conexión
        for idx1, idx2 in self.POSE_CONNECTIONS:
            if idx1 < len(lm) and idx2 < len(lm):
                pt1 = (int(lm[idx1].x * w), int(lm[idx1].y * h))
                pt2 = (int(lm[idx2].x * w), int(lm[idx2].y * h))
                cv2.line(frame_bgr, pt1, pt2, (80, 220, 100), 2, cv2.LINE_AA)

        # 2. Dibujar puntos articulares
        for i in range(min(25, len(lm))):
            pt = (int(lm[i].x * w), int(lm[i].y * h))
            # Hombros, codos y muñecas en color resaltado
            if i in (11, 12, 13, 14, 15, 16):
                cv2.circle(frame_bgr, pt, 5, (0, 200, 255), -1, cv2.LINE_AA)
            else:
                cv2.circle(frame_bgr, pt, 3, (255, 180, 0), -1, cv2.LINE_AA)
