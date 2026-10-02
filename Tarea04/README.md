# AURA
## Módulo de Detección Corporal y Gestos
Proyecto 2 y Tarea 04  
Detección de postura y gestos en tiempo real.

---

## Requisitos

- Python 3.11 o 3.12
- Webcam USB o Pi Camera Module en Raspberry Pi

---

## Instalación

**PC:**
```bash
pip install -r requirements.txt
```

**Raspberry Pi:**
```bash
# OpenCV via apt 
sudo apt install python3-opencv

pip install -r requirements-pi.txt
```

---

## Ejecución

```bash
python main.py
```

Al iniciar se descarga automáticamente el modelo de MediaPipe si no existe en `models/`.

---

## Configuración

Todos los parámetros están en `config.py`. 

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `CAMERA_INDEX` | `0` | Índice de la cámara (`0` = primera disponible) |
| `USE_PI_CAMERA` | `False` | Cambiar a `True` en Raspberry Pi con Pi Camera Module |
| `FRAME_WIDTH / HEIGHT` | `640 / 480` | Resolución fija (no cambiar para compatibilidad con la Pi) |
| `GESTURE_CONFIRM_FRAMES` | `3` | Cuadros consecutivos para confirmar un gesto |
| `PROXIMITY_SHOULDER_RATIO_MIN` | `0.35` | Umbral de "Persona se acerca" |

### Pi Camera Module

En `config.py`, cambiar:
```python
USE_PI_CAMERA = True
```

Esto activa el backend `CAP_V4L2`. Si la cámara no aparece en `/dev/video0`, ajustar también `CAMERA_INDEX`.

---

## Estructura

```bash
Tarea04/
├── main.py                    # Punto de entrada principal
├── main_pose.py               # Prueba aislada solo con Pose (sin gestos ni HUD)
├── config.py                  # Parámetros y umbrales
├── requirements.txt           # Dependencias para PC
├── requirements-pi.txt        # Dependencias para Raspberry Pi
├── models/                    # Modelos MediaPipe (se descargan automáticamente)
├── assets/aura/               # Sprites del robot virtual
├── evidencias/                # Capturas guardadas con tecla s
└── modules/
    ├── pose_detector.py       # Detección corporal (Persona aparece/desaparece/se acerca, Brazos cruzados)
    ├── gesture_detector.py    # Gestos de manos (Mano levantada, Señalar, Pulgar arriba/abajo)
    ├── agent_controller.py    # Máquina de estados: conecta eventos con Robot2D
    ├── robot_2d.py            # Robot virtual y sprites
    └── hud.py                 # Panel informativo sobre el video
```
