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


def test_playground_compila_teste_hardware_com_eventos_novos():
    exemplos = {e["nome"]: e["codigo"] for e in client.get("/api/exemplos").json()["exemplos"]}
    assert "teste_hardware.tupa" in exemplos
    d = client.post("/api/compilar", json={"codigo": exemplos["teste_hardware.tupa"]}).json()
    assert d["erros"] == []
    tipos = {t["tipo"] for t in d["tokens"]}
    assert "TK_ESCREVER" in tipos
    rotulos = [f["rotulo"] for f in d["ast"]["filhos"]]
    assert "Evento(iniciar)" in rotulos and "Evento(obstaculo)" in rotulos and "Evento(cartao)" in rotulos
    assert "IR: obstaculo detectado" in d["cpp"] and "nfcTentar(cartao)" in d["cpp"]
    assert d["metricas"]["cpp_total"] > d["metricas"]["tupa_total"]


def test_playground_erro_didatico_de_botao_sem_pino():
    d = client.post("/api/compilar", json={"codigo": "dispositivo t {\n ao botao(2) { }\n}"}).json()
    e = d["erros"][0]
    assert e["fase"] == "erro semantico" and e["linha"] == 2 and "botao 2" in e["mensagem"]


def test_linguagem_expoe_escrever_para_o_realce():
    palavras = client.get("/api/linguagem").json()["palavras"]
    assert palavras["escrever"] == "TK_ESCREVER" and palavras["botao"] == "TK_BOTAO"


def test_limite_de_tamanho():
    r = client.post("/api/compilar", json={"codigo": "a" * (LIMITE_BYTES + 1)})
    assert r.status_code == 413
