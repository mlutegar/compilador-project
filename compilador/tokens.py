"""Definição dos tokens da linguagem Tupã (conforme docs/tabela-de-tokens.md)."""

from dataclasses import dataclass

# Palavras reservadas -> nome do token
PALAVRAS_RESERVADAS = {
    "dispositivo": "TK_DISPOSITIVO",
    "ao": "TK_AO",
    "se": "TK_SE",
    "senao": "TK_SENAO",
    "repetir": "TK_REPETIR",
    "inteiro": "TK_INTEIRO",
    "decimal": "TK_DECIMAL",
    "texto": "TK_TEXTO",
    "booleano": "TK_BOOLEANO",
    "verdadeiro": "TK_VERDADEIRO",
    "falso": "TK_FALSO",
    "retornar": "TK_RETORNAR",
    # Hardware / comandos embarcados
    "nfc": "TK_NFC",
    "ir": "TK_IR",
    "led": "TK_LED",
    "botao": "TK_BOTAO",
    "esperar": "TK_ESPERAR",
    "escrever": "TK_ESCREVER",
}

TIPOS = {"TK_INTEIRO", "TK_DECIMAL", "TK_TEXTO", "TK_BOOLEANO"}
HARDWARE = {"TK_NFC", "TK_IR", "TK_LED", "TK_BOTAO"}


@dataclass
class Token:
    tipo: str          # ex.: "TK_ID"
    lexema: str        # ex.: "cartao"
    linha: int
    coluna: int
    valor: object = None  # valor já convertido (int/float/str) quando aplicável

    def to_dict(self):
        return {"tipo": self.tipo, "lexema": self.lexema, "linha": self.linha,
                "coluna": self.coluna, "valor": self.valor}

    def __repr__(self):
        v = f", valor={self.valor!r}" if self.valor is not None else ""
        return f"Token({self.tipo}, {self.lexema!r}, L{self.linha}C{self.coluna}{v})"
