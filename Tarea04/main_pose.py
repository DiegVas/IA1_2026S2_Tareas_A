
# Script para pruebas locales:
# Captura de video en 640x480
# Visualiza eventoS detectado, interpretación y métricas de proximidad.

import cv2
import time
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import config
from modules.pose_detector import PoseDetector

def main():
    print("=" * 70)
    print(f"   Resolución Fija:      {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
    print(f"   Model Complexity:     {config.POSE_MODEL_COMPLEXITY} (Lite)")
    print("=" * 70)

    # Inicializar captura de video en local
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara en el índice {config.CAMERA_INDEX}.")
        return

    # resolución obligatoria de 640x480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    detector = PoseDetector()

    print("\n[Iniciado] Presione 'q' para salir.")

    prev_time = time.time()
    fps = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            # Modo espejo
            frame = cv2.flip(frame, 1)

            # Cálculo de FPS
            curr_time = time.time()
            dt = curr_time - prev_time
            prev_time = curr_time
            if dt > 0:
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else (1.0 / dt)


            results, event_name, shoulder_dist = detector.process(frame)


            detector.draw_landmarks(frame)

            # Dibujar panel informativo sobre el frame
            h, w, _ = frame.shape
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 80), (20, 20, 25), -1)
            cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

            # Color del texto e indicador según el evento
            if event_name == config.EVENT_BRAZOS_CRUZADOS:
                color_evento = (0, 200, 255)     # Amarillo
            elif event_name == config.EVENT_PERSONA_SE_ACERCA:
                color_evento = (50, 50, 255)     # Rojo alerta
            elif event_name == config.EVENT_PERSONA_APARECE:
                color_evento = (60, 240, 90)     # Verde
            elif event_name == config.EVENT_PERSONA_DESAPARECE:
                color_evento = (0, 140, 255)     # Naranja 
                color_evento = (200, 200, 210)   # Gris  en espera

            # Mostrar datos en pantalla
            cv2.putText(frame, f"POSE BASE (640x480)", (12, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 180, 0), 1, cv2.LINE_AA)

            cv2.putText(frame, f"EVENTO: {event_name.upper()}", (12, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_evento, 2, cv2.LINE_AA)

            interp = config.EVENT_INTERPRETATIONS.get(event_name, "")
            cv2.putText(frame, f">> {interp}", (12, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)

            # Métricas en esquina superior derecha
            cv2.putText(frame, f"FPS: {fps:04.1f}", (w - 110, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 220, 100), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Dist: {shoulder_dist:.2f}/{config.PROXIMITY_SHOULDER_RATIO_MIN}",
                        (w - 140, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)

            # Mostrar ventana
            cv2.imshow("Pose Detector - Avance Funcional", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\nEstado de la cámara cerrado.")

if __name__ == "__main__":
    main()
