"""
=============================================================================
INTEGRANTE 2: MÓDULO DE DETECCIÓN DE EXTREMIDADES Y MANOS (POSE + HANDS)
=============================================================================
Reutiliza los landmarks que ya calcula PoseDetector (Integrante 1), por lo que
Pose no se ejecuta dos veces por cuadro.

Responsabilidades del Integrante 2:
  - Lógica sobre Pose para:
      1. Mano levantada
      2. Señalar izquierda
      3. Señalar derecha
  - MediaPipe Hands ejecutado de forma CONDICIONAL (solo cuando Pose indica
    una mano a la altura del torso y sin otro gesto activo) para:
      4. Pulgar arriba
      5. Pulgar abajo
  - Persistencia temporal: un gesto se confirma tras 3 cuadros consecutivos.
  - Confianza de cada gesto (0 a 1) para el HUD y el historial.

Nota: main.py voltea el frame (modo espejo), así que "izquierda"/"derecha"
son las del lado izquierdo/derecho de la pantalla, que coinciden con la
izquierda/derecha del usuario.
"""

import math
import os
import urllib.request

import cv2
import mediapipe as mp

import config

# Índices de MediaPipe Pose
NOSE = 0
L_SHOULDER, R_SHOULDER = 11, 12
L_ELBOW, R_ELBOW = 13, 14
L_WRIST, R_WRIST = 15, 16
L_HIP, R_HIP = 23, 24

# Índices de MediaPipe Hands
H_WRIST = 0
H_THUMB_MCP, H_THUMB_TIP = 2, 4
H_MIDDLE_MCP = 9
# (PIP, TIP) de índice, medio, anular y meñique
H_FINGERS = [(6, 8), (10, 12), (14, 16), (18, 20)]

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),
]


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _angle_deg(a, b, c):
    """Ángulo interno en b formado por los segmentos b->a y b->c."""
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    n1, n2 = math.hypot(*v1), math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos))))


class GestureStabilizer:
    """
    Filtro de persistencia temporal: la salida solo cambia cuando la misma
    lectura candidata se repite en N cuadros consecutivos. Aplica también al
    regreso a "sin gesto", evitando parpadeos en ambos sentidos.
    """

    def __init__(self, confirm_frames=config.GESTURE_CONFIRM_FRAMES):
        self.confirm_frames = confirm_frames
        self.reset()

    def update(self, reading, confidence=0.0):
        if reading == self.candidate:
            self.count += 1
            self.confidences.append(confidence)
        else:
            self.candidate = reading
            self.count = 1
            self.confidences = [confidence]
        if self.count >= self.confirm_frames:
            self.confirmed = self.candidate
            # Confianza del gesto confirmado: promedio de los últimos N cuadros
            recent = self.confidences[-self.confirm_frames:]
            self.confirmed_confidence = sum(recent) / len(recent) if self.confirmed else 0.0
        return self.confirmed

    def reset(self):
        self.candidate = None
        self.count = 0
        self.confidences = []
        self.confirmed = None
        self.confirmed_confidence = 0.0


class GestureDetector:
    """
    Detector de gestos de extremidades (Pose) y manos (Hands condicional).
    Soporta el backend clásico mp.solutions (Raspberry Pi) y Tasks (PC).
    """

    def __init__(self):
        self.stabilizer = GestureStabilizer()
        self.hand_landmarks = []     # lista de manos, cada una con 21 puntos (x, y) en px
        self.hands_active = False    # si Hands se ejecutó en el último cuadro
        self.raw_gesture = None      # lectura sin filtrar del último cuadro
        self.raw_confidence = 0.0    # confianza de la lectura sin filtrar

        if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
            self.backend = "solutions"
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=config.HANDS_MAX_NUM,
                model_complexity=config.HANDS_MODEL_COMPLEXITY,
                min_detection_confidence=config.HANDS_MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.HANDS_MIN_TRACKING_CONFIDENCE,
            )
            print("[GestureDetector] Backend Hands: MediaPipe Solutions (Clásico RPi)")
        else:
            self.backend = "tasks"
            self._init_tasks_backend()
            print("[GestureDetector] Backend Hands: MediaPipe Tasks (Moderno PC)")

    def _init_tasks_backend(self):
        from mediapipe.tasks.python import vision
        from mediapipe.tasks.python import BaseOptions

        model_path = config.HAND_MODEL_PATH
        if not os.path.exists(model_path):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            print(f"[GestureDetector] Descargando modelo Hands desde {config.HAND_MODEL_URL}...")
            urllib.request.urlretrieve(config.HAND_MODEL_URL, model_path)
            print(f"[GestureDetector] Modelo descargado en: {model_path}")

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=config.HANDS_MAX_NUM,
            min_hand_detection_confidence=config.HANDS_MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.HANDS_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.HANDS_MIN_TRACKING_CONFIDENCE,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    # -------------------------------------------------------------------------
    # API pública
    # -------------------------------------------------------------------------
    def process(self, frame_bgr, pose_landmarks):
        """
        Evalúa los gestos del Integrante 2 sobre el cuadro actual.
        pose_landmarks: landmarks devueltos por PoseDetector.process (o None).
        Retorna el gesto confirmado (str) o None si no hay gesto estable.
        Su confianza queda en self.confidence.
        """
        self.hand_landmarks = []
        self.hands_active = False

        if not pose_landmarks:
            self.raw_gesture = None
            self.raw_confidence = 0.0
            self.stabilizer.reset()
            return None

        h, w = frame_bgr.shape[:2]
        pts = [(lm.x * w, lm.y * h) for lm in pose_landmarks]
        vis = [getattr(lm, 'visibility', 1.0) for lm in pose_landmarks]
        shoulder_w = _dist(pts[L_SHOULDER], pts[R_SHOULDER])

        reading, conf = None, 0.0
        if shoulder_w > 1.0:
            reading, conf = self._evaluate_pose_gestures(pts, vis, shoulder_w)
            if reading is None and self._hand_in_thumb_zone(pts, vis):
                self.hands_active = True
                reading, conf = self._evaluate_thumb(frame_bgr)

        self.raw_gesture = reading
        self.raw_confidence = conf
        return self.stabilizer.update(reading, conf)

    @property
    def confidence(self):
        """Confianza (0 a 1) del gesto confirmado; 0.0 si no hay gesto."""
        return self.stabilizer.confirmed_confidence

    @staticmethod
    def get_interpretation(gesture):
        return config.EVENT_INTERPRETATIONS.get(gesture, "")

    @staticmethod
    def get_response(gesture):
        return config.EVENT_RESPONSES.get(gesture, "")

    # -------------------------------------------------------------------------
    # Gestos basados en Pose
    # -------------------------------------------------------------------------
    def _evaluate_pose_gestures(self, pts, vis, shoulder_w):
        """
        Retorna (gesto, confianza). La confianza es el promedio de la
        visibilidad de los landmarks de Pose usados en el gesto.
        """
        min_vis = config.LIMB_MIN_VISIBILITY
        arms = [(L_SHOULDER, L_ELBOW, L_WRIST), (R_SHOULDER, R_ELBOW, R_WRIST)]

        # 1. Señalar izquierda / derecha (se evalúa primero porque es más específico:
        #    requiere extensión + horizontalidad + codo recto; así evita que un brazo
        #    extendido lateralmente dispare "Mano levantada" por pasar por encima de la nariz).
        for sh, el, wr in arms:
            if min(vis[sh], vis[el], vis[wr]) < min_vis:
                continue
            dx = pts[wr][0] - pts[sh][0]
            dy = pts[wr][1] - pts[sh][1]
            extended = abs(dx) >= config.POINT_MIN_EXTENSION * shoulder_w
            tilt = math.degrees(math.atan2(abs(dy), abs(dx)))
            elbow = _angle_deg(pts[sh], pts[el], pts[wr])
            if extended and tilt <= config.POINT_MAX_TILT_DEG and \
                    elbow >= config.POINT_MIN_ELBOW_DEG:
                gesture = config.EVENT_SENALAR_IZQUIERDA if dx < 0 else config.EVENT_SENALAR_DERECHA
                return gesture, (vis[sh] + vis[el] + vis[wr]) / 3.0

        # 2. Mano levantada (brazo arriba sin cumplir condiciones de señalar)
        if vis[NOSE] >= min_vis:
            for _, _, wr in arms:
                if vis[wr] >= min_vis and \
                        pts[NOSE][1] - pts[wr][1] >= config.RAISED_HAND_MARGIN * shoulder_w:
                    return config.EVENT_MANO_LEVANTADA, (vis[NOSE] + vis[wr]) / 2.0

        return None, 0.0

    def _hand_in_thumb_zone(self, pts, vis):
        """
        Condición para activar Hands: alguna muñeca visible entre la línea
        de hombros (con margen hacia arriba) y la de caderas.
        """
        top = min(pts[L_SHOULDER][1], pts[R_SHOULDER][1]) - _dist(pts[L_SHOULDER], pts[R_SHOULDER])
        bottom = max(pts[L_HIP][1], pts[R_HIP][1])
        for wr in (L_WRIST, R_WRIST):
            if vis[wr] >= config.LIMB_MIN_VISIBILITY and top <= pts[wr][1] <= bottom:
                return True
        return False

    # -------------------------------------------------------------------------
    # Gestos basados en Hands (pulgar)
    # -------------------------------------------------------------------------
    def _evaluate_thumb(self, frame_bgr):
        """
        Retorna (gesto, confianza). La confianza es el score que MediaPipe
        Hands asigna a la mano detectada.
        """
        h, w = frame_bgr.shape[:2]
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        if self.backend == "solutions":
            frame_rgb.flags.writeable = False
            results = self.hands.process(frame_rgb)
            hands = [hl.landmark for hl in (results.multi_hand_landmarks or [])]
            scores = [hd.classification[0].score for hd in (results.multi_handedness or [])]
        else:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            result = self.landmarker.detect(mp_image)
            hands = result.hand_landmarks or []
            scores = [hd[0].score for hd in (result.handedness or [])]

        self.hand_landmarks = [[(lm.x * w, lm.y * h) for lm in hand] for hand in hands]

        for i, hand in enumerate(self.hand_landmarks):
            gesture = self._classify_thumb(hand)
            if gesture:
                return gesture, scores[i] if i < len(scores) else 0.0
        return None, 0.0

    @staticmethod
    def _classify_thumb(hp):
        """
        Pulgar arriba/abajo: los 4 dedos restantes cerrados, pulgar extendido
        y casi vertical; el sentido lo da la posición de la punta del pulgar
        respecto a todos los demás puntos de la mano.
        """
        wrist = hp[H_WRIST]
        palm = _dist(wrist, hp[H_MIDDLE_MCP])
        if palm < 1.0:
            return None

        # Dedos cerrados: la punta queda más cerca de la muñeca que la PIP
        for pip, tip in H_FINGERS:
            if _dist(hp[tip], wrist) >= _dist(hp[pip], wrist):
                return None

        thumb_mcp, thumb_tip = hp[H_THUMB_MCP], hp[H_THUMB_TIP]
        if _dist(thumb_mcp, thumb_tip) < config.THUMB_MIN_LENGTH_RATIO * palm:
            return None

        dx = thumb_tip[0] - thumb_mcp[0]
        dy = thumb_tip[1] - thumb_mcp[1]
        tilt = math.degrees(math.atan2(abs(dx), abs(dy)))
        if tilt > config.THUMB_MAX_TILT_DEG:
            return None

        # Referencia: muñeca + MCPs de los cuatro dedos (puntos estables,
        # no varían con el cierre). Evita que puntas de dedos cerrados
        # interfieran con la comparación de dirección del pulgar.
        _BASE = (0, 5, 9, 13, 17)   # wrist, index-MCP, middle-MCP, ring-MCP, pinky-MCP
        ref_y = [hp[i][1] for i in _BASE]
        if thumb_tip[1] < min(ref_y):
            return config.EVENT_PULGAR_ARRIBA
        if thumb_tip[1] > max(ref_y):
            return config.EVENT_PULGAR_ABAJO
        return None

    # -------------------------------------------------------------------------
    # Dibujado
    # -------------------------------------------------------------------------
    def draw_hand_landmarks(self, frame_bgr):
        """Dibuja las manos detectadas por Hands en el último cuadro."""
        for hand in self.hand_landmarks:
            ipts = [(int(x), int(y)) for x, y in hand]
            for a, b in HAND_CONNECTIONS:
                cv2.line(frame_bgr, ipts[a], ipts[b], (255, 120, 200), 2, cv2.LINE_AA)
            for i, p in enumerate(ipts):
                color = (0, 255, 255) if i == H_THUMB_TIP else (255, 255, 255)
                cv2.circle(frame_bgr, p, 3, color, -1, cv2.LINE_AA)
