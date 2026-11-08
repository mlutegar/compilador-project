"""Orquestra o pipeline completo: fonte -> tokens -> AST -> semântica -> C++."""

from .lexer import tokenizar
from .parser import parsear
from .semantic import analisar
from .codegen import gerar_ino


def compilar(codigo):
    """Retorna o código C++/Arduino (.ino) a partir do fonte Tupã.

    Lança TupaError (ErroLexico/ErroSintatico/ErroSemantico) em caso de falha.
    """
    tokens = tokenizar(codigo)
    ast = parsear(tokens)
    analisar(ast)
    return gerar_ino(ast)


def compilar_arquivo(caminho_entrada):
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        codigo = f.read()
    return compilar(codigo)
