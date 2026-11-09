"""CLI do compilador Tupã.

Uso:
    tupa build <arquivo.tupa> [-o pasta] [--placa p]  # gera <pasta>/<pasta>.ino
    tupa tokens <arquivo.tupa>                 # lista os tokens (análise léxica)
    tupa ast <arquivo.tupa>                    # imprime a AST (análise sintática)
"""

import argparse
import os
import sys

from .lexer import tokenizar
from .parser import parsear
from .semantic import analisar
from .codegen import gerar_ino
from .astprint import render_programa
from .errors import TupaError
from .placa import carregar_placa, ErroPlaca, PLACA_PADRAO


def _ler(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def _cmd_build(args):
    placa = carregar_placa(args.placa)
    codigo = _ler(args.arquivo)
    tokens = tokenizar(codigo)
    ast = parsear(tokens)
    analisar(ast, placa)
    ino = gerar_ino(ast, placa, os.path.basename(args.arquivo))

    # O arduino-cli exige <pasta>/<pasta>.ino. -o indica a pasta do sketch
    # (se terminar em .ino, usa o nome sem a extensão como pasta).
    if args.saida:
        pasta = args.saida[:-4] if args.saida.endswith(".ino") else args.saida
    else:
        pasta = os.path.join("output", os.path.splitext(os.path.basename(args.arquivo))[0])
    pasta = pasta.rstrip("/\\")
    destino = os.path.join(pasta, os.path.basename(pasta) + ".ino")

    os.makedirs(pasta, exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write(ino)
    print(f"-> {destino}")
    return 0


def _cmd_tokens(args):
    tokens = tokenizar(_ler(args.arquivo))
    for t in tokens:
        val = f"  = {t.valor!r}" if t.valor is not None else ""
        print(f"L{t.linha:>3}C{t.coluna:<3} {t.tipo:<16} {t.lexema!r}{val}")
    return 0


def _cmd_ast(args):
    ast = parsear(tokenizar(_ler(args.arquivo)))
    print(render_programa(ast))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="tupa", description="Compilador da linguagem Tupã (DSL -> C++/Arduino).")
    sub = p.add_subparsers(dest="comando", required=True)

    b = sub.add_parser("build", help="compila .tupa para .ino")
    b.add_argument("arquivo")
    b.add_argument("-o", "--saida",
                   help="pasta do sketch de saída; grava <pasta>/<pasta>.ino (padrão: output/<nome>)")
    b.add_argument("--placa", default=PLACA_PADRAO,
                   help="placa-alvo: nome em compilador/placas/ ou caminho de um .json (padrão: %(default)s)")
    b.set_defaults(func=_cmd_build)

    t = sub.add_parser("tokens", help="mostra a análise léxica (tokens)")
    t.add_argument("arquivo")
    t.set_defaults(func=_cmd_tokens)

    a = sub.add_parser("ast", help="mostra a AST (análise sintática)")
    a.add_argument("arquivo")
    a.set_defaults(func=_cmd_ast)
    return p


def main(argv=None):
    # Garante UTF-8 na saída (necessário no console do Windows / cp1252).
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except TupaError as e:
        print(f"\n{e}\n", file=sys.stderr)
        print("compilacao interrompida: 1 erro", file=sys.stderr)
        return 1
    except ErroPlaca as e:
        print(f"erro de placa: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"arquivo não encontrado: {args.arquivo}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
