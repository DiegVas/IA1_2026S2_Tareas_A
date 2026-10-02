import cv2
import os
import sys
import time
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import config
from modules.pose_detector    import PoseDetector
from modules.gesture_detector import GestureDetector
from modules.robot_2d         import Robot2D
from modules.hud              import HUD
from modules.agent_controller import AgentController

WINDOW_NAME = "AURA - Sistema de Interaccion"


# ──────────────────────────────────────────────────────────────────────
# Helpers de renderizado y limpieza
# ──────────────────────────────────────────────────────────────────────

def _draw_result(frame, mensaje, hud):
    """Dibuja el mensaje de resultado del controlador en la parte inferior."""
    alto, ancho = frame.shape[:2]
    for i, linea in enumerate(hud._lineas(f"Resultado: {mensaje}", ancho - 24)[:2]):
        y = alto - 55 + i * 18
        cv2.putText(frame, linea, (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.43, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, linea, (12, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.43, (255, 255, 255), 1, cv2.LINE_AA)


def _draw_debug(frame, gd):
    """Muestra estado crudo del estabilizador de gestos."""
    stab = gd.stabilizer
    raw  = gd.raw_gesture or "-"
    txt  = (f"Hands: {'ON' if gd.hands_active else 'off'} | "
            f"Crudo: {raw} "
            f"({min(stab.count, stab.confirm_frames)}/{stab.confirm_frames})")
    cv2.putText(frame, txt, (12, frame.shape[0] - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220, 220, 220), 1, cv2.LINE_AA)


def _liberar(detector):
    """Cierra los recursos de MediaPipe del detector indicado."""
    if detector is None:
        return
    for nombre in ("pose", "hands", "landmarker"):
        recurso = getattr(detector, nombre, None)
        if callable(getattr(recurso, "close", None)):
            try:
                recurso.close()
            except Exception:
                pass


# ──────────────────────────────────────────────────────────────────────
# Punto de entrada
# ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("AURA — Sistema de Interaccion Corporal")
    print(f"Resolucion: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT} | "
          f"Confirmacion: {config.GESTURE_CONFIRM_FRAMES} cuadros")
    print("=" * 60)

    cap = pose_detector = gesture_detector = None

    try:
        if sys.platform == "win32":
            cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
        elif config.USE_PI_CAMERA:
            cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_V4L2)
        else:
            cap = cv2.VideoCapture(config.CAMERA_INDEX)

        if not cap.isOpened():
            print(f"[ERROR] No se pudo abrir la camara {config.CAMERA_INDEX}.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        pose_detector    = PoseDetector()
        gesture_detector = GestureDetector()
        robot            = Robot2D()
        hud              = HUD()
        controller       = AgentController(robot)

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, config.FRAME_WIDTH, config.FRAME_HEIGHT)
        print("q / Esc: salir")

        fps          = 0.0
        prev_time    = None
        ultimo_evento = None

        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                continue

            frame = cv2.flip(frame, 1)

            now = time.perf_counter()
            if prev_time:
                fps = 0.9 * fps + 0.1 / (now - prev_time) if fps else 1.0 / (now - prev_time)
            prev_time = now

            # ── Detección ─────────────────────────────────────────────
            landmarks, pose_event, _ = pose_detector.process(frame)

            # Resetear estabilizador al aparecer: evita falsos positivos de mano
            if pose_event == config.EVENT_PERSONA_APARECE:
                gesture_detector.stabilizer.reset()
                gesture = None
            else:
                gesture = gesture_detector.process(frame, landmarks)

            event_name = gesture or pose_event or config.EVENT_NINGUNO

            # ── Reacción ──────────────────────────────────────────────
            controller.update(event_name, presente=pose_detector.person_present)

            # ── Renderizado ───────────────────────────────────────────
            pose_detector.draw_landmarks(frame)
            gesture_detector.draw_hand_landmarks(frame)
            hud.dibujar(frame,
                        evento=robot.evento_actual,
                        interpretacion=robot.interpretacion,
                        estado=robot.estado,
                        sprite=robot.sprite_actual,
                        fps=fps,
                        respuesta=robot.respuesta)
            _draw_result(frame, controller.mensaje, hud)
            _draw_debug(frame, gesture_detector)

            cv2.imshow(WINDOW_NAME, frame)

            if event_name != ultimo_evento:
                print(f"[EVENTO] {event_name} | AURA: {robot.estado}", flush=True)
                ultimo_evento = event_name

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            elif key in (ord("e"), ord("E")):
                controller.forzar_error()

            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
    finally:
        _liberar(gesture_detector)
        _liberar(pose_detector)
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        print("Recursos liberados.")


if __name__ == "__main__":
    main()
