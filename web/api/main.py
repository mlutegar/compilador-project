"""API do playground Tupã (FastAPI). Reaproveita o pacote `compilador`, sem duplicar lógica.

Não executa arduino-cli: só gera o .ino.
"""

import asyncio
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from compilador import __version__
from compilador.codegen import gerar_ino
from compilador.catalogo_erros import publico as catalogo_publico
from compilador.errors import TupaError
from compilador.lexer import tokenizar
from compilador.parser import parsear
from compilador.semantic import analisar
from compilador.tokens import PALAVRAS_RESERVADAS

RAIZ = Path(__file__).resolve().parents[2]
EXEMPLOS_DIR = Path(os.environ.get("TUPA_EXEMPLOS_DIR", RAIZ / "examples"))
STATIC_DIR = Path(os.environ.get("TUPA_STATIC_DIR", RAIZ / "web" / "app" / "dist"))
LIMITE_BYTES = int(os.environ.get("TUPA_LIMITE_BYTES", 20 * 1024))
TIMEOUT_S = float(os.environ.get("TUPA_TIMEOUT_S", 5))
EXTENSOES = {".tupa", ".dsl"}

app = FastAPI(title="Tupã Playground", version=__version__)


class Entrada(BaseModel):
    codigo: str


def _linhas_codigo(texto, comentario):
    """(total, de código: não vazias e sem comentário puro)."""
    linhas = texto.splitlines()
    codigo = [l for l in linhas if l.strip() and not l.strip().startswith(comentario)]
    return len(linhas), len(codigo)


def processar(codigo: str) -> dict:
    """Executa as fases em ordem, devolvendo o que foi produzido até o 1º erro."""
    resultado = {"tokens": [], "ast": None, "erros": [], "cpp": None, "metricas": None}
    try:
        tokens = tokenizar(codigo)
        resultado["tokens"] = [t.to_dict() for t in tokens]
        ast = parsear(tokens)
        resultado["ast"] = ast.to_dict()
        analisar(ast)
        resultado["cpp"] = gerar_ino(ast)
    except TupaError as e:  # o compilador para no primeiro erro
        resultado["erros"].append(e.to_dict())

    if resultado["cpp"] is not None:
        t_total, t_cod = _linhas_codigo(codigo, "#")
        c_total, c_cod = _linhas_codigo(resultado["cpp"], "//")
        resultado["metricas"] = {
            "tupa_total": t_total, "tupa_codigo": t_cod,
            "cpp_total": c_total, "cpp_codigo": c_cod,
            "razao_total": round(c_total / t_total, 1) if t_total else None,
            "razao_codigo": round(c_cod / t_cod, 1) if t_cod else None,
        }
    return resultado


@app.post("/api/compilar")
async def compilar(entrada: Entrada):
    if len(entrada.codigo.encode("utf-8")) > LIMITE_BYTES:
        raise HTTPException(413, f"código maior que o limite de {LIMITE_BYTES // 1024} KB")
    try:
        return await asyncio.wait_for(asyncio.to_thread(processar, entrada.codigo), TIMEOUT_S)
    except asyncio.TimeoutError:
        raise HTTPException(408, "tempo limite de compilação excedido")


@app.get("/api/exemplos")
def exemplos():
    itens = []
    if EXEMPLOS_DIR.is_dir():
        for p in sorted(EXEMPLOS_DIR.iterdir()):
            if p.is_file() and p.suffix in EXTENSOES:
                itens.append({"nome": p.name, "codigo": p.read_text(encoding="utf-8")})
    return {"padrao": "controle_nfc.tupa", "exemplos": itens}


@app.get("/api/linguagem")
def linguagem():
    """Palavras-chave reais do lexer (para o destaque de sintaxe do editor)."""
    return {"palavras": PALAVRAS_RESERVADAS, "comentario": "#"}


@app.get("/api/erros")
def erros():
    """Catálogo de erros (mesma fonte de docs/tabela-de-erros.md)."""
    return {"erros": catalogo_publico()}


@app.get("/api/saude")
def saude():
    return {"status": "ok", "versao": __version__}


@app.exception_handler(404)
async def _nao_encontrado(request, exc):
    if request.url.path.startswith("/api/"):
        return JSONResponse({"detail": "não encontrado"}, status_code=404)
    index = STATIC_DIR / "index.html"
    if index.is_file():
        return FileResponse(index)
    return JSONResponse({"detail": "front-end não compilado"}, status_code=404)


if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="app")
