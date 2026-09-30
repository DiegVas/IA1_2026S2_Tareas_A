"""
=============================================================================
INTEGRANTE 2: PRUEBA LOCAL DE EXTREMIDADES Y MANOS (POSE + HANDS)
=============================================================================
Script de prueba en tiempo real:
- Reutiliza PoseDetector (Integrante 1) y le pasa sus landmarks a GestureDetector.
- Muestra el gesto confirmado (3 cuadros), la lectura cruda del cuadro y si
  MediaPipe Hands se ejecutó en ese cuadro.
- Guarda capturas de evidencia con la tecla 's'.
"""

import cv2
import time
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import config
from modules.pose_detector import PoseDetector
from modules.gesture_detector import GestureDetector

GESTURE_COLORS = {
    config.EVENT_MANO_LEVANTADA:    (60, 240, 90),
    config.EVENT_SENALAR_IZQUIERDA: (255, 180, 0),
    config.EVENT_SENALAR_DERECHA:   (255, 180, 0),
    config.EVENT_PULGAR_ARRIBA:     (0, 220, 120),
    config.EVENT_PULGAR_ABAJO:      (50, 50, 255),
}


def main():
    print("=" * 70)
    print("   Integrante 2: Extremidades y Manos (Pose + Hands)")
    print(f"   Resolución Fija:      {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
    print(f"   Confirmación:         {config.GESTURE_CONFIRM_FRAMES} cuadros consecutivos")
    print("=" * 70)

    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara en el índice {config.CAMERA_INDEX}.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    pose_detector = PoseDetector()
    gesture_detector = GestureDetector()

    evidencias_dir = os.path.join(SCRIPT_DIR, "evidencias")
    os.makedirs(evidencias_dir, exist_ok=True)

    print("\n[Iniciado] Presione 'q' para salir | Presione 's' para guardar captura de evidencia.")

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            frame = cv2.flip(frame, 1)

            curr_time = time.time()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)

            landmarks, pose_event, _ = pose_detector.process(frame)
            gesture = gesture_detector.process(frame, landmarks)

            pose_detector.draw_landmarks(frame)
            gesture_detector.draw_hand_landmarks(frame)

            h, w, _ = frame.shape
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 80), (20, 20, 25), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

            event_name = gesture or pose_event
            color_evento = GESTURE_COLORS.get(gesture, (200, 200, 210))
            cv2.line(frame, (0, 80), (w, 80), color_evento, 2)

            cv2.putText(frame, "EXTREMIDADES + MANOS (640x480)", (12, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 180, 0), 1, cv2.LINE_AA)
            cv2.putText(frame, f"EVENTO: {event_name.upper()}", (12, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_evento, 2, cv2.LINE_AA)
            if gesture:
                # Formato corto para que quepa en 640 px: interpretacion -> respuesta (confianza)
                info = (f">> {gesture_detector.get_interpretation(gesture)}"
                        f" -> {gesture_detector.get_response(gesture)}"
                        f" (conf. {gesture_detector.confidence:.0%})")
            else:
                info = f">> {config.EVENT_INTERPRETATIONS.get(event_name, '')}"
            cv2.putText(frame, info, (12, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)

            # Métricas: FPS, estado de Hands y progreso de la persistencia temporal
            stab = gesture_detector.stabilizer
            raw = gesture_detector.raw_gesture or "-"
            cv2.putText(frame, f"FPS: {fps:04.1f}", (w - 110, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 220, 100), 2, cv2.LINE_AA)
            hands_txt = "Hands: ON" if gesture_detector.hands_active else "Hands: off"
            cv2.putText(frame, hands_txt, (w - 110, 46),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(frame, f"Crudo: {raw} ({min(stab.count, stab.confirm_frames)}/{stab.confirm_frames})",
                        (12, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)

            cv2.imshow("Gestos Extremidades y Manos - Avance Funcional", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('s'):
                filename = f"evidencia_int2_{event_name.replace(' ', '_')}_{int(time.time())}.png"
                path = os.path.join(evidencias_dir, filename)
                cv2.imwrite(path, frame)
                print(f"[Evidencia Guardada] -> {path}")

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n[Cerrado] Recursos de cámara liberados.")


if __name__ == "__main__":
    main()
