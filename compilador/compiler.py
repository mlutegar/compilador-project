"""Orquestra o pipeline completo: fonte -> tokens -> AST -> semântica -> C++."""

import os

from .lexer import tokenizar
from .parser import parsear
from .semantic import analisar
from .codegen import gerar_ino


def compilar(codigo, placa=None, fonte=None):
    """Retorna o código C++/Arduino (.ino) a partir do fonte Tupã.

    Lança TupaError (ErroLexico/ErroSintatico/ErroSemantico) em caso de falha.
    """
    tokens = tokenizar(codigo)
    ast = parsear(tokens)
    analisar(ast, placa)
    return gerar_ino(ast, placa, fonte)


def compilar_arquivo(caminho_entrada, placa=None):
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        codigo = f.read()
    return compilar(codigo, placa, os.path.basename(caminho_entrada))
