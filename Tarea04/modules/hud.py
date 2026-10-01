import unicodedata

import cv2


class HUD:
    def __init__(self):
        self.fuente = cv2.FONT_HERSHEY_SIMPLEX

    @staticmethod
    def _texto_simple(texto):
        # La fuente basica de OpenCV no representa bien las tildes.
        return unicodedata.normalize(
            "NFKD", str(texto)
        ).encode("ascii", "ignore").decode("ascii")

    def _lineas(self, texto, ancho_maximo, escala=0.43):
        """Dividir texto en varias lineas para evitar que salga del frame."""
        palabras = self._texto_simple(texto).split()
        lineas = []
        actual = ""

        for palabra in palabras:
            candidata = f"{actual} {palabra}".strip()

            ancho = cv2.getTextSize(
                candidata, self.fuente, escala, 1
            )[0][0]

            if ancho > ancho_maximo and actual:
                lineas.append(actual)
                actual = palabra
            else:
                actual = candidata

        if actual:
            lineas.append(actual)

        return lineas or [""]

    def _dibujar_sprite(self, frame, sprite):
        """Redimensionar y superponer una imagen en la esquina inferior."""
        alto, ancho = frame.shape[:2]

        # Conservar proporciones y reservar espacio para el video.
        alto_maximo = min(150, alto // 3)
        ancho_maximo = min(140, ancho // 4)

        factor = min(
            ancho_maximo / sprite.shape[1],
            alto_maximo / sprite.shape[0]
        )

        nuevo_ancho = max(1, int(sprite.shape[1] * factor))
        nuevo_alto = max(1, int(sprite.shape[0] * factor))

        imagen = cv2.resize(
            sprite,
            (nuevo_ancho, nuevo_alto),
            interpolation=cv2.INTER_AREA
        )

        x = ancho - nuevo_ancho - 12
        y = alto - nuevo_alto - 38

        zona = frame[y:y + nuevo_alto, x:x + nuevo_ancho]

        if imagen.ndim == 2:
            # Aceptar tambien imagenes en escala de grises.
            imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

        if imagen.shape[2] == 4:
            # PNG con transparencia: combinar usando su canal alfa.
            colores = imagen[:, :, :3].astype("float32")
            alfa = imagen[:, :, 3:4].astype("float32") / 255.0

            zona[:] = (
                colores * alfa
                + zona.astype("float32") * (1.0 - alfa)
            ).astype("uint8")
        else:
            zona[:] = imagen[:, :, :3]

    def dibujar(self, frame, evento, interpretacion, estado,
            sprite=None, fps=None, respuesta=""):
        alto, ancho = frame.shape[:2]

        color = (100, 230, 180)

        if estado == "Alerta":
            color = (70, 70, 255)
        elif estado == "Rechazo":
            color = (0, 160, 255)

        # Preparar la interpretacion en varias lineas.
        lineas = self._lineas(
            f"Interpretacion: {interpretacion}",
            ancho - 24
        )

        lineas += self._lineas(
            f"Respuesta prevista: {respuesta}",
            ancho - 24
        )

        alto_panel = 78 + len(lineas) * 18

        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (0, 0),
            (ancho, alto_panel),
            (20, 20, 25),
            -1
        )

        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        titulo = "AURA | INTERFAZ VISUAL"

        cv2.putText(
            frame, titulo, (12, 22),
            self.fuente, 0.5, color, 1, cv2.LINE_AA
        )

        if fps is not None:
            cv2.putText(
                frame, f"FPS: {fps:.1f}", (ancho - 105, 22),
                self.fuente, 0.45, (255, 255, 255), 1,
                cv2.LINE_AA
            )

        cv2.putText(
            frame,
            self._texto_simple(f"Evento: {evento}"),
            (12, 46),
            self.fuente, 0.55, color, 1, cv2.LINE_AA
        )

        cv2.putText(
            frame,
            self._texto_simple(f"Estado de AURA: {estado}"),
            (12, 68),
            self.fuente, 0.48, (255, 255, 255), 1,
            cv2.LINE_AA
        )

        for indice, linea in enumerate(lineas):
            cv2.putText(
                frame, linea, (12, 90 + indice * 18),
                self.fuente, 0.43, (210, 210, 210), 1,
                cv2.LINE_AA
            )

        cv2.line(
            frame,
            (0, alto_panel),
            (ancho, alto_panel),
            color,
            2
        )

        if sprite is not None:
            self._dibujar_sprite(frame, sprite)
        else:
            cv2.putText(
                frame, "Sprite pendiente", (ancho - 150, alto - 45),
                self.fuente, 0.43, color, 1, cv2.LINE_AA
            )

        return frame