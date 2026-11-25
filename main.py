# =====================================================================
#  API DE TAREAS - Etapa 2 (CRUD con SQLite) - VERSIÓN COMENTADA
#  Ejecutar:  uvicorn main:app --reload
#  Probar:    http://127.0.0.1:8000/docs
# =====================================================================

# ---------------------------------------------------------------------
# 1. IMPORTS
# ---------------------------------------------------------------------
import sqlite3                               # Librería de Python para usar SQLite (viene incluida, no se instala).

from fastapi import FastAPI, HTTPException   # FastAPI: crea la API | HTTPException: responde errores (404, etc.)
from pydantic import BaseModel               # BaseModel: define la "forma" de los datos y los valida.


# ---------------------------------------------------------------------
# 2. CREAR LA APLICACIÓN
# ---------------------------------------------------------------------
app = FastAPI(title="API de tareas")         # El "garzón". "uvicorn main:app" = archivo main.py, variable app.


# ---------------------------------------------------------------------
# 3. MODELOS (moldes de los datos)
# ---------------------------------------------------------------------
class TareaCrear(BaseModel):     # Lo que el CLIENTE envía al crear.
    titulo: str                  # Obligatorio. Si falta -> 422 automático.
    descripcion: str = ""        # Opcional (valor por defecto "").


class Tarea(TareaCrear):         # Lo que la API DEVUELVE. HERENCIA: titulo + descripcion...
    id: int                      # ...+ id (lo asigna la base de datos)...
    hecha: bool = False          # ...+ estado (False al crear).


# ---------------------------------------------------------------------
# 4. BASE DE DATOS (SQLite = un archivo "tareas.db" que queda guardado en la carpeta)
#    Antes: lista en RAM (pizarra que se borra). Ahora: archivo en disco (cuaderno).
# ---------------------------------------------------------------------
DB = "tareas.db"                 # Nombre del archivo. En MAYÚSCULAS porque es una constante.


def conectar():
    con = sqlite3.connect(DB)            # Abre el archivo de la base. Si no existe, lo CREA.
    con.row_factory = sqlite3.Row        # Permite leer columnas por nombre: fila["titulo"] en vez de fila[1].
    return con


def crear_tabla():
    with conectar() as con:              # "with": al terminar el bloque hace COMMIT (guarda) o ROLLBACK si hubo error.
        con.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo      TEXT    NOT NULL,
                descripcion TEXT    NOT NULL DEFAULT '',
                hecha       INTEGER NOT NULL DEFAULT 0
            )
        """)
        # IF NOT EXISTS  -> solo la crea la primera vez (no falla al reiniciar).
        # PRIMARY KEY    -> identificador único de cada fila (tiene índice: buscar por id es muy rápido).
        # AUTOINCREMENT  -> la base asigna el id sola: 1, 2, 3...
        # NOT NULL       -> campo obligatorio.
        # DEFAULT        -> valor si no se envía.
        # hecha INTEGER  -> SQLite no tiene bool: 0 = no hecha, 1 = hecha.


crear_tabla()                            # Se ejecuta UNA vez al arrancar la API.


def fila_a_tarea(fila):
    """TRADUCTOR: convierte una fila de la base de datos en un objeto Tarea."""
    return Tarea(
        id=fila["id"],
        titulo=fila["titulo"],
        descripcion=fila["descripcion"],
        hecha=bool(fila["hecha"]),       # 0 -> False, 1 -> True
    )


# ---------------------------------------------------------------------
# 5. ENDPOINTS
#    REGLA DE ORO: valores del usuario SIEMPRE con "?" -> evita SQL INJECTION.
#    Nunca armar el SQL con f-strings: f"... WHERE id = {tarea_id}"  ❌
# ---------------------------------------------------------------------

@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la API de tareas, mira si funciona :D"}


# ---------- READ (leer todas) ----------
@app.get("/tareas")
def listar_tareas():
    with conectar() as con:
        filas = con.execute("SELECT * FROM tareas ORDER BY id").fetchall()
        # SELECT *  -> todas las columnas | ORDER BY id -> ordenadas | fetchall() -> TODAS las filas (lista)
    return [fila_a_tarea(f) for f in filas]
    # List comprehension: traduce cada fila a Tarea en una línea.


# ---------- READ (leer una) ----------
@app.get("/tareas/{tarea_id}")
def obtener_tarea(tarea_id: int):
    with conectar() as con:
        fila = con.execute(
            "SELECT * FROM tareas WHERE id = ?", (tarea_id,)   # WHERE filtra | ? se reemplaza por tarea_id
        ).fetchone()                                           # fetchone() -> UNA fila, o None si no hay
        # (tarea_id,) -> la COMA es obligatoria: es una tupla de un elemento.
    if fila is None:                                           # No existe -> 404
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return fila_a_tarea(fila)


# ---------- CREATE (crear) ----------
@app.post("/tareas", status_code=201)
def crear_tarea(datos: TareaCrear):
    with conectar() as con:
        cursor = con.execute(
            "INSERT INTO tareas (titulo, descripcion) VALUES (?, ?)",   # id y hecha los pone la base (AUTOINCREMENT / DEFAULT)
            (datos.titulo, datos.descripcion),                         # valores para los ?, en orden
        )
        fila = con.execute(
            "SELECT * FROM tareas WHERE id = ?", (cursor.lastrowid,)   # lastrowid = id que se acaba de asignar
        ).fetchone()
    return fila_a_tarea(fila)                                          # 201 con la tarea creada


# ---------- UPDATE (actualizar) ----------
@app.patch("/tareas/{tarea_id}/completar")
def completar_tarea(tarea_id: int):
    obtener_tarea(tarea_id)                      # Solo VERIFICA que exista (404 si no). Principio DRY.
    with conectar() as con:
        con.execute("UPDATE tareas SET hecha = 1 WHERE id = ?", (tarea_id,))
        #  Sin WHERE se actualizarían TODAS las filas.
    return obtener_tarea(tarea_id)               # Lee de nuevo y devuelve la tarea ya actualizada.


# ---------- DELETE (eliminar) ----------
@app.delete("/tareas/{tarea_id}", status_code=204)
def eliminar_tarea(tarea_id: int):
    obtener_tarea(tarea_id)                      # 404 si no existe.
    with conectar() as con:
        con.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
        #  Sin WHERE se borrarían TODAS las filas.
    # Sin return -> 204 No Content.


# =====================================================================
# RESUMEN: ENDPOINT -> SQL
# ---------------------------------------------------------------------
#  GET    /tareas                 -> SELECT * FROM tareas ORDER BY id
#  GET    /tareas/{id}            -> SELECT * FROM tareas WHERE id = ?
#  POST   /tareas                 -> INSERT INTO tareas (titulo, descripcion) VALUES (?, ?)
#  PATCH  /tareas/{id}/completar  -> UPDATE tareas SET hecha = 1 WHERE id = ?
#  DELETE /tareas/{id}            -> DELETE FROM tareas WHERE id = ?
#
#  Preguntas típicas de entrevista:
#   - ¿Qué es SQL Injection y cómo se evita? -> parámetros "?" (consultas parametrizadas)
#   - ¿Qué es una PRIMARY KEY? -> identificador único con índice (búsqueda rápida)
#   - ¿Qué pasa si olvidas el WHERE en UPDATE/DELETE? -> afecta TODAS las filas
#   - ¿Qué hace COMMIT / ROLLBACK? -> guardar cambios / deshacerlos si hubo error
# =====================================================================