"""A tabela de erros (docs/tabela-de-erros.md) e o compilador não podem divergir.

Cada linha do catálogo: o exemplo mínimo realmente gera aquele código, com a mensagem da tabela.
"""

import copy
import json
import os
import re
import sys

import pytest

RAIZ = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, RAIZ)

from compilador import cli  # noqa: E402
from compilador.catalogo_erros import CATALOGO, publico  # noqa: E402
from compilador.compiler import compilar  # noqa: E402
from compilador.errors import TupaError  # noqa: E402
from compilador.placa import ErroPlaca, carregar_placa  # noqa: E402
from tools.gerar_tabela_erros import gerar, DESTINO  # noqa: E402

ATIVOS = [e for e in CATALOGO if not e["interno"]]
FASES = {"L": "erro lexico", "S": "erro sintatico", "E": "erro semantico"}


def _regex(mensagem):
    partes = re.split(r"\{[a-z]+\}", mensagem)
    return re.compile("^" + ".*".join(re.escape(p) for p in partes) + "$", re.S)


def _placa_json(tmp_path, alteracoes):
    with open(os.path.join(RAIZ, "compilador", "placas", "esp32_wrover.json"), encoding="utf-8") as f:
        d = json.load(f)
    for k, v in alteracoes.items():
        if v is None:
            d.pop(k)
        else:
            d[k] = v
    caminho = tmp_path / "placa_teste.json"
    caminho.write_text(json.dumps(d), encoding="utf-8")
    return str(caminho)


def test_codigos_unicos_e_bem_formados():
    codigos = [e["codigo"] for e in CATALOGO]
    assert len(codigos) == len(set(codigos))
    assert all(re.fullmatch(r"[LSEG]\d{2}", c) for c in codigos)


@pytest.mark.parametrize("e", ATIVOS, ids=lambda e: e["codigo"])
def test_exemplo_gera_o_codigo_da_tabela(e, tmp_path, capsys):
    tipo, arg = e["gatilho"]
    if tipo in ("tupa", "tupa_sem_ir"):
        placa = carregar_placa()
        if tipo == "tupa_sem_ir":
            placa = copy.deepcopy(placa)
            placa.pinos.pop("ir")
        with pytest.raises(TupaError) as exc:
            compilar(arg, placa)
        erro = exc.value
        assert erro.codigo == e["codigo"]
        assert erro.fase == FASES[e["codigo"][0]]
        assert _regex(e["mensagem"]).match(erro.mensagem), erro.mensagem
        assert erro.to_dict()["codigo"] == e["codigo"]
        assert f"[{e['codigo']}]" in erro.formatar()
    elif tipo in ("placa_json", "placa_nome"):
        alvo = _placa_json(tmp_path, arg) if tipo == "placa_json" else arg
        with pytest.raises(ErroPlaca) as exc:
            carregar_placa(alvo)
        assert exc.value.codigo == e["codigo"]
        assert _regex(e["mensagem"]).match(exc.value.mensagem), exc.value.mensagem
    else:  # cli_arquivo
        assert cli.main(["build", str(tmp_path / arg)]) == 2
        err = capsys.readouterr().err
        assert f"[{e['codigo']}]" in err
        assert "arquivo não encontrado" in err


def test_cli_mostra_codigo_de_erro_de_placa(capsys):
    assert cli.main(["build", os.path.join(RAIZ, "examples", "controle_nfc.tupa"),
                     "--placa", "inexistente", "-o", "x"]) == 2
    assert "erro de placa [G01]" in capsys.readouterr().err


def test_cli_mostra_codigo_de_erro_do_compilador(tmp_path, capsys):
    f = tmp_path / "a.tupa"
    f.write_text("dispositivo d {\n led.roxo();\n}", encoding="utf-8")
    assert cli.main(["build", str(f), "-o", str(tmp_path / "o")]) == 1
    assert "erro semantico [E19] - linha 2" in capsys.readouterr().err


def test_todo_codigo_do_fonte_esta_no_catalogo_e_vice_versa():
    usados = set()
    for nome in ("lexer.py", "parser.py", "semantic.py", "placa.py", "cli.py"):
        with open(os.path.join(RAIZ, "compilador", nome), encoding="utf-8") as f:
            usados |= set(re.findall(r'["\[]([LSEG]\d{2})["\]]', f.read()))
    usados.discard("S99")  # reserva do parser para um `esperado` sem código mapeado (teste abaixo)
    catalogados = {e["codigo"] for e in CATALOGO}
    assert usados == catalogados


def test_tabela_markdown_esta_sincronizada_com_o_catalogo():
    with open(DESTINO, encoding="utf-8") as f:
        assert f.read() == gerar(), "rode: python tools/gerar_tabela_erros.py"


def test_parser_cobre_todas_as_descricoes_esperadas():
    from compilador.parser import CODIGOS_ESPERADO
    assert len(CODIGOS_ESPERADO) == 10
    assert set(CODIGOS_ESPERADO.values()) <= {e["codigo"] for e in CATALOGO}


def test_catalogo_publico_sem_gatilho():
    assert all("gatilho" not in e for e in publico())


def test_tabela_de_simbolos_do_controle_nfc():
    from compilador.lexer import tokenizar
    from compilador.parser import parsear
    from compilador.semantic import tabela_de_simbolos
    with open(os.path.join(RAIZ, "examples", "controle_nfc.tupa"), encoding="utf-8") as f:
        simbolos = tabela_de_simbolos(parsear(tokenizar(f.read())))
    assert [(s["nome"], s["tipo"], s["escopo"], s["linha"]) for s in simbolos] == [
        ("tentativas", "inteiro", "global", 3), ("cartao", "cartao", "ao botao(1)", 8)]
