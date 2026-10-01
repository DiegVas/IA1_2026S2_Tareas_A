from pathlib import Path

import cv2
import config


class Robot2D:
    ESPERA = "Espera"
    SALUDO = "Saludo"
    DETECCION = "Deteccion"
    INTERPRETACION = "Interpretacion"
    EJECUCION = "Ejecucion"
    EXITO = "Exito"
    ERROR = "Error"
    DESPEDIDA = "Despedida"

    def __init__(self):
        self.assets_dir = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "aura"
        )

        self.archivos = {
            self.ESPERA: "espera.png",
            self.SALUDO: "saludo.png",
            self.DETECCION: "deteccion.png",
            self.INTERPRETACION: "interpretacion.png",
            self.EJECUCION: "ejecucion.png",
            self.EXITO: "exito.png",
            self.ERROR: "error.png",
            self.DESPEDIDA: "despedida.png",
        }

        self.sprites = {}

        for estado, archivo in self.archivos.items():
            ruta = self.assets_dir / archivo
            imagen = None

            if ruta.is_file():
                imagen = cv2.imread(
                    str(ruta),
                    cv2.IMREAD_UNCHANGED
                )

            if imagen is None:
                print(
                    f"[Robot2D] Imagen pendiente o invalida: {ruta}",
                    flush=True
                )

            self.sprites[estado] = imagen

        self.evento_actual = config.EVENT_NINGUNO
        self.interpretacion = ""
        self.respuesta = ""
        self.detalle_resultado = ""

        self.estado = self.ESPERA
        self.sprite_actual = self.sprites[self.ESPERA]

        # Evitar que el mismo evento reinicie el estado en cada frame.
        self._ultimo_evento = None

    def cambiar_estado(self, estado):
        """Seleccionar un estado visual válido."""
        if estado not in self.archivos:
            raise ValueError(
                f"Estado de AURA no valido: {estado}"
            )

        self.estado = estado
        self.sprite_actual = self.sprites[estado]

    def actualizar(self, evento, estado_agente=None):
        """
        Actualizar evento, interpretación, respuesta y sprite.

        Sin estado_agente:
            selecciona una reacción inicial cuando cambia el evento.

        Con estado_agente:
            representa la etapa indicada por el sistema.
        """
        evento = evento or config.EVENT_NINGUNO
        cambio_evento = evento != self._ultimo_evento

        self.evento_actual = evento

        self.interpretacion = config.EVENT_INTERPRETATIONS.get(
            evento, ""
        )

        self.respuesta = config.EVENT_RESPONSES.get(
            evento, ""
        )

        if estado_agente is not None:
            self.cambiar_estado(estado_agente)

        elif cambio_evento:
            self.detalle_resultado = ""

            if evento == config.EVENT_NINGUNO:
                self.cambiar_estado(self.ESPERA)

            elif evento in (
                config.EVENT_PERSONA_APARECE,
                config.EVENT_MANO_LEVANTADA
            ):
                self.cambiar_estado(self.SALUDO)

            elif evento == config.EVENT_PERSONA_DESAPARECE:
                self.cambiar_estado(self.DESPEDIDA)

            else:
                self.cambiar_estado(self.INTERPRETACION)

        self._ultimo_evento = evento

    def iniciar_deteccion(self):
        """Llamar cuando comienza la detección de una interacción."""
        self.cambiar_estado(self.DETECCION)

    def iniciar_interpretacion(self):
        """Llamar cuando el sistema analiza el evento."""
        self.cambiar_estado(self.INTERPRETACION)

    def iniciar_ejecucion(self):
        """Llamar cuando realmente comienza la acción asociada."""
        self.detalle_resultado = ""
        self.cambiar_estado(self.EJECUCION)

    def finalizar_accion(self, exitosa, detalle=""):
        """
        Mostrar el resultado real de una acción.

        exitosa debe ser True o False.
        """
        if not isinstance(exitosa, bool):
            raise TypeError("exitosa debe ser True o False.")

        self.detalle_resultado = detalle

        if exitosa:
            self.cambiar_estado(self.EXITO)
        else:
            self.cambiar_estado(self.ERROR)

    def volver_a_espera(self):
        """Llamar al terminar la respuesta o despedida."""
        self.detalle_resultado = ""
        self.cambiar_estado(self.ESPERA)