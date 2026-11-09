"""Descrição da placa-alvo (pinos, FQBN, biblioteca, UIDs autorizados).

O codegen e a análise semântica leem tudo daqui: nenhum pino fica fixo no gerador.
Os arquivos ficam em compilador/placas/<nome>.json.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List

PLACA_PADRAO = "esp32_wrover"
_DIR_PLACAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placas")


class ErroPlaca(Exception):
    """Placa inexistente ou arquivo de placa inválido."""

    def __init__(self, mensagem, codigo=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.codigo = codigo

    def to_dict(self):
        return {"codigo": self.codigo, "fase": "erro de placa", "mensagem": self.mensagem}


@dataclass
class Placa:
    nome: str
    descricao: str
    fqbn: str
    biblioteca_nfc: str
    pinos: dict
    spi: dict
    eletrica: dict
    timeout_nfc_ms: int
    uids_autorizados: List[List[int]] = field(default_factory=list)

    @property
    def botoes(self) -> Dict[int, int]:
        return {int(n): int(p) for n, p in self.pinos.get("botoes", {}).items()}


def _uid_para_bytes(texto):
    try:
        bs = [int(p, 16) for p in texto.split()]
    except ValueError:
        raise ErroPlaca(f"UID inválido na placa: {texto!r} (use bytes em hexadecimal, ex.: '33 7A 87 F7')", "G02")
    if len(bs) not in (4, 7, 10) or any(not 0 <= b <= 255 for b in bs):
        raise ErroPlaca(f"UID inválido na placa: {texto!r} (um UID tem 4, 7 ou 10 bytes)", "G03")
    return bs


def placas_disponiveis():
    return sorted(f[:-5] for f in os.listdir(_DIR_PLACAS) if f.endswith(".json"))


def carregar_placa(nome=None):
    """Carrega uma placa pelo nome (ex.: 'esp32_wrover') ou pelo caminho de um .json."""
    nome = nome or PLACA_PADRAO
    if nome.endswith(".json") or os.sep in nome or "/" in nome:
        caminho = nome
    else:
        caminho = os.path.join(_DIR_PLACAS, nome + ".json")
    if not os.path.isfile(caminho):
        raise ErroPlaca(
            f"placa '{nome}' não encontrada. Disponíveis: {', '.join(placas_disponiveis())}",
            "G01",
        )
    with open(caminho, "r", encoding="utf-8") as f:
        d = json.load(f)
    try:
        return Placa(
            nome=d["nome"], descricao=d.get("descricao", ""), fqbn=d["fqbn"],
            biblioteca_nfc=d.get("biblioteca_nfc", "MFRC522"),
            pinos=d["pinos"], spi=d["spi"], eletrica=d["eletrica"],
            timeout_nfc_ms=int(d["nfc"].get("timeout_ms", 3000)),
            uids_autorizados=[_uid_para_bytes(u) for u in d["nfc"].get("uids_autorizados", [])],
        )
    except KeyError as e:
        raise ErroPlaca(f"arquivo de placa '{caminho}' sem o campo {e}", "G04")
