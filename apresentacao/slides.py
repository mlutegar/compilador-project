"""Conteúdo dos slides: HTML, quem fala, tempo e fala (as notas e o roteiro saem daqui).

Os números e trechos de código vêm do repositório (ver build.py, que confere cada número).
"""
import html
import pathlib
import textwrap

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FOLD = "// ..."
FOLD2 = "  // ..."


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


def trecho(rel, *partes, fold=FOLD):
    """Junta intervalos (a, b) de linhas (1-based, inclusivos) de um arquivo, com marcador de corte."""
    linhas = ler(rel).splitlines()
    out = []
    for p in partes:
        if isinstance(p, str):
            out.append(p)
        else:
            out.extend(linhas[p[0] - 1:p[1]])
    return "\n".join(out)


def pre(cls, texto, estilo=""):
    return f'<pre class="{cls}" style="{estilo}">{html.escape(texto)}</pre>'


def painel(titulo, direita, corpo, estilo=""):
    return (f'<div class="painel" style="{estilo}"><div class="tit"><span>{titulo}</span><b>{direita}</b></div>'
            f'{corpo}</div>')


# ---------------------------------------------------------------- diagramas
def svg_ast():
    """AST do controle_nfc, rótulos iguais aos de `tupa ast`. Nós folha recebem colunas; pais ficam no centro dos filhos."""
    # (tipo, detalhe, filhos, rótulo da aresta, cor)
    def N(t, d="", f=(), aresta="", cor="o"):
        return dict(t=t, d=d, f=list(f), a=aresta, cor=cor)
    arvore = N("Programa", "controle", [
        N("DeclVar", "tentativas", [N("Literal", "3", cor="a", aresta="valor")]),
        N("Evento", "botao 1", [
            N("Atribuicao", "=", [
                N("Id", "cartao", cor="v", aresta="alvo"),
                N("Chamada", "nfc.ler()", cor="v", aresta="valor")]),
            N("Se", "", [
                N("Binaria", "==", [
                    N("Membro", "cartao.valido", cor="v"),
                    N("Literal", "verdadeiro", cor="a")], aresta="cond", cor="v"),
                N("Comando", "led.verde()", aresta="então"),
                N("Esperar", "1500"),
                N("Comando", "led.vermelho()", aresta="senão")]),
        ])])
    W, BW, BH, DY = 1136, 134, 44, 74
    folhas = []

    def colunas(n, nivel):
        n["nivel"] = nivel
        if not n["f"]:
            n["col"] = len(folhas); folhas.append(n)
        else:
            for c in n["f"]:
                colunas(c, nivel + 1)
            n["col"] = (n["f"][0]["col"] + n["f"][-1]["col"]) / 2
    colunas(arvore, 0)
    nl = max(f["nivel"] for f in folhas)
    passo = (W - BW) / (len(folhas) - 1)
    cores = {"o": "#FF7A1A", "v": "#2EE6A6", "a": "#FFD166"}
    linhas, caixas = [], []

    def desenhar(n):
        x = BW / 2 + n["col"] * passo
        y = 4 + n["nivel"] * DY
        for c in n["f"]:
            cx = BW / 2 + c["col"] * passo
            cy = 4 + c["nivel"] * DY
            linhas.append(f'<path d="M{x:.0f},{y + BH} C{x:.0f},{y + BH + 20} {cx:.0f},{cy - 20} {cx:.0f},{cy}" '
                          f'stroke="#3B4552" stroke-width="2" fill="none"/>')
            if c["a"]:
                linhas.append(f'<text x="{x + (cx - x) * 0.62:.0f}" y="{y + BH + (cy - y - BH) * 0.6 + 4:.0f}" text-anchor="middle" '
                              f'font-size="12" fill="#98A2B3" font-family="JetBrains Mono,monospace" '
                              f'style="paint-order:stroke;stroke:#0E1116;stroke-width:4px">{c["a"]}</text>')
            desenhar(c)
        cor = cores[n["cor"]]
        caixas.append(
            f'<rect x="{x - BW / 2:.0f}" y="{y}" width="{BW}" height="{BH}" rx="8" fill="#161B22" stroke="{cor}" stroke-width="2"/>'
            f'<text x="{x:.0f}" y="{y + (17 if n["d"] else 27)}" text-anchor="middle" font-size="15" font-weight="700" '
            f'fill="{cor}" font-family="Inter,sans-serif">{n["t"]}</text>'
            + (f'<text x="{x:.0f}" y="{y + 36}" text-anchor="middle" font-size="13" fill="#F5F7FA" '
               f'font-family="JetBrains Mono,monospace">{html.escape(n["d"])}</text>' if n["d"] else ""))
    desenhar(arvore)
    h = 4 + nl * DY + BH + 4
    return f'<svg viewBox="0 0 {W} {h}" width="{W}" height="{h}">{"".join(linhas)}{"".join(caixas)}</svg>'


CMD = {"Léxico": "tupa tokens", "Sintático": "tupa ast", "Semântico": "tupa simbolos", "Geração": "tupa build"}


def svg_pipeline():
    fases = [("Léxico", "tokens"), ("Sintático", "AST"), ("Semântico", "símbolos"), ("Geração", "C++")]
    W = 1136
    bw, gap = 118, 24
    itens = [(".tupa", "texto-fonte", "#98A2B3")] + [(f, o, "#FF7A1A") for f, o in fases] + \
            [(".ino", "sketch", "#2EE6A6"), ("arduino-cli", "binário", "#98A2B3"), ("ESP32", "firmware", "#2EE6A6")]
    x0 = (W - (len(itens) * bw + (len(itens) - 1) * gap)) / 2
    out = ['<defs><marker id="seta" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
           '<path d="M0,0 L10,5 L0,10 z" fill="#98A2B3"/></marker></defs>']
    y, h = 60, 96
    pos = []
    for i, (t, o, cor) in enumerate(itens):
        x = x0 + i * (bw + gap)
        pos.append(x)
        fase = cor == "#FF7A1A"
        out.append(f'<rect x="{x:.0f}" y="{y}" width="{bw}" height="{h}" rx="12" fill="{"#2A1A0C" if fase else "#161B22"}" '
                   f'stroke="{cor}" stroke-width="2"/>')
        out.append(f'<text x="{x + bw / 2:.0f}" y="{y + 36}" text-anchor="middle" font-size="{22 if len(t) < 9 else 16}" '
                   f'font-weight="700" fill="#F5F7FA" font-family="{"JetBrains Mono,monospace" if t[0] in ".aE" and not fase else "Inter,sans-serif"}">{t}</text>')
        out.append(f'<text x="{x + bw / 2:.0f}" y="{y + 58}" text-anchor="middle" font-size="15" fill="{cor}" '
                   f'font-family="Inter,sans-serif">{o}</text>')
        if fase:
            out.append(f'<text x="{x + bw / 2:.0f}" y="{y + 80}" text-anchor="middle" font-size="13" fill="#FFD1A0" '
                       f'font-family="JetBrains Mono,monospace">{CMD[t]}</text>')
        if i:
            out.append(f'<line x1="{pos[i - 1] + bw + 3:.0f}" y1="{y + h / 2}" x2="{x - 4:.0f}" y2="{y + h / 2}" '
                       f'stroke="#98A2B3" stroke-width="2" marker-end="url(#seta)"/>')
    # chave do compilador
    xa, xb = pos[1], pos[4] + bw
    out.append(f'<path d="M{xa:.0f},{y - 14} V{y - 24} H{xb:.0f} V{y - 14}" stroke="#FF7A1A" stroke-width="2" fill="none"/>')
    out.append(f'<text x="{(xa + xb) / 2:.0f}" y="{y - 32}" text-anchor="middle" font-size="15" font-weight="700" '
               f'fill="#FF7A1A" font-family="Inter,sans-serif" letter-spacing="2">COMPILADOR TUPÃ (PYTHON)</text>')
    # arquivo de placa
    py = y + h + 80
    bx = pos[3]
    out.append(f'<rect x="{bx:.0f}" y="{py}" width="{pos[4] + bw - bx:.0f}" height="52" rx="12" fill="#161B22" stroke="#C792FF" stroke-width="2"/>')
    out.append(f'<text x="{(bx + pos[4] + bw) / 2:.0f}" y="{py + 22}" text-anchor="middle" font-size="16" font-weight="700" fill="#F5F7FA" font-family="JetBrains Mono,monospace">esp32_wrover.json</text>')
    out.append(f'<text x="{(bx + pos[4] + bw) / 2:.0f}" y="{py + 42}" text-anchor="middle" font-size="13.5" fill="#C792FF" font-family="Inter,sans-serif">pinos, SPI, FQBN, UIDs</text>')
    for xx in (pos[3] + bw / 2, pos[4] + bw / 2):
        out.append(f'<line x1="{xx:.0f}" y1="{py - 3}" x2="{xx:.0f}" y2="{y + h + 5}" stroke="#C792FF" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#seta)"/>')
    # erro
    ex = pos[2] + bw / 2
    out.append(f'<path d="M{ex:.0f},{y + h + 3} V{y + h + 36}" stroke="#FF5A6A" stroke-width="2" fill="none" marker-end="url(#seta)"/>')
    out.append(f'<text x="{ex - 6:.0f}" y="{y + h + 58}" text-anchor="end" font-size="14" fill="#FF5A6A" font-family="Inter,sans-serif">erro com código</text>')
    return f'<svg viewBox="0 0 {W} {py + 60}" width="{W}" height="{py + 60}">{"".join(out)}</svg>'


def tabela_tokens(codigo="cartao = nfc.ler();"):
    from compilador.lexer import tokenizar
    linhas = []
    for t in tokenizar(codigo):
        if t.tipo == "TK_EOF":
            continue
        cor = "h" if t.tipo == "TK_NFC" else ("k" if t.tipo in ("TK_ATRIB",) else "")
        linhas.append(f'<tr><td style="font-family:var(--mono)">{html.escape(t.lexema)}</td>'
                      f'<td class="{cor}">{t.tipo}</td><td class="cinza">{t.linha}:{t.coluna}</td></tr>')
    return ('<table style="font-size:15px"><tr><th>lexema</th><th>token</th><th>lin:col</th></tr>'
            + "".join(linhas) + "</table>")


# ---------------------------------------------------------------- slides
def montar(n):
    """n: contagens conferidas no repositório (dict)."""
    S = []

    def slide(html_, quem, tempo, fala, mini=True):
        S.append(dict(html=html_, quem=quem, tempo=tempo, fala=fala, mini=mini))

    nfc = ler("examples/controle_nfc.tupa").rstrip()

    # 1 capa
    slide(f'''
  <div style="position:absolute;right:96px;top:90px;width:430px;height:430px;border-radius:50%;background:radial-gradient(circle,#2a1a0c 0%,var(--bg) 70%)"></div>
  <div style="position:absolute;right:96px;top:90px;width:430px;height:430px;background:var(--logo) center/contain no-repeat"></div>
  <div style="position:absolute;left:72px;top:170px">
    <div class="kicker">Apresentação final</div>
    <div style="font-size:150px;font-weight:800;color:var(--branco);letter-spacing:.14em;line-height:1.05;margin-top:10px">TUPÃ</div>
    <div style="font-size:44px;font-weight:600;color:var(--laranja);margin-top:6px">Programe o ESP32 em português.</div>
    <div style="font-size:21px;color:var(--corpo);margin-top:56px;line-height:1.6">Michel Lutegar · André Costa<br>Felipe Dutrain · Guilherme Lopes</div>
    <div style="font-size:15px;color:var(--cinza);margin-top:16px;letter-spacing:.1em;text-transform:uppercase">Linguagens Formais e Compiladores · IBMEC</div>
  </div>''', "Michel", 25,
          "Boa tarde, banca. Somos Michel, André, Felipe e Guilherme. O Tupã é uma linguagem em português que um compilador "
          "nosso transforma em firmware para ESP32. Em dez minutos, percorremos as quatro fases do compilador e terminamos "
          "na placa, ao vivo.", mini=False)

    # 2 problema
    ino = trecho("firmware/teste_hardware.ino", (9, 11), FOLD, (19, 19), (22, 22), FOLD2, (35, 36), FOLD2, (44, 46), (48, 48), FOLD2, (50, 51),
                 FOLD2, (66, 67))
    tup = "\n".join(l for l in ler("examples/teste_hardware.tupa").splitlines()
                    if l.strip() and not l.strip().startswith("#")).replace("    ", "  ")
    slide(f'''
  <div class="kicker">O problema</div>
  <h2>O mesmo teste, em duas linguagens.</h2>
  <div class="grid" style="grid-template-columns:.8fr 1.2fr;margin-top:22px">
    {painel("firmware/teste_hardware.ino", f"{n['manual_th']} linhas", pre("cpp", ino, "font-size:14.5px;line-height:1.5"))}
    {painel("examples/teste_hardware.tupa", f"{n['tupa_th']} linhas", pre("tupa", tup, "font-size:14px;line-height:1.45"))}
  </div>''', "Michel", 55,
          f"À esquerda, o teste de hardware que provou a nossa bancada, escrito à mão em C++: {n['manual_th']} linhas de código. "
          "Para ler um botão, um sensor e um cartão, o estudante precisa saber número de pino, modo de entrada, SPI e o "
          f"protocolo do leitor RC522. À direita, o mesmo teste em Tupã, {n['tupa_th']} linhas, com eventos em português. "
          "Detalhe honesto: o manual acende o vermelho enquanto o botão está apertado; o Tupã acende por 300 milissegundos "
          "a cada aperto, porque o LED apaga ao fim do evento. Os trechos são recortes reais dos arquivos, com reticências onde cortamos.")

    # 3 lacuna
    slide('''
  <div class="kicker">A lacuna</div>
  <h2>Ninguém une <em>português</em>, <em>texto</em> e <em>placa real</em>.</h2>
  <div class="grid" style="grid-template-columns:repeat(4,1fr);gap:16px;margin-top:56px">
    <div class="card" style="min-height:150px"><h3>Arduino IDE</h3><p style="font-size:23px">C++ e pinos.</p></div>
    <div class="card" style="min-height:150px"><h3>MakeCode, Blockly</h3><p style="font-size:23px">Só blocos.</p></div>
    <div class="card" style="min-height:150px"><h3>Flipper Zero</h3><p style="font-size:23px">Produto pronto.</p></div>
    <div class="card" style="min-height:150px"><h3>Portugol Studio</h3><p style="font-size:23px">Sem placa.</p></div>
  </div>
  <div class="card t" style="margin-top:28px;display:flex;align-items:center;gap:24px;padding:24px 28px">
    <h3 style="margin:0;font-size:34px">Tupã</h3><p style="font-size:26px;color:var(--branco)">texto em português, firmware de verdade.</p></div>''',
          "Michel", 35,
          "O Arduino IDE exige C++ e pinos desde o primeiro dia. MakeCode e Blockly usam blocos e não treinam texto. "
          "O Flipper Zero é um produto pronto, não uma ferramenta de ensino de programação. O Portugol Studio ensina "
          "lógica em português, mas não chega a uma placa. O espaço livre é texto em português gerando firmware para "
          "hardware real. É onde o Tupã se encaixa. A comparação completa está na seção de trabalhos relacionados do artigo.")

    # 4 linguagem
    slide(f'''
  <div class="kicker">A linguagem</div>
  <h2>Legível, por evento, sem pino à vista.</h2>
  <div class="grid" style="grid-template-columns:1.15fr 1fr;gap:28px;margin-top:22px">
    {painel("examples/controle_nfc.tupa", f"{n['tupa_nfc']} linhas", pre("tupa", nfc, "font-size:17.5px;line-height:1.5"))}
    <div>
      <table class="gd"><tr><th>evento</th><th>dispara quando</th></tr>
      <tr><td style="font-family:var(--mono)" class="laranja">ao iniciar</td><td style="font-family:var(--sans)">liga a placa</td></tr>
      <tr><td style="font-family:var(--mono)" class="laranja">ao botao(N)</td><td style="font-family:var(--sans)">a cada aperto</td></tr>
      <tr><td style="font-family:var(--mono)" class="laranja">ao obstaculo</td><td style="font-family:var(--sans)">IR detecta</td></tr>
      <tr><td style="font-family:var(--mono)" class="laranja">ao cartao</td><td style="font-family:var(--sans)">cartão lido</td></tr></table>
      <div class="card t" style="margin-top:22px;padding:16px 20px"><p style="font-size:20px;color:var(--branco)">Pinos e UIDs ficam em <span class="laranja" style="font-family:var(--mono)">esp32_wrover.json</span>.</p></div>
    </div>
  </div>''', "André", 55,
          "Três princípios: texto legível em português, programa organizado por eventos e nenhum número de pino no código, "
          "porque o pino mora no arquivo da placa. São quatro eventos: ao iniciar vira o setup; ao botao dispara uma vez por "
          "aperto, com debounce; ao obstaculo, quando o sensor infravermelho passa de livre para bloqueado; ao cartao, quando um "
          "cartão novo é lido. No controle de acesso: apertou o botão, lê o cartão; se for válido, LED verde por 1,5 segundo; "
          "senão, vermelho. Detalhe de projeto: iniciar, obstaculo e cartao não são palavras reservadas, só têm sentido logo depois de "
          "ao, então cartao continua livre como nome de variável.")

    # 5 arquitetura
    slide(f'''
  <div class="kicker">Arquitetura</div>
  <h2>Quatro fases, depois o arduino-cli.</h2>
  <div style="margin-top:34px">{svg_pipeline()}</div>''', "André", 40,
          "O pipeline é o clássico: léxico, sintático, semântico e geração de código. Cada fase tem uma saída que dá para "
          "inspecionar na linha de comando: tokens, AST, tabela de símbolos e o C++. O compilador para no primeiro erro e "
          "mostra um código estável. O arquivo de placa, em JSON, alimenta o semântico e o gerador com pinos, SPI, FQBN e "
          "UIDs autorizados. O compilador entrega um .ino; quem o transforma em binário e grava na placa é o arduino-cli. "
          "É uma decisão de escopo: o trabalho está na linguagem, não no backend de máquina.")

    # 6 léxico
    regex = (
        '_MESTRE = re.compile("|".join(\n'
        '    f"(?P<{nome}>{padrao})"\n'
        '    for nome, padrao in _ESPECIFICACAO))')
    ordem = ('("TK_IGUAL", r"=="),   # antes de TK_ATRIB\n'
             '("TK_ATRIB", r"="),\n'
             '("TK_ID",    r"[a-zA-Z][a-zA-Z0-9_]*")')
    slide(f'''
  <div class="kicker">Análise léxica</div>
  <h2>Uma regex mestre, 44 tokens.</h2>
  <div class="grid" style="grid-template-columns:1.1fr 1fr;gap:28px;margin-top:20px">
    <div>
      {painel("compilador/lexer.py", "regex mestre", pre("py", regex + "\n\n" + ordem, "font-size:17px"))}
      <div style="margin-top:18px">
        <span class="chip o">18 reservadas</span><span class="chip">ID</span><span class="chip">3 literais</span>
        <span class="chip">14 operadores</span><span class="chip">7 delimitadores</span><span class="chip v">EOF</span>
      </div>
    </div>
    {painel("cartao = nfc.ler();", "tokenização real", tabela_tokens())}
  </div>''', "André", 50,
          "O lexer é uma regex mestre: um grupo nomeado por token, unidos por barra vertical. A ordem importa: operadores de "
          "dois caracteres vêm antes dos de um, senão o igual-igual seria lido como dois iguais. São 44 tipos de token: 18 "
          "palavras reservadas, identificador, 3 literais, 14 operadores, 7 delimitadores e o fim de arquivo. Espaço e comentário "
          "são reconhecidos e descartados. À direita, a tokenização real de cartao igual nfc ponto ler: note que nfc é palavra "
          "reservada, mas ler é só identificador, e quem confere o método é o semântico. Caractere desconhecido gera o erro L01 "
          "com linha e coluna.")

    # 7 sintático
    ebnf1 = ('programa ::= "dispositivo" ID "{" item* "}" EOF\n'
             'evento   ::= "ao" "botao" "(" INT ")" bloco | "ao" ID bloco\n'
             'se       ::= "se" expr bloco ( "senao" bloco )?')
    ebnf2 = ('ou      ::= e ( "||" e )*\n'
             'termo   ::= fator ( ("+" | "-") fator )*\n'
             'posfixo ::= primario ( "." ID | "(" args? ")" )*')
    slide(f'''
  <div class="kicker">Análise sintática</div>
  <h2>Descendente recursivo, <em>17 nós</em> de AST.</h2>
  <div style="margin-top:14px">{svg_ast()}</div>
  <div class="grid" style="grid-template-columns:1fr 1fr;gap:20px;margin-top:10px">
    {painel("EBNF resumida", "docs/linguagem.md", pre("ebnf", ebnf1, "font-size:13px;line-height:1.5;padding:8px 14px"))}
    {painel("precedência", "uma função por regra", pre("ebnf", ebnf2, "font-size:13px;line-height:1.5;padding:8px 14px"))}
  </div>''', "Felipe", 55,
          "O parser é descendente recursivo, com um token de lookahead e uma função por regra da gramática. A precedência dos "
          "operadores está na cadeia de regras: ou, e, igualdade, comparação, soma, multiplicação, unário e posfixo; repetições "
          "viram laços. A AST tem 17 tipos de nó. A árvore é a do controle_nfc: uma declaração, o evento do botão com a atribuição "
          "de nfc.ler e um se com condição, ramo então e ramo senão. É a mesma árvore que o comando tupa ast imprime. "
          "Erro sintático informa o que era esperado e o que veio, com código S01 a S13.")

    # 8 semântico
    slide(f'''
  <div class="kicker">Análise semântica</div>
  <h2>Símbolos, tipos e a API de hardware.</h2>
  <div class="grid" style="grid-template-columns:1.05fr 1fr;gap:28px;margin-top:26px">
    <div>
      {painel("$ tupa simbolos controle_nfc.tupa", "tabela de símbolos", """<table class="gd"><tr><th>nome</th><th>tipo</th><th>escopo</th><th>lin:col</th></tr>
      <tr><td style="font-family:var(--mono)">tentativas</td><td class="t">inteiro</td><td>global</td><td class="cinza">3:5</td></tr>
      <tr><td style="font-family:var(--mono)">cartao</td><td class="h">cartao</td><td>ao botao(1)</td><td class="cinza">8:16</td></tr></table>""")}
    </div>
    <div style="margin-top:4px">
      <div class="passo"><i>1</i>variável declarada antes do uso</div>
      <div class="passo"><i>2</i>tipos corretos</div>
      <div class="passo"><i>3</i>evento único</div>
      <div class="passo"><i>4</i>pino existe na placa</div>
      <div class="passo"><i>5</i>método existe no módulo</div>
    </div>
  </div>''', "Felipe", 45,
          "O analisador semântico percorre a AST com uma tabela de símbolos por escopo. O comando tupa simbolos mostra o resultado: "
          "tentativas é um inteiro global, declarado na linha 3; cartao é uma variável do tipo cartao, que só existe dentro do evento "
          "ao botao. As verificações: variável declarada antes de usar, tipos em expressões e atribuições, evento repetido, botão "
          "sem pino na placa e método que o módulo de hardware não tem. A API de hardware é fechada: led, nfc, ir e botao, cada um com "
          "seus métodos. São 21 códigos E na tabela de erros; dois são defesas internas que nenhum programa dispara.")

    # 9 erros
    slide(f'''
  <div class="kicker">Tabela de erros</div>
  <h2>40 códigos estáveis, um por condição.</h2>
  <div class="grid" style="grid-template-columns:1fr 1.25fr;gap:28px;margin-top:22px">
    <div>
      <div class="grid" style="grid-template-columns:1fr 1fr;gap:16px">
        <div class="card"><div class="num">{n['L']}</div><div class="rot">L · léxico</div></div>
        <div class="card"><div class="num">{n['S']}</div><div class="rot">S · sintático</div></div>
        <div class="card"><div class="num">{n['E']}</div><div class="rot">E · semântico</div></div>
        <div class="card"><div class="num">{n['G']}</div><div class="rot">G · placa e arquivo</div></div>
      </div>
      <p style="font-size:21px;margin-top:20px" class="cinza">Um teste por código.</p>
    </div>
    <div>
      {painel("exemplo.tupa", "erro real", pre("tupa", "dispositivo d {\n    ao iniciar {\n        led.roxo();\n    }\n}", "font-size:18px;padding:10px 16px"))}
      <div class="term" style="margin-top:14px"><pre style="font-size:18px;line-height:1.55"><span class="e">erro semantico [E19] - linha 3, coluna 12</span>
    metodo inexistente no modulo 'led'
    disponiveis: verde(), vermelho(), apagar()
    led.roxo()

compilacao interrompida: 1 erro</pre></div>
    </div>
  </div>''', "Felipe", 45,
          "Cada condição de erro tem um código estável: L de léxico, S de sintático, E de semântico e G de geração e arquivo de placa. "
          "São 1, 13, 21 e 5: 40 no total. À direita, uma saída verdadeira do compilador: led.roxo não existe, e a mensagem "
          "lista o que existe, com o código E19, linha e coluna. A tabela completa, com exemplo mínimo e como corrigir, está em "
          "docs/tabela-de-erros.md, e é gerada do mesmo catálogo que o compilador usa. A saída está sem acento porque o compilador "
          "imprime assim.")

    # 10 geração
    gen = trecho("firmware/controle_nfc_gerado/controle_nfc_gerado.ino", (104, 104), (106, 106), "    // ... debounce por millis()", (110, 119))
    gen = textwrap.dedent(gen)
    placa = ('"pinos": { "nfc_ss": 5, "led_verde": 25,\n'
             '           "botoes": { "1": 4 } },\n'
             '"nfc": { "timeout_ms": 3000,\n'
             '         "uids_autorizados": ["33 7A 87 F7",\n'
             '                              "43 A3 6F F5"] }')
    slide(f'''
  <div class="kicker">Geração de código</div>
  <h2>Evento vira C++; a placa vem de um arquivo.</h2>
  <div class="grid" style="grid-template-columns:.9fr 1.3fr;gap:24px;margin-top:20px">
    <div>
      {painel("esp32_wrover.json", "arquivo de placa", pre("json", placa, "font-size:16px;line-height:1.55"))}
      <div style="margin-top:20px">
        <span class="chip o">debounce 50 ms</span><span class="chip o">timeout 3 s</span><span class="chip o">UIDs na placa</span>
      </div>
    </div>
    {painel("controle_nfc.ino, gerado", "ao botao(1) no loop()", pre("cpp", gen, "font-size:15px;line-height:1.5"))}
  </div>''', "Guilherme", 60,
          "O gerador percorre a AST e produz um .ino pronto para o arduino-cli. Pinagem, SPI, FQBN, biblioteca e a lista de UIDs "
          "autorizados vêm do arquivo da placa: trocar de placa é trocar o JSON. O ao iniciar vira o corpo do setup; os outros "
          "eventos viram blocos no loop. O botão tem debounce de 50 milissegundos por millis, sem delay, e dispara só na borda de "
          "descida, uma vez por aperto. O nfc.ler espera até 3 segundos por um cartão; sem cartão, o resultado é inválido. O "
          "comentário com arquivo e linha liga cada bloco ao .tupa. O trecho à direita é recorte do arquivo gerado de verdade. "
          "A lista de UIDs ficou na placa e não na linguagem porque pedia menos mudança: nenhum token, regra ou nó novo.")

    # 11 métricas
    slide(f'''
  <div class="kicker">Métricas e compilação</div>
  <h2>Menos código; compila com arduino-cli.</h2>
  <div class="grid" style="grid-template-columns:1.35fr 1fr;gap:30px;margin-top:22px">
    <div>
      <table class="gd"><tr><th>linhas de código</th><th>Tupã</th><th>C++ gerado</th><th>razão</th><th>manual</th></tr>
      <tr><td>controle_nfc</td><td>{n['tupa_nfc']}</td><td>{n['ger_nfc']}</td><td style="color:var(--verde);font-weight:700">{n['r_nfc']}x</td><td class="cinza">·</td></tr>
      <tr><td>teste_hardware</td><td>{n['tupa_th']}</td><td>{n['ger_th']}</td><td style="color:var(--verde);font-weight:700">{n['r_th']}x</td><td>{n['manual_th']}</td></tr></table>
      <p class="rot" style="margin-top:12px">Sem linhas vazias nem comentários.</p>
    </div>
    <div class="grid" style="grid-template-columns:1fr 1fr;gap:14px">
      <div class="card"><div class="num" style="font-size:56px">293<small>KB</small></div><div class="rot">flash · 22%</div></div>
      <div class="card"><div class="num" style="font-size:56px">22<small>KB</small></div><div class="rot">RAM · 6%</div></div>
      <div class="card" style="grid-column:span 2"><div class="num" style="font-size:56px">{n['testes']}<small>testes passando</small></div></div>
    </div>
  </div>''', "Guilherme", 45,
          "Linhas de código sem brancos nem comentários. O controle_nfc: 12 linhas de Tupã viram 100 de C++, razão de 8,3. O teste "
          "de hardware: 23 viram 112, razão de 4,9, contra 51 do manual. O gerado é maior que o manual porque inclui debounce, "
          "verificação do RC522, conferência de UIDs e logs, e nada disso o usuário precisa escrever. Compilado com arduino-cli 1.5.1, "
          "core esp32 3.3.12: cerca de 293 KB de flash, 22 por cento, e 22 KB de RAM, 6 por cento, praticamente iguais ao manual "
          "(291 KB). A suíte tem 98 testes passando, um por código de erro. Cuidado ao falar: a razão mede digitação poupada, "
          "não facilidade de aprender; isso está no artigo, na seção de limitações.")

    # 12 playground
    slide(f'''
  <div class="kicker">Playground</div>
  <h2>Teste agora, sem instalar nada.</h2>
  <div style="display:grid;grid-template-columns:660px 1fr;gap:28px;margin-top:20px;align-items:start">
    <div class="painel"><img src="{{{{PLAY}}}}" alt="Playground do Tupã" style="display:block;width:100%"></div>
    <div style="display:flex;flex-direction:column;align-items:center;gap:12px">
      <div style="width:150px;height:150px;background:#fff;border-radius:12px;padding:8px">{{{{QR}}}}</div>
      <div style="font-family:var(--mono);font-size:19px;color:var(--verde)">tupa.mlutegar.com</div>
      <div class="painel" style="width:400px"><div class="tit"><span>aba Como gravar</span></div><img src="{{{{GRAVAR}}}}" alt="Aba Como gravar" style="display:block;width:100%"></div>
    </div>
  </div>''', "Guilherme", 30,
          "O compilador roda em tupa.mlutegar.com: FastAPI no servidor, React e CodeMirror no navegador. Abas de tokens, AST, "
          "erros, C++, métricas e Como gravar. Erro é clicável e leva à linha; dá para copiar ou baixar o .ino. O QR code abre "
          "o site no celular de quem quiser testar. O código está aberto, licença MIT. A aba Como gravar é o passo a passo que "
          "vamos seguir na demonstração.")

    # 13 hardware e demo
    slide(f'''
  <div class="kicker">Hardware e demo ao vivo</div>
  <h2>ESP32-WROVER, RC522, IR, botão e LEDs.</h2>
  <div style="display:grid;grid-template-columns:auto 1fr;gap:36px;margin-top:20px;align-items:start">
    <div style="display:flex;gap:12px">
      <img src="{{{{FOTO1}}}}" alt="Protótipo, vista superior" style="height:440px;border-radius:10px;border:1px solid var(--linha)">
      <img src="{{{{FOTO2}}}}" alt="Protótipo, vista geral" style="height:440px;border-radius:10px;border:1px solid var(--linha)">
    </div>
    <div style="padding-top:6px">
      <div class="passo"><i>1</i>compilar</div>
      <div class="passo"><i>2</i>baixar o .ino</div>
      <div class="passo"><i>3</i>gravar</div>
      <div style="margin-top:20px;font-size:22px;line-height:1.9;color:var(--branco)">
        <span class="verde">●</span> 33 7A 87 F7 <span class="cinza">→</span> <b class="verde">liberado</b><br>
        <span class="verm">●</span> 33 8F BD F7 <span class="cinza">→</span> <b class="verm">negado</b><br>
        <span class="cinza">●</span> sem cartão <span class="cinza">→</span> <b class="verm">negado em 3 s</b></div>
      <div class="rot" style="margin-top:14px">≈ R$ 120 de material</div>
    </div>
  </div>''', "Guilherme", 25,
          "O protótipo: ESP32-WROVER-DEV, leitor RC522, sensor infravermelho de obstáculo, um botão e dois LEDs, cerca de 120 reais "
          "de material. Demonstração, de 3 minutos: o André abre o site e compila o controle_nfc; baixa o .ino; o Guilherme grava "
          "na placa com Arduino IDE em ESP32 Wrover Module, 115200 no monitor serial. O Felipe lê o serial, que mostra a checagem "
          "do RC522. Botão com o cartão 33 7A 87 F7: LED verde, acesso liberado. Botão com 33 8F BD F7: vermelho, negado. Botão "
          "sem cartão: depois de 3 segundos, nenhum detectado, negado. O Michel narra e faz a ponte com a banca. "
          "% TODO (placa): o .ino gerado de controle_nfc.tupa ainda precisa ser gravado e testado nos três casos antes da banca; "
          "hoje só o teste_hardware.ino manual foi validado em bancada (26/10/2026). Plano B no roteiro.md.")

    # 14 conclusão
    slide(f'''
  <div class="kicker">Conclusão</div>
  <h2>Entregue, com limites claros.</h2>
  <div class="grid" style="grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px">
    <div class="card" style="min-height:215px"><h3 class="verde">Entregue</h3><p>Linguagem, compilador, site e protótipo.</p></div>
    <div class="card" style="min-height:215px"><h3 class="laranja">Limitações</h3><p>Uma placa. Um erro por vez. Sem teste com usuários.</p></div>
    <div class="card" style="min-height:215px"><h3 style="color:var(--roxo)">Próximos passos</h3><p>Mais placas, atualização OTA, teste em sala.</p></div>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-top:34px">
    <div style="font-family:var(--mono);font-size:17px;line-height:1.7;color:var(--cinza)">Licença MIT · repositório público<br>github.com/mlutegar/compilador-project</div>
    <div style="font-size:64px;font-weight:800;color:var(--laranja);letter-spacing:-.01em">Perguntas?</div>
  </div>''', "Michel", 35,
          "Entregamos uma linguagem com 44 tokens, lexer por regex mestre, parser descendente recursivo, AST de 17 tipos, 40 códigos de "
          "erro, gerador para ESP32, 98 testes, site no ar e um protótipo de cerca de 120 reais. Limitações, ditas com franqueza: "
          "só a ESP32-WROVER-DEV; o compilador reporta um erro por vez; o ir é só sensor de obstáculo; não há atualização OTA; não "
          "testamos com estudantes; e o código gerado compila com o arduino-cli, e a gravação na placa foi a demonstração que acabamos de fazer. Próximos "
          "passos: mais placas, OTA e teste em sala de aula. Tudo em licença MIT, repositório público. Perguntas?")
    return S
