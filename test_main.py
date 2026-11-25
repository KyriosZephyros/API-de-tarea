import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB", str(tmp_path / "test.db"))
    main.crear_tabla()
    return TestClient(main.app)


def test_inicio(client):
    respuesta = client.get("/")
    assert respuesta.status_code == 200
    assert "mensaje" in respuesta.json()


def test_crear_tarea(client):
    respuesta = client.post("/tareas", json={"titulo": "Estudiar"})
    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["id"] == 1
    assert datos["titulo"] == "Estudiar"
    assert datos["hecha"] is False


def test_crear_sin_titulo_da_422(client):
    respuesta = client.post("/tareas", json={})
    assert respuesta.status_code == 422


def test_listar_tareas(client):
    client.post("/tareas", json={"titulo": "Uno"})
    client.post("/tareas", json={"titulo": "Dos"})
    respuesta = client.get("/tareas")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_obtener_tarea_inexistente_da_404(client):
    respuesta = client.get("/tareas/99")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Tarea no encontrada"


def test_completar_tarea(client):
    client.post("/tareas", json={"titulo": "Estudiar"})
    respuesta = client.patch("/tareas/1/completar")
    assert respuesta.status_code == 200
    assert respuesta.json()["hecha"] is True


def test_eliminar_tarea(client):
    client.post("/tareas", json={"titulo": "Borrar"})
    respuesta = client.delete("/tareas/1")
    assert respuesta.status_code == 204
    assert client.get("/tareas/1").status_code == 404


def test_eliminar_inexistente_da_404(client):
    assert client.delete("/tareas/99").status_code == 404
