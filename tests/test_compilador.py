"""Testes do compilador Tupã: lexer, parser, semântica e codegen.

Rodar:
    python -m pytest tests/ -q      (se tiver pytest)
    python tests/test_compilador.py (execução direta, sem dependências)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compilador.lexer import tokenizar          # noqa: E402
from compilador.parser import parsear           # noqa: E402
from compilador.semantic import analisar        # noqa: E402
from compilador.compiler import compilar        # noqa: E402
from compilador.errors import ErroSemantico, ErroLexico, ErroSintatico  # noqa: E402

EXEMPLO = """
dispositivo controle {
    inteiro tentativas = 3;
    ao botao(1) {
        cartao = nfc.ler();
        se cartao.valido == verdadeiro {
            led.verde();
            esperar(1500);
        } senao {
            led.vermelho();
        }
    }
}
"""


# ---------- Lexer ----------
def test_lexer_tipos_de_token():
    toks = tokenizar(EXEMPLO)
    tipos = [t.tipo for t in toks]
    assert tipos[0] == "TK_DISPOSITIVO"
    assert "TK_NFC" in tipos
    assert "TK_LED" in tipos
    assert "TK_SE" in tipos and "TK_SENAO" in tipos
    assert tipos[-1] == "TK_EOF"


def test_lexer_ignora_comentarios_e_valores():
    toks = tokenizar('inteiro x = 1500; # comentario\n')
    assert not any(t.tipo == "TK_COMENTARIO" for t in toks)
    intliteral = [t for t in toks if t.tipo == "TK_INT"][0]
    assert intliteral.valor == 1500


def test_lexer_caractere_invalido():
    try:
        tokenizar("inteiro x = @;")
        assert False, "deveria ter lançado ErroLexico"
    except ErroLexico:
        pass


# ---------- Parser / AST ----------
def test_parser_estrutura():
    ast = parsear(tokenizar(EXEMPLO))
    assert ast.nome == "controle"
    tipos = [type(n).__name__ for n in ast.corpo]
    assert "DeclVar" in tipos and "Evento" in tipos


def test_parser_erro_sintatico():
    try:
        parsear(tokenizar("dispositivo x { ao botao(1) { }"))  # falta '}'
        assert False, "deveria ter lançado ErroSintatico"
    except ErroSintatico:
        pass


# ---------- Semântica ----------
def test_semantica_ok():
    analisar(parsear(tokenizar(EXEMPLO)))  # não deve lançar


def test_semantica_metodo_inexistente():
    codigo = "dispositivo t { ao botao(1) { led.roxo(); } }"
    try:
        analisar(parsear(tokenizar(codigo)))
        assert False, "deveria ter lançado ErroSemantico"
    except ErroSemantico as e:
        assert "led" in str(e) and "roxo" in str(e)
        assert "verde()" in str(e)  # lista os métodos válidos


def test_semantica_variavel_nao_declarada():
    codigo = "dispositivo t { ao botao(1) { esperar(x); } }"
    try:
        analisar(parsear(tokenizar(codigo)))
        assert False
    except ErroSemantico:
        pass


# ---------- Codegen (back-end) ----------
def test_codegen_produz_ino_valido():
    ino = compilar(EXEMPLO)
    # boilerplate Arduino essencial
    assert "void setup()" in ino
    assert "void loop()" in ino
    # tradução das construções
    assert "nfcLer()" in ino
    assert "ledVerde()" in ino
    assert "ledVermelho()" in ino
    assert "delay(1500)" in ino
    assert "digitalRead(BOTAO_1)" in ino
    assert "cartao.valido == true" in ino
    assert "#include <MFRC522.h>" in ino


def test_codegen_sem_nfc_nao_inclui_mfrc():
    codigo = "dispositivo t { ao botao(1) { led.verde(); } }"
    ino = compilar(codigo)
    assert "MFRC522" not in ino
    assert "ledVerde()" in ino


def test_repetir_gera_for():
    codigo = "dispositivo t { ao botao(1) { repetir(3) { led.verde(); } } }"
    ino = compilar(codigo)
    assert "for (int _i = 0; _i < 3; _i++)" in ino


# ---------- runner sem pytest ----------
if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"  ok  {t.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f" FAIL {t.__name__}: {e}")
        except Exception as e:
            falhas += 1
            print(f" ERR  {t.__name__}: {type(e).__name__}: {e}")
    total = len(testes)
    print(f"\n{total - falhas}/{total} testes passaram")
    sys.exit(1 if falhas else 0)
