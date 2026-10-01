"""
Prueba local de Pose + Hands + HUD + Robot AURA.

Estados:
Espera -> Deteccion -> Interpretacion -> Ejecucion -> Exito/Error.
Incluye Saludo y Despedida cuando corresponde.

q / Esc: salir.
s: guardar captura de evidencia.
"""

import cv2
import time
import os
import sys
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import config
from modules.pose_detector import PoseDetector
from modules.gesture_detector import GestureDetector
from modules.robot_2d import Robot2D
from modules.hud import HUD


WINDOW_NAME = "AURA - Gestos y Robot 2D"


def log(mensaje):
    print(mensaje, flush=True)


class ControlVisual:
    TIEMPO_DETECCION = 0.4
    TIEMPO_INTERPRETACION = 0.6
    TIEMPO_REACCION = 0.8
    TIEMPO_EJECUCION = 0.5
    TIEMPO_RESULTADO = 1.5

    def __init__(self, robot):
        self.robot = robot
        self.ultimo_evento = config.EVENT_NINGUNO
        self.evento_activo = config.EVENT_NINGUNO
        self.etapa = None
        self.inicio_etapa = time.perf_counter()

        self.mensaje = "Esperando interaccion"
        self.opcion_seleccionada = None
        self.interaccion_activa = False
        self.aprobado = None

        self.respuestas = {
            config.EVENT_PERSONA_APARECE: "Saludar",
            config.EVENT_MANO_LEVANTADA: "Responder saludo",
            config.EVENT_PULGAR_ARRIBA: "Confirmar",
            config.EVENT_PULGAR_ABAJO: "Cambiar respuesta",
            config.EVENT_SENALAR_IZQUIERDA: "Mostrar opcion izquierda",
            config.EVENT_SENALAR_DERECHA: "Mostrar opcion derecha",
            config.EVENT_BRAZOS_CRUZADOS: "Reiniciar seleccion",
            config.EVENT_PERSONA_SE_ACERCA: "Activar interaccion",
            config.EVENT_PERSONA_DESAPARECE: "Despedirse",
        }

    def _cambiar_etapa(self, etapa, ahora):
        self.etapa = etapa
        self.inicio_etapa = ahora

        if etapa == self.robot.DETECCION:
            self.robot.iniciar_deteccion()
        elif etapa == self.robot.INTERPRETACION:
            self.robot.iniciar_interpretacion()
        elif etapa == self.robot.EJECUCION:
            self.robot.iniciar_ejecucion()
        else:
            self.robot.cambiar_estado(etapa)

        log(
            f"[ESTADO] {self.evento_activo} "
            f"| {self.robot.estado}"
        )

    def _iniciar_evento(self, evento, ahora):
        self.evento_activo = evento

        self.robot.actualizar(
            evento,
            estado_agente=self.robot.DETECCION
        )

        self.robot.detalle_resultado = ""
        self.robot.respuesta = self.respuestas.get(evento, "")

        if evento == config.EVENT_BRAZOS_CRUZADOS:
            self.robot.interpretacion = (
                "Comando definido: reiniciar seleccion"
            )

        self.mensaje = "Evento detectado"
        self._cambiar_etapa(self.robot.DETECCION, ahora)

    def _ejecutar_respuesta_local(self):
        evento = self.evento_activo

        if evento == config.EVENT_PERSONA_APARECE:
            self.interaccion_activa = True
            self.mensaje = "Hola, bienvenido a AURA"

        elif evento == config.EVENT_MANO_LEVANTADA:
            self.mensaje = "Hola, he recibido tu saludo"

        elif evento == config.EVENT_PULGAR_ARRIBA:
            self.aprobado = True
            self.mensaje = "Respuesta confirmada"

        elif evento == config.EVENT_PULGAR_ABAJO:
            self.aprobado = False
            self.opcion_seleccionada = None
            self.mensaje = (
                "Respuesta rechazada; selecciona otra opcion"
            )

        elif evento == config.EVENT_SENALAR_IZQUIERDA:
            self.opcion_seleccionada = "Izquierda"
            self.aprobado = None
            self.mensaje = "Opcion izquierda seleccionada"

        elif evento == config.EVENT_SENALAR_DERECHA:
            self.opcion_seleccionada = "Derecha"
            self.aprobado = None
            self.mensaje = "Opcion derecha seleccionada"

        elif evento == config.EVENT_BRAZOS_CRUZADOS:
            self.opcion_seleccionada = None
            self.aprobado = None
            self.mensaje = "Seleccion reiniciada"

        elif evento == config.EVENT_PERSONA_SE_ACERCA:
            self.interaccion_activa = True
            self.mensaje = "Interaccion activada"

        elif evento == config.EVENT_PERSONA_DESAPARECE:
            self.interaccion_activa = False
            self.mensaje = "Hasta pronto"

        else:
            raise ValueError(
                f"No existe una respuesta para: {evento}"
            )

        return self.mensaje

    def actualizar(self, evento):
        ahora = time.perf_counter()
        evento = evento or config.EVENT_NINGUNO

        cambio_evento = evento != self.ultimo_evento
        self.ultimo_evento = evento

        if cambio_evento and evento != config.EVENT_NINGUNO:
            self._iniciar_evento(evento, ahora)
            return

        if self.etapa is None:
            return

        transcurrido = ahora - self.inicio_etapa

        if self.etapa == self.robot.DETECCION:
            if transcurrido >= self.TIEMPO_DETECCION:
                self.mensaje = "Interpretando evento"
                self._cambiar_etapa(
                    self.robot.INTERPRETACION,
                    ahora
                )

        elif self.etapa == self.robot.INTERPRETACION:
            if transcurrido >= self.TIEMPO_INTERPRETACION:
                if self.evento_activo in (
                    config.EVENT_PERSONA_APARECE,
                    config.EVENT_MANO_LEVANTADA,
                ):
                    siguiente = self.robot.SALUDO

                elif (
                    self.evento_activo
                    == config.EVENT_PERSONA_DESAPARECE
                ):
                    siguiente = self.robot.DESPEDIDA

                else:
                    siguiente = self.robot.EJECUCION

                self._cambiar_etapa(siguiente, ahora)

        elif self.etapa in (
            self.robot.SALUDO,
            self.robot.DESPEDIDA,
        ):
            if transcurrido >= self.TIEMPO_REACCION:
                self._cambiar_etapa(
                    self.robot.EJECUCION,
                    ahora
                )

        elif self.etapa == self.robot.EJECUCION:
            if transcurrido >= self.TIEMPO_EJECUCION:
                try:
                    detalle = self._ejecutar_respuesta_local()

                except Exception as error:
                    self.mensaje = f"Error: {error}"
                    self.robot.finalizar_accion(
                        False,
                        self.mensaje
                    )

                else:
                    self.robot.finalizar_accion(
                        True,
                        detalle
                    )

                self.etapa = self.robot.estado
                self.inicio_etapa = ahora

                log(
                    f"[RESULTADO] {self.robot.estado} "
                    f"| {self.mensaje}"
                )

        elif self.etapa in (
            self.robot.EXITO,
            self.robot.ERROR,
        ):
            if transcurrido >= self.TIEMPO_RESULTADO:
                self.robot.actualizar(
                    config.EVENT_NINGUNO,
                    estado_agente=self.robot.ESPERA
                )

                self.robot.volver_a_espera()
                self.etapa = None
                self.mensaje = "Esperando un nuevo evento"


def dibujar_resultado(frame, hud, mensaje):
    """Mostrar el resultado local encima del diagnostico."""
    alto, ancho = frame.shape[:2]

    lineas = hud._lineas(
        f"Resultado local: {mensaje}",
        ancho - 24,
        escala=0.43
    )

    for indice, linea in enumerate(lineas[:2]):
        posicion = (12, alto - 55 + indice * 18)

        cv2.putText(
            frame,
            linea,
            posicion,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            (0, 0, 0),
            3,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            linea,
            posicion,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )


def liberar_detector(detector):
    """Cerrar el recurso de MediaPipe del backend utilizado."""
    if detector is None:
        return

    for nombre in ("pose", "hands", "landmarker"):
        recurso = getattr(detector, nombre, None)

        if recurso is not None:
            cerrar = getattr(recurso, "close", None)

            if callable(cerrar):
                try:
                    cerrar()
                except Exception as error:
                    log(
                        f"[AVISO] No se pudo cerrar "
                        f"{nombre}: {error}"
                    )


def main():
    log("=" * 70)
    log("AURA: Pose + Hands + HUD + Robot 2D")
    log(
        f"Resolucion solicitada: "
        f"{config.FRAME_WIDTH}x{config.FRAME_HEIGHT}"
    )
    log(
        f"Confirmacion: "
        f"{config.GESTURE_CONFIRM_FRAMES} cuadros"
    )
    log("=" * 70)

    cap = None
    pose_detector = None
    gesture_detector = None

    try:
        log("[1] Abriendo camara...")

        if sys.platform == "win32":
            cap = cv2.VideoCapture(
                config.CAMERA_INDEX,
                cv2.CAP_DSHOW
            )
        else:
            cap = cv2.VideoCapture(config.CAMERA_INDEX)

        if not cap.isOpened():
            log(
                f"[ERROR] No se pudo abrir la camara "
                f"{config.CAMERA_INDEX}."
            )
            return

        cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            config.FRAME_WIDTH
        )
        cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            config.FRAME_HEIGHT
        )

        log("[2] Camara abierta.")

        log("[3] Cargando PoseDetector...")
        pose_detector = PoseDetector()
        log("[4] PoseDetector listo.")

        log("[5] Cargando GestureDetector...")
        gesture_detector = GestureDetector()
        log("[6] GestureDetector listo.")

        log("[7] Cargando robot y HUD...")
        robot = Robot2D()
        hud = HUD()
        control_visual = ControlVisual(robot)

        faltantes = [
            estado
            for estado, sprite in robot.sprites.items()
            if sprite is None
        ]

        if faltantes:
            log(
                "[AVISO] Sprites no disponibles: "
                + ", ".join(faltantes)
            )

        log("[8] Robot y HUD listos.")

        evidencias_dir = os.path.join(
            SCRIPT_DIR,
            "evidencias"
        )
        os.makedirs(evidencias_dir, exist_ok=True)

        log("[9] Creando ventana...")
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        cv2.resizeWindow(
            WINDOW_NAME,
            config.FRAME_WIDTH,
            config.FRAME_HEIGHT
        )

        log("[Iniciado] Haz clic en la ventana del video.")
        log(
            "Presiona q / Esc para salir, "
            "o s para guardar una captura."
        )

        prev_time = None
        fps = 0.0
        primer_cuadro = True
        ultimo_evento = None

        while True:
            if primer_cuadro:
                log("[10] Leyendo primer cuadro...")

            ret, frame = cap.read()

            if not ret or frame is None:
                log(
                    "[ERROR] La camara no esta "
                    "entregando imagen."
                )
                break

            if primer_cuadro:
                alto, ancho = frame.shape[:2]
                log(
                    f"[11] Cuadro recibido: "
                    f"{ancho}x{alto}."
                )

            frame = cv2.flip(frame, 1)

            curr_time = time.perf_counter()

            if prev_time is not None:
                dt = curr_time - prev_time

                if dt > 0:
                    instant_fps = 1.0 / dt
                    fps = (
                        0.9 * fps + 0.1 * instant_fps
                        if fps > 0
                        else instant_fps
                    )

            prev_time = curr_time

            if primer_cuadro:
                log("[12] Procesando Pose...")

            landmarks, pose_event, _ = (
                pose_detector.process(frame)
            )

            if primer_cuadro:
                log("[13] Procesando gestos...")

            gesture = gesture_detector.process(
                frame,
                landmarks
            )

            if primer_cuadro:
                log("[14] Dibujando landmarks...")

            pose_detector.draw_landmarks(frame)
            gesture_detector.draw_hand_landmarks(frame)

            event_name = (
                gesture
                or pose_event
                or config.EVENT_NINGUNO
            )

            control_visual.actualizar(event_name)

            if primer_cuadro:
                log("[15] Dibujando HUD y robot...")

            hud.dibujar(
                frame,
                evento=robot.evento_actual,
                interpretacion=robot.interpretacion,
                estado=robot.estado,
                sprite=robot.sprite_actual,
                fps=fps,
                respuesta=robot.respuesta
            )

            dibujar_resultado(
                frame,
                hud,
                control_visual.mensaje
            )

            alto = frame.shape[0]
            stab = gesture_detector.stabilizer
            raw = gesture_detector.raw_gesture or "-"

            hands_txt = (
                "Hands: ON"
                if gesture_detector.hands_active
                else "Hands: off"
            )

            diagnostico = (
                f"{hands_txt} | Crudo: {raw} "
                f"({min(stab.count, stab.confirm_frames)}"
                f"/{stab.confirm_frames})"
            )

            cv2.putText(
                frame,
                diagnostico,
                (12, alto - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (220, 220, 220),
                1,
                cv2.LINE_AA
            )

            if primer_cuadro:
                log("[16] Mostrando video...")

            cv2.imshow(WINDOW_NAME, frame)
            key = cv2.waitKey(1) & 0xFF

            if primer_cuadro:
                log(
                    "[17] Primer cuadro "
                    "mostrado correctamente."
                )
                primer_cuadro = False

            if event_name != ultimo_evento:
                log(
                    f"[EVENTO] {event_name} "
                    f"| Estado de AURA: {robot.estado}"
                )
                ultimo_evento = event_name

            if key in (ord("q"), ord("Q"), 27):
                log("[Salida] Tecla de cierre recibida.")
                break

            elif key in (ord("s"), ord("S")):
                filename = (
                    f"evidencia_"
                    f"{robot.evento_actual.replace(' ', '_')}_"
                    f"{robot.estado}_"
                    f"{time.time_ns()}.png"
                )

                path = os.path.join(
                    evidencias_dir,
                    filename
                )

                if cv2.imwrite(path, frame):
                    log(f"[Evidencia guardada] {path}")
                else:
                    log(
                        f"[ERROR] No se pudo guardar: "
                        f"{path}"
                    )

            if cv2.getWindowProperty(
                WINDOW_NAME,
                cv2.WND_PROP_VISIBLE
            ) < 1:
                log("[Salida] Ventana cerrada.")
                break

    except KeyboardInterrupt:
        log("[Salida] Interrumpido desde la terminal.")

    except Exception:
        log("[ERROR] Ocurrio un problema. Detalle:")
        traceback.print_exc()

    finally:
        liberar_detector(gesture_detector)
        liberar_detector(pose_detector)

        if cap is not None:
            cap.release()

        cv2.destroyAllWindows()
        log("[Cerrado] Recursos liberados.")


if __name__ == "__main__":
    main()