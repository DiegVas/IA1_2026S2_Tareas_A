from pathlib import Path
from typing import List
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pyswip import Prolog

app = FastAPI(title="Motor de Inferencia de Inventario (Prolog + FastAPI)")

# Configuracion de CORS para permitir peticiones desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar base de conocimiento en Prolog mediante PySwip
BASE_DIR = Path(__file__).resolve().parent
PROLOG_FILE = BASE_DIR / "inventario.pl"

prolog = Prolog()
prolog.consult(str(PROLOG_FILE).replace("\\", "/"))

# Esquema de respuesta JSON
class InventarioResponse(BaseModel):
    item_buscado: str
    encontrado: bool
    total_items: int
    inventario_invertido: List[str]
    inventario_unico: List[str]
    inventario_ordenado: List[str]
    mensaje: str

def ejecutar_consulta_prolog(item: str) -> dict:
    """Ejecuta procesar_inventario/5 en Prolog y unifica variables de respuesta."""
    item_limpio = item.strip().lower().replace("'", "\\'")
    query_str = f"procesar_inventario('{item_limpio}', TotalItems, InventarioInvertido, InventarioUnico, InventarioOrdenado)"
    soluciones = list(prolog.query(query_str))

    if soluciones:
        # Item encontrado: extrae variables unificadas por Prolog
        sol = soluciones[0]
        return {
            "item_buscado": item,
            "encontrado": True,
            "total_items": int(sol["TotalItems"]),
            "inventario_invertido": [str(x) for x in sol["InventarioInvertido"]],
            "inventario_unico": [str(x) for x in sol["InventarioUnico"]],
            "inventario_ordenado": [str(x) for x in sol["InventarioOrdenado"]],
            "mensaje": f"El ítem '{item}' fue encontrado en el inventario."
        }
    else:
        # Item no encontrado (member/2 fallo): obtiene listas generales con regla auxiliar
        gen_sol = list(prolog.query("obtener_inventario_completo(TotalItems, InventarioGeneral, InventarioInvertido, InventarioUnico, InventarioOrdenado)"))[0]
        return {
            "item_buscado": item,
            "encontrado": False,
            "total_items": int(gen_sol["TotalItems"]),
            "inventario_invertido": [str(x) for x in gen_sol["InventarioInvertido"]],
            "inventario_unico": [str(x) for x in gen_sol["InventarioUnico"]],
            "inventario_ordenado": [str(x) for x in gen_sol["InventarioOrdenado"]],
            "mensaje": f"El ítem '{item}' no se encuentra en el inventario."
        }

# Endpoints GET
@app.get("/api/inventario", response_model=InventarioResponse, tags=["Inventario"])
def consultar_inventario_query(item: str = Query(..., description="Nombre del ítem a buscar")):
    if not item or not item.strip():
        raise HTTPException(status_code=400, detail="Debe ingresar un ítem válido.")
    return ejecutar_consulta_prolog(item)

@app.get("/api/inventario/{item}", response_model=InventarioResponse, tags=["Inventario"])
def consultar_inventario_path(item: str):
    if not item or not item.strip():
        raise HTTPException(status_code=400, detail="Debe ingresar un ítem válido.")
    return ejecutar_consulta_prolog(item)

# Servir archivos estaticos del frontend
app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")

@app.get("/", include_in_schema=False)
def get_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/styles.css", include_in_schema=False)
def get_css():
    return FileResponse(BASE_DIR / "styles.css")

@app.get("/app.js", include_in_schema=False)
def get_js():
    return FileResponse(BASE_DIR / "app.js")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
