"""Gera index.html (autocontido) e roteiro.md a partir de fonte.html + slides.py.

Confere no repositório cada número citado nos slides (falha se divergir). Uso: python apresentacao/build.py
"""
import base64
import io
import json
import pathlib
import re
import sys

from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

import slides  # noqa: E402
from compilador.lexer import _ESPECIFICACAO, _IGNORAR  # noqa: E402
from compilador.tokens import PALAVRAS_RESERVADAS  # noqa: E402
from compilador import ast_nodes, catalogo_erros  # noqa: E402


def b64(img, fmt, **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    return f"data:{'image/png' if fmt == 'PNG' else 'image/jpeg'};base64," + base64.b64encode(buf.getvalue()).decode()


def codigo(rel, comentario):
    """Linhas de código: sem linhas vazias nem comentários (mesma regra do artigo)."""
    return sum(1 for l in slides.ler(rel).splitlines() if l.strip() and not l.strip().startswith(comentario))


# ----------------------------------------------------------- números do repositório
tokens = len([nome for nome, _ in _ESPECIFICACAO if nome not in _IGNORAR]) + len(PALAVRAS_RESERVADAS) + 1
nos = len([c for c in vars(ast_nodes).values()
           if isinstance(c, type) and issubclass(c, ast_nodes.No) and c is not ast_nodes.No])
cat = catalogo_erros.CATALOGO
por_fase = {k: sum(1 for e in cat if e["codigo"].startswith(k)) for k in "LSEG"}
n = dict(
    tupa_nfc=codigo("examples/controle_nfc.tupa", "#"), tupa_th=codigo("examples/teste_hardware.tupa", "#"),
    ger_nfc=codigo("firmware/controle_nfc_gerado/controle_nfc_gerado.ino", "//"),
    ger_th=codigo("firmware/teste_hardware_gerado/teste_hardware_gerado.ino", "//"),
    manual_th=codigo("firmware/teste_hardware.ino", "//"), testes=98, **por_fase)
n["r_nfc"] = f"{n['ger_nfc'] / n['tupa_nfc']:.1f}".replace(".", ",")
n["r_th"] = f"{n['ger_th'] / n['tupa_th']:.1f}".replace(".", ",")

esperado = dict(tokens=44, nos=17, erros=40, L=1, S=13, E=21, G=5, tupa_nfc=12, ger_nfc=100, tupa_th=23, ger_th=112,
                manual_th=51, r_nfc="8,3", r_th="4,9")
real = dict(n, tokens=tokens, nos=nos, erros=len(cat))
dif = {k: (v, real[k]) for k, v in esperado.items() if real[k] != v}
assert not dif, f"números divergem do repositório (esperado, real): {dif}"
doc = slides.ler("docs/compilacao.md")
assert "293740 bytes (22%)" in doc and "22308 bytes (6%)" in doc, "flash/RAM divergem de docs/compilacao.md"
assert "tupa.mlutegar.com" in slides.ler("README.md") and "MIT" in slides.ler("LICENSE")
print("números conferidos:", {k: real[k] for k in esperado})

# ----------------------------------------------------------- imagens
logo = Image.open(RAIZ / "web/app/public/tupa-icone.png").convert("RGB").resize((400, 400), Image.LANCZOS)
play = Image.open(AQUI / "assets/playground.png").convert("RGB")
gravar = Image.open(AQUI / "assets/como-gravar.png").convert("RGB").resize((700, 450), Image.LANCZOS)
f1 = Image.open(RAIZ / "artigo/figuras/prototipo_vista_superior.jpg").convert("RGB")
f2 = Image.open(RAIZ / "artigo/figuras/prototipo_visao_geral.jpg").convert("RGB")
qr = (AQUI / "assets/qr.svg").read_text(encoding="utf-8")
qr = re.sub(r"<\?xml.*?\?>", "", qr)
qr = re.sub(r'width="[^"]*" height="[^"]*"', 'style="width:100%;height:100%;display:block"', qr, count=1)

# ----------------------------------------------------------- slides
S = slides.montar(n)
assert len(S) == 14
partes = []
total = 0
for i, s in enumerate(S, 1):
    nota = f'<b>{s["quem"]} · {s["tempo"] // 60}:{s["tempo"] % 60:02d}.</b> {s["fala"]}'
    mini = '<div class="mini"></div>' if s["mini"] else ""
    rod = f'<div class="rodape"><span>Tupã · banca LFC · IBMEC</span><span>{i:02d}</span></div>' if s["mini"] else ""
    corpo = s["html"]
    if "</h2>" in corpo:
        corpo = corpo.replace("</h2>", '</h2><div class="cx">', 1) + "</div>"
    partes.append(f'<section class="slide" data-n="{i}">{mini}{corpo}{rod}<template class="notas">{nota}</template></section>')
    total += s["tempo"]
assert total == 600, f"fala soma {total} s, esperado 600"

KW = sorted(set(PALAVRAS_RESERVADAS) - {"nfc", "ir", "led", "botao"})
page = (AQUI / "fonte.html").read_text(encoding="utf-8")
page = (page.replace("{{LOGO}}", b64(logo, "PNG", optimize=True))
        .replace("{{KW}}", json.dumps(KW))
        .replace("{{SLIDES}}", "\n".join(partes))
        .replace("{{PLAY}}", b64(play, "PNG", optimize=True))
        .replace("{{GRAVAR}}", b64(gravar, "JPEG", quality=85))
        .replace("{{FOTO1}}", b64(f1, "JPEG", quality=85))
        .replace("{{FOTO2}}", b64(f2, "JPEG", quality=85))
        .replace("{{QR}}", qr))
assert "{{" not in page.split("<script>")[0].split("</style>")[1], "placeholder sem substituir"
(AQUI / "index.html").write_text(page, encoding="utf-8")
print("index.html", len(page) // 1024, "KB")


# ----------------------------------------------------------- roteiro.md
def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


quem_t = {}
for s in S:
    quem_t[s["quem"]] = quem_t.get(s["quem"], 0) + s["tempo"]
slides_de = {q: [i for i, s in enumerate(S, 1) if s["quem"] == q] for q in quem_t}
titulos = ["Capa", "Problema", "Lacuna", "A linguagem", "Arquitetura", "Léxico", "Sintático", "Semântico",
           "Tabela de erros", "Geração de código", "Métricas e compilação", "Playground", "Hardware e demo", "Conclusão"]

linhas = ["| # | Slide | Quem | Tempo | Fala |", "|---|---|---|---|---|"]
for i, s in enumerate(S, 1):
    t = mmss(s["tempo"]) if i != 13 else mmss(s["tempo"]) + " + demo 3:00"
    linhas.append(f"| {i} | {titulos[i - 1]} | {s['quem']} | {t} | {s['fala']} |")
tabela = "\n".join(linhas)
div = "\n".join(f"| {q} | {', '.join(map(str, slides_de[q]))} | {mmss(quem_t[q])} |" for q in
                ["Michel", "André", "Felipe", "Guilherme"])

roteiro = f"""# Roteiro da apresentação final do Tupã (P16)

Banca de Linguagens Formais e Compiladores, IBMEC. Deck em `apresentacao/index.html` (setas navegam, **N** mostra as notas, **F** tela cheia) e versão impressa em `apresentacao.pdf`. Este arquivo é gerado por `python apresentacao/build.py`; as mesmas falas aparecem nas notas dos slides.

**Tempo:** 10:00 de fala em 14 slides, mais 3:00 de demonstração ao vivo no slide 13.
**Equipe:** Michel Lutegar (Michel), André Costa (André), Felipe Dutrain (Felipe), Guilherme Lopes (Guilherme).

## Fala por slide

{tabela}

## Divisão entre os quatro

| Quem | Slides | Tempo de fala |
|---|---|---|
{div}

Total: {mmss(total)}, mais a demonstração. Na demo: André abre o site, compila e baixa o `.ino`; Guilherme grava e mexe na placa; Felipe lê o Monitor Serial; Michel narra e faz a ponte com a banca. Cada um fala cerca de 2:30 e participa da demo.

## Demonstração (3 min)

1. Abrir tupa.mlutegar.com, escolher `controle_nfc.tupa`, compilar (Ctrl+Enter). Mostrar a aba C++ e a aba Como gravar.
2. Baixar o `.ino` e abrir na Arduino IDE: placa ESP32 Wrover Module, Monitor Serial em 115200. Gravar.
3. No Serial aparece a checagem do RC522 (`RC522 versao: 0x.. -> OK`).
4. Apertar o botão com o cartão `33 7A 87 F7`: LED verde, "acesso liberado".
5. Apertar o botão com o cartão `33 8F BD F7`: LED vermelho, "acesso negado".
6. Apertar o botão sem cartão: após 3 s, "Cartao: nenhum detectado em 3 s" e "acesso negado".

% TODO (placa): o `.ino` gerado de `controle_nfc.tupa` ainda não foi gravado e testado nos três casos. Fazer isso antes da banca. Até hoje só o `teste_hardware.ino` manual foi validado em bancada (26/10/2026).

## Plano B da demonstração

- **Vídeo tutorial:** deixar o vídeo (roteiro em `roteiro-video-tutorial.md.pdf`, na raiz do repositório) baixado no computador, fora do navegador, e abrir se a placa ou a USB falhar. O arquivo de vídeo não está no repositório: conferir que está na máquina da apresentação.
- **Playground:** se a placa falhar mas houver internet, compilar `controle_nfc` em tupa.mlutegar.com ao vivo e mostrar as abas Tokens, AST, Erros (provocar `led.roxo()` e ler o `[E19]`) e C++. Isso cobre as quatro fases sem hardware.
- **Sem internet:** usar `python -m compilador build examples/controle_nfc.tupa` no terminal e abrir `firmware/controle_nfc_gerado/controle_nfc_gerado.ino`, já versionado; mostrar as fotos do protótipo e o Serial da bancada em `artigo/figuras/`.
- **Decisão:** se em 30 s a gravação não funcionar, passar ao vídeo sem pedir desculpas e voltar ao slide 14.

## Antes da banca

- [ ] % TODO (placa): gravar o `.ino` gerado e testar os três casos.
- [ ] Compilar o `controle_nfc` no site e baixar o `.ino` com antecedência, como cópia local.
- [ ] Placa ligada por USB, Arduino IDE em ESP32 Wrover Module, Monitor Serial em 115200, cartões `33 7A 87 F7` (liberado) e `33 8F BD F7` (negado) à mão.
- [ ] Abrir `apresentacao/index.html` em tela cheia (F), testar a tecla N, ter o vídeo e o `apresentacao.pdf` à mão.

## Perguntas prováveis da banca

**1. Por que regex e não um autômato escrito à mão?**
Cada token do Tupã é uma linguagem regular, então a regex equivale a um autômato finito; usamos o motor de `re` em vez de escrever a tabela de transição, o que dá menos código e menos chance de erro. A especificação continua formal (cada um dos 44 tokens tem sua regex em `docs/especificacao-lexica.md`). A ordem das alternativas resolve os prefixos: `==` antes de `=`.

**2. Por que descendente recursivo?**
A gramática é pequena e cabe em um token de lookahead. Uma função por regra deixa o código quase igual à EBNF, a precedência fica explícita na cadeia de regras, e as mensagens de erro ("esperado X, encontrado Y") saem naturalmente. Um gerador de parser traria dependência e uma etapa extra de build sem ganho para este tamanho de linguagem.

**3. Como garantem que a tabela de erros bate com o código?**
`compilador/catalogo_erros.py` é a fonte única; `tools/gerar_tabela_erros.py` gera `docs/tabela-de-erros.md` a partir dele. `tests/test_erros.py` executa o exemplo de cada código e exige o código e a mensagem, confere que o arquivo gerado é idêntico ao versionado e que todo código usado no fonte existe no catálogo. Os 98 testes passam. E06 e E15 são defesas internas, sem exemplo.

**4. Por que transpilar para C++ e não gerar binário?**
O ecossistema do ESP32 (core Arduino, biblioteca MFRC522, `arduino-cli`) já resolve toolchain, bibliotecas e gravação. Gerar `.ino` mantém o trabalho na linguagem e nas fases do compilador, e o resultado é legível, com comentários `// [arquivo:linha]` ligando cada bloco ao `.tupa`. O custo em memória é pequeno: cerca de 293 KB de flash contra 291 KB do manual.

**5. Quais são as limitações?**
Só a ESP32-WROVER-DEV (outra placa pede um JSON novo); um erro por vez, sem recuperação; o módulo `ir` é só sensor de obstáculo; sem OTA; a linguagem não foi avaliada com estudantes; e a redução de linhas mede digitação poupada, não facilidade de aprender. Tudo isso está na seção de limitações do artigo.

**6. Por que o compilador para no primeiro erro?**
Porque a linguagem é pequena, o programa típico tem poucas linhas e um erro de sintaxe costuma gerar erros em cascata. Parar no primeiro, com código, linha, coluna e o que era esperado, é mais claro para o iniciante. Recuperação de erros está nos próximos passos.

**7. Por que pinos e UIDs ficam no arquivo da placa e não na linguagem?**
Para o programa ficar portátil e legível: `ao botao(1)` não diz em que GPIO o botão está. A lista de UIDs ficou na placa porque era a opção que pedia menos mudança (nenhum token, regra ou nó novo). Declarar a lista no `.tupa` é uma evolução possível.

**8. O código gerado já foi testado na placa?**
Compila de verdade com arduino-cli 1.5.1 e core esp32 3.3.12 (4 sketches, sem erro nem aviso), e o hardware e a pinagem foram validados em bancada com o `teste_hardware.ino` manual em 26/10/2026. A gravação do `.ino` gerado a partir do Tupã é a demonstração ao vivo. % TODO (placa): confirmar o resultado antes da banca e ajustar esta resposta.

## Fontes dos números

44 tokens e regex mestre (`compilador/lexer.py`, `docs/tabela-de-tokens.md`); 17 nós de AST (`compilador/ast_nodes.py`); 40 códigos de erro (`docs/tabela-de-erros.md`); 98 testes (`pytest`); linhas e razões (`artigo/main.tex`, tabela de comparação, recontadas por `build.py`); flash e RAM (`docs/compilacao.md`); hardware e custo (`artigo/main.tex`).
"""
(AQUI / "roteiro.md").write_text(roteiro, encoding="utf-8")
print("roteiro.md ok")
