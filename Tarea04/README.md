# Integrante 1: Módulo Base de Detección Corporal (Pose)

**Universidad de San Carlos de Guatemala**  
**Facultad de Ingeniería**  
**Escuela de Ingeniería en Ciencias y Sistemas (ECYS)**  
**Curso:** Inteligencia Artificial 1  
**Actividad:** Tarea 04 - Avance Funcional Proyecto 2 AURA  

---

## 1. Responsabilidades del Integrante 1

1. **Desarrollo en local** de la clase `PoseDetector` basada en **MediaPipe Pose**.
2. **Implementación de la lógica de detección** para los 4 eventos corporales base:
   * **Persona aparece**
   * **Persona desaparece**
   * **Persona se acerca**
   * **Brazos cruzados**
3. **Formulación geométrica y matemática** y definición de umbrales para la documentación e informe final.
4. **Cumplimiento estricto** de las reglas de compatibilidad para evitar cuellos de botella en la Raspberry Pi.

---

## 2. Reglas de Compatibilidad Obligatorias

* **Resolución fija de captura:** Forzada a **`640x480`** para garantizar fluidez (>15 FPS en hardware embebido).
* **Modelo ligero (Lite):** En `mp.solutions.pose.Pose`, se fija **`model_complexity=0`** de manera obligatoria.
* **Dependencias puras:** `opencv-python`, `mediapipe` y `numpy`.

---

## 3. Formulación Geométrica y Umbrales (Para el Informe)

### Evento 1: Persona aparece
* **Fundamento:** Detección de presencia a partir del flujo de landmarks.
* **Condición lógica:**
  $$\text{estado\_previo} = \text{False} \quad \land \quad \text{pose\_landmarks} \neq \text{None}$$
* **Comportamiento:** Al detectar el primer cuadro con puntos corporales válidos tras un periodo de ausencia, se activa el evento y se actualiza el estado interno a `person_present = True`.

---

### Evento 2: Persona desaparece
* **Fundamento:** Ausencia sostenida de landmarks corporales para filtrar oclusiones momentáneas o falsos negativos de un solo cuadro.
* **Condición lógica:**
  $$\text{pose\_landmarks} = \text{None} \quad \text{durante} \quad N \ge \text{DISAPPEAR\_TIMEOUT\_FRAMES}$$
* **Umbral:** $\text{DISAPPEAR\_TIMEOUT\_FRAMES} = 10 \text{ cuadros}$.
* **Comportamiento:** Si la persona estaba presente y transcurren 10 cuadros consecutivos sin detección, se confirma la salida del usuario del campo visual.

---

### Evento 3: Persona se acerca
* **Fundamento:** Medición de proximidad basada en la distancia euclidiana normalizada entre ambos hombros. Al aproximarse a la cámara, la distancia aparente entre los hombros aumenta en el plano de la imagen.
* **Landmarks utilizados:**
  * Hombro izquierdo: $L_{11} = (X_{l\_sh}, Y_{l\_sh})$
  * Hombro derecho: $L_{12} = (X_{r\_sh}, Y_{r\_sh})$
* **Ecuación matemática:**
  $$d_{\text{hombros}} = \sqrt{(X_{l\_sh} - X_{r\_sh})^2 + (Y_{l\_sh} - Y_{r\_sh})^2}$$
* **Umbral de activación:**
  $$d_{\text{hombros}} \ge \text{PROXIMITY\_SHOULDER\_RATIO\_MIN} = 0.35$$
  *(Un valor $\ge 0.35$ en coordenadas normalizadas indica que el ancho de hombros ocupa más del 35% del encuadre, situando al usuario a corta distancia).*

---

### Evento 4: Brazos cruzados
* **Fundamento:** Análisis postural tridimensional proyectado en 2D que verifica que ambas muñecas se encuentren sobre el torso, cruzadas respecto al eje medio y con una separación menor a la distancia entre codos.
* **Landmarks utilizados:**
  * Hombros: $L_{11}, L_{12}$
  * Codos: $L_{13}, L_{14}$
  * Muñecas: $L_{15}, L_{16}$
  * Caderas: $L_{23}, L_{24}$
* **Condiciones geométricas simultáneas:**
  1. **Franja vertical del torso:** Las muñecas deben posicionarse entre la línea de los hombros y las caderas:
     $$\min(Y_{l\_sh}, Y_{r\_sh}) - 0.05 < Y_{\text{muñeca}} < \max(Y_{l\_hip}, Y_{r\_hip}) + 0.05$$
  2. **Eje medio horizontal del torso:**
     $$X_{\text{centro}} = \frac{X_{l\_sh} + X_{r\_sh}}{2}$$
  3. **Cruce contralateral:**
     $$(X_{l\_wr} > X_{\text{centro}} \land X_{r\_wr} < X_{\text{centro}}) \quad \lor \quad (X_{l\_wr} < X_{\text{centro}} \land X_{r\_wr} > X_{\text{centro}})$$
  4. **Proximidad relativa de muñecas:** La separación entre muñecas debe ser menor que la distancia entre codos multiplicada por un factor de tolerancia:
     $$|X_{l\_wr} - X_{r\_wr}| < 0.65 \cdot |X_{l\_el} - X_{r\_el}|$$

---

## 4. Estructura de Archivos del Integrante 1

```text
Tarea04_AURA/
├── config.py                 # Constantes, umbrales geométricos y nombres de los 4 eventos
├── requirements.txt          # Dependencias (opencv-python, mediapipe, numpy)
├── main.py                   # Script de prueba local en tiempo real con webcam
├── README.md                 # Documentación técnica y formulación geométrica
└── modules/
    ├── __init__.py
    └── pose_detector.py      # Clase PoseDetector con MediaPipe Pose Lite
```

---

## 5. Instrucciones de Ejecución Local

1. Instalar dependencias en el entorno de Python:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar las pruebas locales con la cámara web:
   ```bash
   python main.py
   ```

3. Controles en la ventana de prueba:
   * **`q`** o **`ESC`**: Finalizar la ejecución.
   * **`s`**: Guardar una captura de pantalla del frame actual en la carpeta `evidencias/` con el evento detectado y marca de tiempo (para anexar al informe).

---
---

# Integrante 2: Módulo de Detección de Extremidades y Manos (Pose + Hands)

## 1. Responsabilidades del Integrante 2

1. **Lógica sobre MediaPipe Pose** para: **Mano levantada**, **Señalar izquierda** y **Señalar derecha**.
2. **Integración condicional de MediaPipe Hands** para: **Pulgar arriba** y **Pulgar abajo**.
3. **Persistencia temporal**: un gesto solo se confirma tras **3 cuadros consecutivos** con la misma lectura.
4. **Interpretación, respuesta y confianza** de cada gesto, según la tabla del Módulo 1 del enunciado:

| Percepción | Interpretación | Respuesta |
|---|---|---|
| Mano levantada | Saludo | Responder |
| Pulgar arriba | Aprobación | Confirmar |
| Pulgar abajo | Rechazo | Cambiar respuesta |
| Señalar izquierda | Dirección | Mostrar opción izquierda |
| Señalar derecha | Dirección | Mostrar opción derecha |

Están en `config.EVENT_INTERPRETATIONS` y `config.EVENT_RESPONSES` (sin tildes ni ñ en el código porque `cv2.putText` no las dibuja).

El módulo (`modules/gesture_detector.py`) **reutiliza los landmarks de `PoseDetector`** (Integrante 1), así que Pose se ejecuta una sola vez por cuadro.

---

## 2. Convenciones

* Los landmarks normalizados se convierten a píxeles del frame 640x480 para que $x$ e $y$ tengan la misma escala.
* **Ancho de hombros** como unidad de normalización (hace los umbrales independientes de la distancia a la cámara):
  $$W_h = \lVert P_{11} - P_{12} \rVert$$
* Un landmark de Pose se usa solo si su visibilidad es $\ge 0.5$ (`LIMB_MIN_VISIBILITY`).
* El frame se muestra en **modo espejo**, por lo que *izquierda/derecha* son las de la pantalla, que coinciden con las del usuario.
* En imagen, $y$ crece hacia abajo.

---

## 3. Formulación Geométrica y Umbrales (Para el Informe)

### Evento 5: Mano levantada (Pose)
* **Landmarks:** nariz $P_0$, muñecas $P_{15}, P_{16}$.
* **Condición** (para cualquiera de las dos muñecas):
  $$Y_{nariz} - Y_{muñeca} \ge 0.10 \cdot W_h$$
* **Umbral:** `RAISED_HAND_MARGIN = 0.10`. La muñeca debe quedar claramente por encima de la cabeza, no solo a la altura del hombro.

---

### Eventos 6 y 7: Señalar izquierda / Señalar derecha (Pose)
* **Landmarks:** hombro $S$, codo $E$, muñeca $W$ del mismo brazo ($11,13,15$ o $12,14,16$).
* **Condiciones simultáneas:**
  1. **Brazo extendido lateralmente:**
     $$|X_W - X_S| \ge 1.0 \cdot W_h$$
  2. **Brazo casi horizontal:**
     $$\theta = \arctan\left(\frac{|Y_W - Y_S|}{|X_W - X_S|}\right) \le 30^\circ$$
  3. **Codo recto** (ángulo interno hombro–codo–muñeca):
     $$\alpha = \arccos\left(\frac{(S-E)\cdot(W-E)}{\lVert S-E\rVert\,\lVert W-E\rVert}\right) \ge 140^\circ$$
* **Dirección:** $X_W - X_S < 0 \Rightarrow$ **Señalar izquierda**; $X_W - X_S > 0 \Rightarrow$ **Señalar derecha**.
* **Umbrales:** `POINT_MIN_EXTENSION = 1.0`, `POINT_MAX_TILT_DEG = 30`, `POINT_MIN_ELBOW_DEG = 140`.

---

### Activación condicional de MediaPipe Hands
Hands es costoso en la Raspberry Pi, por eso **solo se ejecuta** cuando se cumplen ambas condiciones:
1. Ningún gesto de Pose (mano levantada / señalar) está activo en el cuadro.
2. Alguna muñeca visible está en la **zona del pulgar**, entre un ancho de hombros por encima de la línea de hombros y la línea de caderas:
   $$\min(Y_{11}, Y_{12}) - W_h \;\le\; Y_{muñeca} \;\le\; \max(Y_{23}, Y_{24})$$

Si no hay persona o las manos están abajo/fuera de la zona, Hands no se invoca. Parámetros: `model_complexity=0`, `max_num_hands=2`, confianza mínima 0.5.

---

### Eventos 8 y 9: Pulgar arriba / Pulgar abajo (Hands)
* **Landmarks de la mano:** muñeca $H_0$, pulgar MCP $H_2$ y punta $H_4$, MCP medio $H_9$, pares (PIP, TIP) de los demás dedos: $(6,8), (10,12), (14,16), (18,20)$.
* **Tamaño de palma:** $p = \lVert H_0 - H_9 \rVert$
* **Condiciones simultáneas:**
  1. **Cuatro dedos cerrados:** para cada dedo,
     $$\lVert H_{tip} - H_0 \rVert < \lVert H_{pip} - H_0 \rVert$$
  2. **Pulgar extendido:**
     $$\lVert H_4 - H_2 \rVert \ge 0.55 \cdot p$$
  3. **Pulgar casi vertical:**
     $$\arctan\left(\frac{|X_4 - X_2|}{|Y_4 - Y_2|}\right) \le 45^\circ$$
* **Sentido:**
  * **Pulgar arriba:** $Y_4 < \min Y_i$ de todos los demás puntos de la mano (excepto $H_3$).
  * **Pulgar abajo:** $Y_4 > \max Y_i$ de todos los demás puntos de la mano (excepto $H_3$).
* **Umbrales:** `THUMB_MIN_LENGTH_RATIO = 0.55`, `THUMB_MAX_TILT_DEG = 45`.

---

### Prioridad entre gestos
$$\text{Mano levantada} \;>\; \text{Señalar izq./der.} \;>\; \text{Pulgar arriba/abajo}$$

---

### Confianza del gesto
Valor entre 0 y 1 que acompaña a cada gesto (para el HUD y el historial de `/history`):
* **Gestos de Pose** (mano levantada, señalar): promedio de la `visibility` de los landmarks usados.
  * Mano levantada: $rac{v_{nariz} + v_{muñeca}}{2}$
  * Señalar: $rac{v_{hombro} + v_{codo} + v_{muñeca}}{3}$
* **Gestos de Hands** (pulgar): score de la mano detectada que devuelve MediaPipe Hands (`handedness[i].score`).
* **Gesto confirmado:** promedio de la confianza de los 3 cuadros que lo confirmaron.

---

### Persistencia temporal (anti-parpadeo)
Clase `GestureStabilizer`. Sea $g_t$ la lectura cruda del cuadro $t$ (un gesto o *ninguno*):
$$\text{salida}_t = \begin{cases} g_t & \text{si } g_t = g_{t-1} = g_{t-2} \ \text{salida}_{t-1} & \text{en otro caso} \end{cases}$$
* **Umbral:** `GESTURE_CONFIRM_FRAMES = 3`.
* Se aplica en ambos sentidos: también hacen falta 3 cuadros sin gesto para dejar de mostrarlo. Una lectura aislada de 1–2 cuadros nunca llega a la salida.
* Si Pose pierde a la persona, el filtro se reinicia.

---

## 4. Archivos del Integrante 2

```text
Tarea04/
├── config.py                  # + sección 5: umbrales, rutas del modelo Hands y nombres de los 5 gestos
├── main_gestos.py             # Prueba local en tiempo real (Pose + Hands)
└── modules/
    └── gesture_detector.py    # GestureDetector + GestureStabilizer
```

El modelo `models/hand_landmarker.task` se descarga automáticamente la primera vez cuando se usa el backend Tasks (PC con Python 3.12+). En Raspberry Pi con `mp.solutions` no hace falta.

## 5. Uso desde el pipeline integrado (Integrante 4)

```python
landmarks, pose_event, _ = pose_detector.process(frame)
gesture = gesture_detector.process(frame, landmarks)   # str confirmado o None
evento = gesture or pose_event

if gesture:
    interpretacion = gesture_detector.get_interpretation(gesture)  # p. ej. "Saludo"
    respuesta      = gesture_detector.get_response(gesture)        # p. ej. "Responder"
    confianza      = gesture_detector.confidence                   # 0.0 a 1.0
```

## 6. Ejecución local

```bash
python main_gestos.py
```

* **`q`** / **`ESC`**: salir.
* **`s`**: guardar evidencia en `evidencias/` como `evidencia_int2_<gesto>_<timestamp>.png`.
* En pantalla: gesto confirmado con `interpretación -> respuesta (conf. %)`, lectura cruda con contador `n/3` y si Hands se ejecutó en el cuadro (`Hands: ON/off`).
