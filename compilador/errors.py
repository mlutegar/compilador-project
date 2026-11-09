"""Erros do compilador Tupã, com posição (linha/coluna) e mensagem amigável em português."""


class TupaError(Exception):
    """Erro base do compilador, com fase, linha e coluna."""

    fase = "erro"

    def __init__(self, mensagem, linha=None, coluna=None, trecho=None, codigo=None):
        self.mensagem = mensagem
        self.codigo = codigo
        self.linha = linha
        self.coluna = coluna
        self.trecho = trecho
        super().__init__(self.formatar())

    def to_dict(self):
        return {"codigo": self.codigo, "fase": self.fase, "mensagem": self.mensagem, "linha": self.linha,
                "coluna": self.coluna, "trecho": self.trecho,
                "texto": self.formatar()}

    def formatar(self):
        pos = ""
        if self.linha is not None:
            pos = f" - linha {self.linha}"
            if self.coluna is not None:
                pos += f", coluna {self.coluna}"
        cod = f" [{self.codigo}]" if self.codigo else ""
        texto = f"{self.fase}{cod}{pos}\n    {self.mensagem}"
        if self.trecho:
            texto += f"\n    {self.trecho}"
        return texto


class ErroLexico(TupaError):
    fase = "erro lexico"


class ErroSintatico(TupaError):
    fase = "erro sintatico"


class ErroSemantico(TupaError):
    fase = "erro semantico"
