"""Analisador sintático (parser) do Tupã — recursivo descendente.

Consome a lista de tokens e produz a AST (ast_nodes.Programa).
"""

from . import ast_nodes as A
from .tokens import TIPOS
from .errors import ErroSintatico


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    # ---------- utilidades ----------
    @property
    def atual(self):
        return self.tokens[self.i]

    def _avanca(self):
        tok = self.tokens[self.i]
        if tok.tipo != "TK_EOF":
            self.i += 1
        return tok

    def _verifica(self, *tipos):
        return self.atual.tipo in tipos

    def _aceita(self, *tipos):
        if self.atual.tipo in tipos:
            return self._avanca()
        return None

    def _espera(self, tipo, descricao):
        if self.atual.tipo == tipo:
            return self._avanca()
        tok = self.atual
        raise ErroSintatico(
            f"esperado {descricao}, encontrado {tok.lexema!r}", tok.linha, tok.coluna
        )

    # ---------- ponto de entrada ----------
    def parse(self):
        prog = self._programa()
        if self.atual.tipo != "TK_EOF":
            tok = self.atual
            raise ErroSintatico(
                f"código inesperado após o fim do programa: {tok.lexema!r}",
                tok.linha, tok.coluna,
            )
        return prog

    # dispositivo ID { corpo }
    def _programa(self):
        tok = self._espera("TK_DISPOSITIVO", "'dispositivo'")
        nome = self._espera("TK_ID", "nome do dispositivo").lexema
        self._espera("TK_ABRE_CHAVE", "'{'")
        corpo = []
        while not self._verifica("TK_FECHA_CHAVE", "TK_EOF"):
            corpo.append(self._item_topo())
        self._espera("TK_FECHA_CHAVE", "'}'")
        return A.Programa(nome, corpo, tok.linha, tok.coluna)

    def _item_topo(self):
        if self._verifica("TK_AO"):
            return self._evento()
        return self._comando()

    # ao botao(N) { ... }  |  ao iniciar { ... }  |  ao obstaculo { ... }  |  ao cartao { ... }
    # Só 'botao' é palavra reservada. Os demais nomes de evento são TK_ID (palavras
    # contextuais) porque 'cartao' já é nome de variável em programas existentes;
    # a análise semântica confere se o nome é um evento conhecido.
    def _evento(self):
        tok = self._espera("TK_AO", "'ao'")
        if self._aceita("TK_BOTAO"):
            self._espera("TK_ABRE_PAR", "'('")
            num = self._espera("TK_INT", "número do botão")
            self._espera("TK_FECHA_PAR", "')'")
            corpo = self._bloco()
            return A.Evento("botao", num.valor, corpo, tok.linha, tok.coluna)
        if self.atual.tipo != "TK_ID":
            raise ErroSintatico(
                f"esperado nome do evento (botao, iniciar, obstaculo, cartao), "
                f"encontrado {self.atual.lexema!r}", self.atual.linha, self.atual.coluna,
            )
        nome = self._avanca().lexema
        corpo = self._bloco()
        return A.Evento(nome, None, corpo, tok.linha, tok.coluna)

    def _bloco(self):
        self._espera("TK_ABRE_CHAVE", "'{'")
        cmds = []
        while not self._verifica("TK_FECHA_CHAVE", "TK_EOF"):
            cmds.append(self._comando())
        self._espera("TK_FECHA_CHAVE", "'}'")
        return cmds

    # ---------- comandos ----------
    def _comando(self):
        t = self.atual.tipo
        if t in TIPOS:
            return self._decl_var()
        if t == "TK_SE":
            return self._se()
        if t == "TK_REPETIR":
            return self._repetir()
        if t == "TK_ESPERAR":
            return self._esperar()
        if t == "TK_ESCREVER":
            return self._escrever()
        if t == "TK_RETORNAR":
            return self._retornar()
        # senão: atribuição ou chamada (expressão-comando)
        return self._atrib_ou_chamada()

    def _decl_var(self):
        tok = self._avanca()  # tipo
        tipo = tok.lexema
        nome = self._espera("TK_ID", "nome da variável").lexema
        valor = None
        if self._aceita("TK_ATRIB"):
            valor = self._expr()
        self._espera("TK_PONTO_VIRGULA", "';'")
        return A.DeclVar(tipo, nome, valor, tok.linha, tok.coluna)

    def _se(self):
        tok = self._espera("TK_SE", "'se'")
        cond = self._expr()
        entao = self._bloco()
        senao = None
        if self._aceita("TK_SENAO"):
            senao = self._bloco()
        return A.Se(cond, entao, senao, tok.linha, tok.coluna)

    def _repetir(self):
        tok = self._espera("TK_REPETIR", "'repetir'")
        self._espera("TK_ABRE_PAR", "'('")
        vezes = self._expr()
        self._espera("TK_FECHA_PAR", "')'")
        corpo = self._bloco()
        return A.Repetir(vezes, corpo, tok.linha, tok.coluna)

    def _esperar(self):
        tok = self._espera("TK_ESPERAR", "'esperar'")
        self._espera("TK_ABRE_PAR", "'('")
        tempo = self._expr()
        self._espera("TK_FECHA_PAR", "')'")
        self._espera("TK_PONTO_VIRGULA", "';'")
        return A.Esperar(tempo, tok.linha, tok.coluna)

    def _escrever(self):
        tok = self._espera("TK_ESCREVER", "'escrever'")
        self._espera("TK_ABRE_PAR", "'('")
        valor = self._expr()
        self._espera("TK_FECHA_PAR", "')'")
        self._espera("TK_PONTO_VIRGULA", "';'")
        return A.Escrever(valor, tok.linha, tok.coluna)

    def _retornar(self):
        tok = self._espera("TK_RETORNAR", "'retornar'")
        valor = None
        if not self._verifica("TK_PONTO_VIRGULA"):
            valor = self._expr()
        self._espera("TK_PONTO_VIRGULA", "';'")
        return A.Retornar(valor, tok.linha, tok.coluna)

    def _atrib_ou_chamada(self):
        expr = self._expr()
        if self._verifica("TK_ATRIB"):
            tok = self._avanca()
            valor = self._expr()
            self._espera("TK_PONTO_VIRGULA", "';'")
            return A.Atribuicao(expr, valor, tok.linha, tok.coluna)
        self._espera("TK_PONTO_VIRGULA", "';'")
        return A.ExprComando(expr, getattr(expr, "linha", 0), getattr(expr, "coluna", 0))

    # ---------- expressões (precedência) ----------
    def _expr(self):
        return self._ou()

    def _ou(self):
        no = self._e()
        while self._verifica("TK_OU"):
            tok = self._avanca()
            no = A.Binaria("||", no, self._e(), tok.linha, tok.coluna)
        return no

    def _e(self):
        no = self._igualdade()
        while self._verifica("TK_E"):
            tok = self._avanca()
            no = A.Binaria("&&", no, self._igualdade(), tok.linha, tok.coluna)
        return no

    def _igualdade(self):
        no = self._comparacao()
        while self._verifica("TK_IGUAL", "TK_DIFERENTE"):
            tok = self._avanca()
            op = "==" if tok.tipo == "TK_IGUAL" else "!="
            no = A.Binaria(op, no, self._comparacao(), tok.linha, tok.coluna)
        return no

    def _comparacao(self):
        no = self._termo()
        mapa = {"TK_MAIOR": ">", "TK_MENOR": "<", "TK_MAIOR_IGUAL": ">=", "TK_MENOR_IGUAL": "<="}
        while self.atual.tipo in mapa:
            tok = self._avanca()
            no = A.Binaria(mapa[tok.tipo], no, self._termo(), tok.linha, tok.coluna)
        return no

    def _termo(self):
        no = self._fator()
        mapa = {"TK_SOMA": "+", "TK_SUB": "-"}
        while self.atual.tipo in mapa:
            tok = self._avanca()
            no = A.Binaria(mapa[tok.tipo], no, self._fator(), tok.linha, tok.coluna)
        return no

    def _fator(self):
        no = self._unaria()
        mapa = {"TK_MULT": "*", "TK_DIV": "/"}
        while self.atual.tipo in mapa:
            tok = self._avanca()
            no = A.Binaria(mapa[tok.tipo], no, self._unaria(), tok.linha, tok.coluna)
        return no

    def _unaria(self):
        if self._verifica("TK_NAO", "TK_SUB"):
            tok = self._avanca()
            op = "!" if tok.tipo == "TK_NAO" else "-"
            return A.Unaria(op, self._unaria(), tok.linha, tok.coluna)
        return self._posfixo()

    def _posfixo(self):
        no = self._primario()
        while True:
            if self._verifica("TK_PONTO"):
                tok = self._avanca()
                nome = self._espera("TK_ID", "nome do membro").lexema
                no = A.AcessoMembro(no, nome, tok.linha, tok.coluna)
            elif self._verifica("TK_ABRE_PAR"):
                tok = self._avanca()
                args = self._argumentos()
                self._espera("TK_FECHA_PAR", "')'")
                no = A.Chamada(no, args, tok.linha, tok.coluna)
            else:
                break
        return no

    def _argumentos(self):
        args = []
        if self._verifica("TK_FECHA_PAR"):
            return args
        args.append(self._expr())
        while self._aceita("TK_VIRGULA"):
            args.append(self._expr())
        return args

    def _primario(self):
        tok = self.atual
        if tok.tipo == "TK_INT":
            self._avanca(); return A.Literal("int", tok.valor, tok.linha, tok.coluna)
        if tok.tipo == "TK_FLOAT":
            self._avanca(); return A.Literal("float", tok.valor, tok.linha, tok.coluna)
        if tok.tipo == "TK_STRING":
            self._avanca(); return A.Literal("texto", tok.valor, tok.linha, tok.coluna)
        if tok.tipo == "TK_VERDADEIRO":
            self._avanca(); return A.Literal("booleano", True, tok.linha, tok.coluna)
        if tok.tipo == "TK_FALSO":
            self._avanca(); return A.Literal("booleano", False, tok.linha, tok.coluna)
        if tok.tipo in ("TK_NFC", "TK_IR", "TK_LED", "TK_BOTAO"):
            self._avanca(); return A.Hardware(tok.lexema, tok.linha, tok.coluna)
        if tok.tipo == "TK_ID":
            self._avanca(); return A.Identificador(tok.lexema, tok.linha, tok.coluna)
        if tok.tipo == "TK_ABRE_PAR":
            self._avanca()
            no = self._expr()
            self._espera("TK_FECHA_PAR", "')'")
            return no
        raise ErroSintatico(
            f"expressão esperada, encontrado {tok.lexema!r}", tok.linha, tok.coluna
        )


def parsear(tokens):
    return Parser(tokens).parse()
