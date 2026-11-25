# API REST de Tareas	
> Este es un proyecto de práctica. Lo hice para aprender cómo se construye una API de verdad mientras me preparo para mi primera práctica profesional. Partí guardando las tareas en una lista, después las pasé a una base de datos y al final le agregué tests.


API para gestionar una lista de tareas (crear, listar, buscar, completar y eliminar), desarrollada en **Python** con **FastAPI** y persistencia en **SQLite**. Incluye tests automáticos con **pytest**.

## Tecnologías

- Python 3.14
- FastAPI + Uvicorn
- SQLite (módulo `sqlite3` de Python)
- Pydantic (validación de datos)
- pytest (tests automáticos)

## Funcionalidades

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| GET | `/tareas` | Lista todas las tareas | 200 |
| GET | `/tareas/{id}` | Obtiene una tarea por id | 200 / 404 |
| POST | `/tareas` | Crea una tarea | 201 / 422 |
| PATCH | `/tareas/{id}/completar` | Marca una tarea como completada | 200 / 404 |
| DELETE | `/tareas/{id}` | Elimina una tarea | 204 / 404 |

Puntos destacados:

- **CRUD completo** siguiendo las convenciones REST y los códigos de estado HTTP.
- **Consultas SQL parametrizadas** (`?`) para prevenir SQL Injection.
- **Validación automática** de los datos de entrada con Pydantic (responde 422 si son inválidos).
- **Tests aislados**: cada test usa su propia base de datos temporal, sin afectar los datos reales.

## Cómo ejecutarlo

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/api-tareas.git
cd api-tareas

# 2. Crear y activar un entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la API
uvicorn main:app --reload
```

Luego abrir **http://127.0.0.1:8000/docs** para probar todos los endpoints desde el navegador (documentación interactiva Swagger generada automáticamente).

## Cómo ejecutar los tests

```bash
pytest -v
```

Resultado esperado: `8 passed`.

## Estructura

```
api-tareas/
├── main.py            # API: modelos, conexión a la base de datos y endpoints
├── test_main.py       # Tests automáticos (8 casos: éxito y errores 404 / 422)
├── requirements.txt   # Dependencias
└── README.md
```

## Autor

**David Keller Valpreda** — Estudiante de Ingeniería en Computación e Informática, Universidad Andrés Bello.
