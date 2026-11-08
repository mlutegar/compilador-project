"""Analisador léxico (lexer) do Tupã.

Transforma o texto-fonte em uma lista de Tokens, ignorando espaços e comentários.
Segue a especificação de docs/tabela-de-tokens.md.
"""

import re

from .tokens import Token, PALAVRAS_RESERVADAS
from .errors import ErroLexico

# Ordem importa: operadores de 2 caracteres antes dos de 1.
_ESPECIFICACAO = [
    ("TK_ESPACO",       r"[ \t\r\n]+"),
    ("TK_COMENTARIO",   r"\#[^\n]*"),
    ("TK_FLOAT",        r"[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?"),
    ("TK_INT",          r"[0-9]+"),
    ("TK_STRING",       r"\"[^\"\n]*\""),
    ("TK_ID",           r"[a-zA-Z][a-zA-Z0-9_]*"),
    ("TK_IGUAL",        r"=="),
    ("TK_DIFERENTE",    r"!="),
    ("TK_MAIOR_IGUAL",  r">="),
    ("TK_MENOR_IGUAL",  r"<="),
    ("TK_E",            r"&&"),
    ("TK_OU",           r"\|\|"),
    ("TK_ATRIB",        r"="),
    ("TK_MAIOR",        r">"),
    ("TK_MENOR",        r"<"),
    ("TK_NAO",          r"!"),
    ("TK_SOMA",         r"\+"),
    ("TK_SUB",          r"-"),
    ("TK_MULT",         r"\*"),
    ("TK_DIV",          r"/"),
    ("TK_ABRE_PAR",     r"\("),
    ("TK_FECHA_PAR",    r"\)"),
    ("TK_ABRE_CHAVE",   r"\{"),
    ("TK_FECHA_CHAVE",  r"\}"),
    ("TK_VIRGULA",      r","),
    ("TK_PONTO",        r"\."),
    ("TK_PONTO_VIRGULA", r";"),
]

_MESTRE = re.compile("|".join(f"(?P<{nome}>{padrao})" for nome, padrao in _ESPECIFICACAO))

# Tokens que o lexer reconhece mas NÃO envia ao parser.
_IGNORAR = {"TK_ESPACO", "TK_COMENTARIO"}


def tokenizar(codigo, incluir_ignorados=False):
    """Recebe o código-fonte (str) e devolve uma lista de Token.

    Se `incluir_ignorados` for True, também retorna espaços e comentários
    (útil para depuração/documentação da análise léxica).
    """
    tokens = []
    linha = 1
    inicio_linha = 0  # índice do último '\n' + 1, para calcular coluna
    pos = 0

    for m in _MESTRE.finditer(codigo):
        # Detecta caracteres não reconhecidos entre o fim do último match e este.
        if m.start() != pos:
            trecho = codigo[pos:m.start()]
            col = pos - inicio_linha + 1
            raise ErroLexico(
                f"caractere inesperado: {trecho.strip()!r}", linha, col
            )
        pos = m.end()

        tipo = m.lastgroup
        lexema = m.group()
        col = m.start() - inicio_linha + 1

        if tipo == "TK_ESPACO":
            # Atualiza contagem de linhas/colunas.
            quebras = lexema.count("\n")
            if quebras:
                linha += quebras
                inicio_linha = m.start() + lexema.rfind("\n") + 1
            if incluir_ignorados:
                tokens.append(Token(tipo, lexema, linha, col))
            continue

        if tipo == "TK_COMENTARIO":
            if incluir_ignorados:
                tokens.append(Token(tipo, lexema, linha, col))
            continue

        valor = None
        if tipo == "TK_ID":
            # Palavra reservada? (inclui hardware e comandos)
            reservada = PALAVRAS_RESERVADAS.get(lexema)
            if reservada:
                tipo = reservada
        elif tipo == "TK_INT":
            valor = int(lexema)
        elif tipo == "TK_FLOAT":
            valor = float(lexema)
        elif tipo == "TK_STRING":
            valor = lexema[1:-1]  # remove aspas

        tokens.append(Token(tipo, lexema, linha, col, valor))

    # Caractere inesperado no final?
    if pos != len(codigo):
        col = pos - inicio_linha + 1
        raise ErroLexico(f"caractere inesperado: {codigo[pos:].strip()!r}", linha, col)

    tokens.append(Token("TK_EOF", "", linha, 1))
    return tokens
