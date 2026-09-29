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
