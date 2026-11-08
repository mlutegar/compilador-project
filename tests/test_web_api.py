"""Testes do endpoint /api/compilar do playground."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from web.api.main import app, LIMITE_BYTES  # noqa: E402

client = TestClient(app)

VALIDO = open(os.path.join(os.path.dirname(__file__), "..", "examples", "controle_nfc.tupa"),
              encoding="utf-8").read()


def test_saude():
    r = client.get("/api/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_exemplos_inclui_canonico():
    r = client.get("/api/exemplos").json()
    assert "controle_nfc.tupa" in [e["nome"] for e in r["exemplos"]]


def test_compilar_valido():
    r = client.post("/api/compilar", json={"codigo": VALIDO})
    assert r.status_code == 200
    d = r.json()
    assert d["erros"] == []
    assert d["tokens"][0]["tipo"] == "TK_DISPOSITIVO"
    assert d["tokens"][-1]["tipo"] == "TK_EOF"
    assert d["ast"]["tipo"] == "Programa"
    assert "void loop()" in d["cpp"]
    assert d["metricas"]["tupa_codigo"] == 12
    assert d["metricas"]["cpp_total"] > d["metricas"]["tupa_total"]


def test_compilar_erro_semantico_led_roxo():
    codigo = VALIDO.replace("led.verde()", "led.roxo()")
    d = client.post("/api/compilar", json={"codigo": codigo}).json()
    assert len(d["erros"]) == 1
    e = d["erros"][0]
    assert e["fase"] == "erro semantico"
    assert "metodo inexistente no modulo 'led'" in e["mensagem"]
    assert e["linha"] == 11 and e["trecho"] == "led.roxo()"
    assert d["cpp"] is None
    assert d["tokens"] and d["ast"]  # fases anteriores continuam disponíveis


def test_erro_lexico_sem_cpp():
    d = client.post("/api/compilar", json={"codigo": "dispositivo x { @ }"}).json()
    assert d["erros"][0]["fase"] == "erro lexico" and d["tokens"] == []


def test_limite_de_tamanho():
    r = client.post("/api/compilar", json={"codigo": "a" * (LIMITE_BYTES + 1)})
    assert r.status_code == 413
