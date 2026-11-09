"""Gera docs/tabela-de-erros.md a partir de compilador/catalogo_erros.py.

Uso: python tools/gerar_tabela_erros.py           (grava o arquivo)
     python tools/gerar_tabela_erros.py --stdout
"""

import html
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from compilador.catalogo_erros import CATALOGO  # noqa: E402

DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "tabela-de-erros.md")

CABECALHO = """# Tabela de erros do compilador Tupã

> Arquivo gerado por `python tools/gerar_tabela_erros.py` a partir de `compilador/catalogo_erros.py`.
> Não edite à mão. `tests/test_erros.py` executa o exemplo de cada linha e exige o código da linha,
> e confere que este arquivo é idêntico ao gerado.

Cada erro tem um código estável: **L** léxico, **S** sintático, **E** semântico, **G** geração/placa.
O código aparece no CLI (`erro semantico [E19] - linha 3, coluna 5`), na API (campo `codigo` de cada item de `erros`)
e no site (aba Erros). O compilador para no primeiro erro. As mensagens têm partes variáveis entre `{chaves}`.

Notas:
- O gerador de código (`codegen.py`) não emite erros: o que chega a ele já passou pela análise semântica.
- Os erros G01 a G05 vêm da leitura da placa e dos arquivos pelo CLI (saída com status 2); L, S e E saem com status 1.
- Erros HTTP da API (413 código maior que 20 KB, 408 tempo limite) não são erros do compilador e não têm código.
- Linhas `interno` são defesas do compilador que nenhum programa Tupã dispara; não têm exemplo.
- Nos exemplos, `dispositivo d { ... }` envolve o trecho mínimo que dispara o erro.

"""


def _cel(texto, codigo=False):
    t = html.escape(texto, quote=False).replace("|", "&#124;").replace("\n", "<br>")
    if codigo:
        return f"<code>{t}</code>"
    return t


def gerar():
    linhas = ["| Código | Fase | Condição que dispara | Mensagem exata | Exemplo mínimo | Como corrigir |",
              "|---|---|---|---|---|---|"]
    for e in CATALOGO:
        fase = e["fase"] + (" (interno)" if e["interno"] else "")
        linhas.append("| " + " | ".join([
            f"**{e['codigo']}**", fase, _cel(e["condicao"]), _cel(e["mensagem"], True),
            _cel(e["exemplo"], True), _cel(e["correcao"])]) + " |")
    return CABECALHO + "\n".join(linhas) + "\n"


if __name__ == "__main__":
    texto = gerar()
    if "--stdout" in sys.argv:
        print(texto)
    else:
        with open(DESTINO, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        print(f"-> {os.path.normpath(DESTINO)} ({len(CATALOGO)} erros)")
