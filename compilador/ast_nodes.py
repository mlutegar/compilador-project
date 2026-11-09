"""Nós da Árvore Sintática Abstrata (AST) do Tupã."""

from dataclasses import dataclass, field
from typing import List, Optional


class No:
    """Base de todos os nós da AST."""
    linha: int = 0
    coluna: int = 0

    def to_dict(self):
        """Árvore serializável: {tipo, rotulo, linha, coluna, filhos:[{campo, ...}]}."""
        from .astprint import _rotulo, _filhos  # import tardio (evita ciclo)
        filhos = []
        for campo, filho in _filhos(self):
            d = filho.to_dict()
            d["campo"] = campo
            filhos.append(d)
        return {"tipo": type(self).__name__, "rotulo": _rotulo(self),
                "linha": self.linha, "coluna": self.coluna, "filhos": filhos}


# ---------- Programa e estrutura ----------
@dataclass
class Programa(No):
    nome: str
    corpo: List[No]           # declarações, eventos e comandos de topo
    linha: int = 0
    coluna: int = 0


@dataclass
class DeclVar(No):
    tipo: str                 # 'inteiro' | 'decimal' | 'texto' | 'booleano'
    nome: str
    valor: Optional[No] = None
    linha: int = 0
    coluna: int = 0


@dataclass
class Evento(No):
    tipo_evento: str          # 'botao' | 'iniciar' | 'obstaculo' | 'cartao' (ou nome desconhecido)
    numero: Optional[int]     # só para 'botao'
    corpo: List[No] = field(default_factory=list)
    linha: int = 0
    coluna: int = 0


# ---------- Comandos ----------
@dataclass
class Atribuicao(No):
    alvo: No                  # Identificador ou AcessoMembro
    valor: No
    linha: int = 0
    coluna: int = 0


@dataclass
class Se(No):
    condicao: No
    entao: List[No]
    senao: Optional[List[No]] = None
    linha: int = 0
    coluna: int = 0


@dataclass
class Repetir(No):
    vezes: No
    corpo: List[No]
    linha: int = 0
    coluna: int = 0


@dataclass
class Esperar(No):
    tempo: No
    linha: int = 0
    coluna: int = 0


@dataclass
class Escrever(No):
    """escrever(expr);  ->  Serial.println(expr)"""
    valor: No
    linha: int = 0
    coluna: int = 0


@dataclass
class Retornar(No):
    valor: Optional[No] = None
    linha: int = 0
    coluna: int = 0


@dataclass
class ExprComando(No):
    """Uma expressão usada como comando (ex.: led.verde();)."""
    expr: No
    linha: int = 0
    coluna: int = 0


# ---------- Expressões ----------
@dataclass
class Binaria(No):
    op: str
    esq: No
    dir: No
    linha: int = 0
    coluna: int = 0


@dataclass
class Unaria(No):
    op: str
    operando: No
    linha: int = 0
    coluna: int = 0


@dataclass
class Literal(No):
    tipo: str                 # 'int' | 'float' | 'texto' | 'booleano'
    valor: object
    linha: int = 0
    coluna: int = 0


@dataclass
class Identificador(No):
    nome: str
    linha: int = 0
    coluna: int = 0


@dataclass
class Hardware(No):
    nome: str                 # 'nfc' | 'ir' | 'led' | 'botao'
    linha: int = 0
    coluna: int = 0


@dataclass
class AcessoMembro(No):
    objeto: No
    membro: str
    linha: int = 0
    coluna: int = 0


@dataclass
class Chamada(No):
    alvo: No                  # normalmente AcessoMembro (led.verde) ou Identificador
    args: List[No] = field(default_factory=list)
    linha: int = 0
    coluna: int = 0
