# CONTEXTO — Projeto Tupã (estado real do repositório)

> Levantamento feito em 2026-11-08, lendo todo o código em `src/tupac/` e rodando testes/compilação.
> Nenhum arquivo de código foi alterado. Arquivos criados: este `docs/CONTEXTO.md` e `build/controle_nfc.ino`
> (saída pedida na tarefa 4; `build/` está no `.gitignore`).
> Tudo aqui foi verificado no código ou executado, exceto onde marcado **(não verificado)**.

## 0. Surpresas logo de cara (leia primeiro)

1. **`arduino-cli` NÃO está instalado** nesta máquina, então o `.ino` **nunca foi compilado de verdade** aqui.
2. **O comando `tupa build` só gera o `.ino`.** Não chama `arduino-cli` (nem compila, nem grava). O artigo diz que ele "automatiza compilação e gravação" como trabalho futuro; está correto, mas o pitch/README podem sugerir o contrário.
3. **O `.ino` gerado tem 64 linhas, não 75.** O "75 linhas (68 de código)" do artigo e do pitch vem do `.ino` **escrito à mão** (`examples/controle_nfc.ino`, 94 linhas), não da saída do compilador.
4. **Bug real:** `ao botao(2)` compila sem erro, mas o `.ino` usa `BOTAO_2` sem `#define` nem `pinMode` → **falha no `arduino-cli compile`**.
5. Há **3 arquivos de exemplo** com a mesma coisa: `controle_nfc.tupa` (canônico), `controle_nfc.dsl` (versão antiga, com acentos) e `controle_nfc.ino` (C++ manual, 94 linhas).

---

## 1. Árvore do repositório

Ignorados: `.git`, `__pycache__`, `node_modules`, venv. O Obsidian já existia (`obsidian-compilador-esp32/`), então não criei outro.

```
compiladores-projeto/
├── .gitignore                       (modificado, não commitado)
├── README.md                        (modificado, não commitado)
├── tupa.py                          ponto de entrada (insere src/ no sys.path e chama tupac.cli.main)
├── artigo/                          artigo IEEEtran (ver §7)
│   ├── IEEE-conference-template-062824.tex / .pdf
│   ├── IEEEtran.cls, IEEEtran_HOWTO.pdf
│   ├── fig1.png
│   └── Tupã.zip                     cópia zipada dos mesmos 5 arquivos (redundante)
├── docs/
│   ├── tabela-de-tokens.md, especificacao-lexica.md, exemplos-tokenizacao.md
│   ├── analise-sintatica-ast.md, analise-semantica-e-codegen.md
│   └── CONTEXTO.md                  (este arquivo)
├── examples/
│   ├── controle_nfc.tupa            canônico (17 linhas, 12 de código)
│   ├── controle_nfc.dsl             versão antiga do mesmo exemplo (18 linhas, `senao` em linha separada, com acentos)
│   └── controle_nfc.ino             C++ ESCRITO À MÃO (94 linhas) para a comparação do pitch
├── output/controle_nfc.ino          saída padrão do `tupa build` (ignorada pelo git)
├── build/controle_nfc.ino           saída desta tarefa
├── src/
│   ├── __init__.py                  (164 B)
│   └── tupac/
│       ├── __init__.py              __version__ = "0.1.0"
│       ├── tokens.py                41 linhas
│       ├── lexer.py                 110
│       ├── parser.py                266
│       ├── ast_nodes.py             141
│       ├── semantic.py              289
│       ├── codegen.py               260
│       ├── astprint.py              95
│       ├── errors.py                37
│       ├── compiler.py              23
│       └── cli.py                   100
├── tests/test_compilador.py         146 linhas, 11 testes
└── obsidian-compilador-esp32/       vault (0-Painel … 6-Entrega-Requisitos), com pitch .pptx/.pdf, artes/, gerar-pitch.js e node_modules
```

---

## 2. O compilador, fase por fase

Pipeline (`compiler.py::compilar`): `tokenizar → parsear → analisar → gerar_ino`. Cerca de 1.390 linhas de Python, sem dependências externas.

### 2.1 Lexer (`lexer.py::tokenizar`)

- **Técnica:** expressões regulares. Uma única regex mestre `_MESTRE` junta todas as alternativas como grupos nomeados `(?P<TK_X>...)`, e `finditer` percorre o texto (`lexer.py:43`). Não é autômato escrito à mão (DFA manual) nem gerador tipo lex.
- **Ordem importa:** `==`, `!=`, `>=`, `<=`, `&&`, `||` vêm antes de `=`, `>`, `<`, `!`. FLOAT vem antes de INT.
- **Palavras reservadas:** `TK_ID` é reclassificado via dicionário `PALAVRAS_RESERVADAS` (`tokens.py`). Não há regex própria por palavra.
- **Posição:** linha/coluna calculadas manualmente, e a coluna é 1-based.
- **Erro léxico:** caractere não casado gera `ErroLexico("caractere inesperado: ...")`, detectado por lacuna entre matches.
- **Limitação:** `TK_ID = [a-zA-Z][a-zA-Z0-9_]*` não aceita acentos nem `_` inicial. `inteiro cartão = 1;` dá erro léxico, e o caractere é impresso como `�` no console.
- Strings (`"[^"\n]*"`) não têm escape e não atravessam linha.

**Contagem de tokens: 43 está certo, mas só com uma convenção específica.**

| Categoria | Qtde | Tokens |
|---|---|---|
| Palavras reservadas "de linguagem" | 12 | `DISPOSITIVO AO SE SENAO REPETIR INTEIRO DECIMAL TEXTO BOOLEANO VERDADEIRO FALSO RETORNAR` |
| Hardware/comando | 5 | `NFC IR LED BOTAO ESPERAR` |
| Identificador | 1 | `ID` |
| Literais | 3 | `INT FLOAT STRING` |
| Operadores | 14 | `ATRIB IGUAL DIFERENTE MAIOR MENOR MAIOR_IGUAL MENOR_IGUAL SOMA SUB MULT DIV E OU NAO` |
| Delimitadores | 7 | `ABRE_PAR FECHA_PAR ABRE_CHAVE FECHA_CHAVE VIRGULA PONTO PONTO_VIRGULA` |
| **Subtotal enviado ao parser** | **42** | |
| `TK_EOF` (sintético, fim da entrada) | 1 | **→ 43** |
| `TK_ESPACO`, `TK_COMENTARIO` (reconhecidos e descartados) | 2 | → 45 se contar tudo |

- **43 = 42 + EOF**, sem contar espaço e comentário. Se o artigo disser "43 tipos de token" sem explicar, um professor que contar na `docs/tabela-de-tokens.md` acha 42 (+2 ignorados = 44) e não encontra EOF lá. Vale uma nota de rodapé ou ajustar o número.
- No código, a lista `_ESPECIFICACAO` tem 27 entradas (25 emitidas + 2 ignoradas), mais 17 reservadas por lookup.

### 2.2 Parser (`parser.py::Parser`)

- **Técnica:** descendente recursivo preditivo, com 1 token de lookahead (`self.atual`). Cada não-terminal é um método. Não há backtracking. Precedência de expressões é feita por níveis de método (`_ou → _e → _igualdade → _comparacao → _termo → _fator → _unaria → _posfixo → _primario`), com laços `while` (associatividade à esquerda).
- **Erro sintático:** `_espera(tipo, descricao)` lança `ErroSintatico("esperado X, encontrado 'Y'")`. O compilador **para no primeiro erro** (não há recuperação).

**Gramática REAL (EBNF), extraída do código:**

```ebnf
programa     ::= "dispositivo" ID "{" item* "}" EOF
item         ::= evento | comando
evento       ::= "ao" "botao" "(" INT ")" bloco
bloco        ::= "{" comando* "}"
comando      ::= decl_var | se | repetir | esperar | retornar | atrib_ou_chamada
decl_var     ::= tipo ID ( "=" expr )? ";"
tipo         ::= "inteiro" | "decimal" | "texto" | "booleano"
se           ::= "se" expr bloco ( "senao" bloco )?          (* sem parênteses na condição; sem "senao se" *)
repetir      ::= "repetir" "(" expr ")" bloco
esperar      ::= "esperar" "(" expr ")" ";"
retornar     ::= "retornar" expr? ";"
atrib_ou_chamada ::= expr ( "=" expr )? ";"
expr         ::= ou
ou           ::= e ( "||" e )*
e            ::= igualdade ( "&&" igualdade )*
igualdade    ::= comparacao ( ("==" | "!=") comparacao )*
comparacao   ::= termo ( (">" | "<" | ">=" | "<=") termo )*
termo        ::= fator ( ("+" | "-") fator )*
fator        ::= unaria ( ("*" | "/") unaria )*
unaria       ::= ("!" | "-") unaria | posfixo
posfixo      ::= primario ( "." ID | "(" args? ")" )*
args         ::= expr ( "," expr )*
primario     ::= INT | FLOAT | STRING | "verdadeiro" | "falso"
               | "nfc" | "ir" | "led" | "botao" | ID | "(" expr ")"
```

Diferenças importantes em relação ao fragmento EBNF do artigo (§Gramática):
- Evento no código é `ao "botao" "(" INT ")"`, e **só `botao` existe**. O artigo escreve `"ao" ID "(" expr ")"`.
- Declaração no código tem `= expr` **opcional**; no artigo é obrigatória.
- O artigo omite `repetir`, `esperar`, `retornar`, expressões e precedência.
- `declaracao` e `evento` podem aparecer em qualquer ordem no corpo, e `comando` solto também é aceito no topo.
- `chamada ::= ID "." ID ...` do artigo é muito restritivo. O código aceita `posfixo` encadeado.
- O parser aceita `esperar(...)` e `ir`/`botao` como primário, mas a semântica rejeita hardware "solto".

**Nós da AST (`ast_nodes.py`)**, dataclasses, todos com `linha`/`coluna`. São 15 tipos:

| Grupo | Nós |
|---|---|
| Estrutura | `Programa(nome, corpo)`, `DeclVar(tipo, nome, valor?)`, `Evento(tipo_evento, numero, corpo)` |
| Comandos | `Atribuicao(alvo, valor)`, `Se(condicao, entao, senao?)`, `Repetir(vezes, corpo)`, `Esperar(tempo)`, `Retornar(valor?)`, `ExprComando(expr)` |
| Expressões | `Binaria(op, esq, dir)`, `Unaria(op, operando)`, `Literal(tipo, valor)`, `Identificador(nome)`, `Hardware(nome)`, `AcessoMembro(objeto, membro)`, `Chamada(alvo, args)` |

(Mais a classe-base `No`.) `astprint.py::render_programa` imprime a árvore (`tupa ast`).

### 2.3 Semântico (`semantic.py::AnalisadorSemantico`)

**O que valida:**
- Variável usada sem declaração (`variável 'x' usada sem ser declarada`).
- Redeclaração no **mesmo** escopo.
- Número de botão `< 1`.
- Tipos em declaração/atribuição (`inteiro → decimal` é permitido; o resto exige tipo idêntico).
- Condição do `se` deve ser `booleano`. `esperar` e `repetir` exigem número. `!` exige booleano.
- Módulo de hardware existe, método existe e **aridade** correta.
- Propriedade existe no tipo objeto.
- Hardware solto (ex.: `led;`) é rejeitado.
- Escopos em pilha (`escopos`), com um novo escopo por evento/`se`/`repetir`.
- **Atribuição implícita:** `cartao = nfc.ler();` cria a variável com o tipo do lado direito.

**Tabela de módulos (`HARDWARE_API`: método → (nº args, retorno)):**

| Módulo | Métodos | Observação |
|---|---|---|
| `led` | `verde()`, `vermelho()`, `apagar()` → vazio | |
| `nfc` | `ler()` → tipo `cartao` | |
| `ir` | `enviar(1 arg)` → vazio, `receber()` → inteiro | codegen só gera **stubs TODO** |
| `botao` | `pressionado()` → booleano | **o codegen não implementa** (gera `botaoPressionado()` inexistente) |
| `esperar` | não é módulo: é comando próprio (`TK_ESPERAR`), `esperar(ms)` | |

Tipo-objeto: `cartao` tem `valido: booleano` e `id: texto`. **`cartao.id` passa na semântica, mas o `struct Cartao` gerado só tem `valido`, então usar `.id` quebraria o C++.**

**Formato dos erros** (`errors.py::TupaError.formatar`):
```
<fase> - linha L, coluna C
    <mensagem>
    <trecho>          (quando existe)
```
Fases: `erro lexico`, `erro sintatico`, `erro semantico` (sem acento), e a CLI imprime `compilacao interrompida: 1 erro` no stderr (retorno 1).

Saída real para `led.roxo()`:
```
erro semantico - linha 11, coluna 16
    metodo inexistente no modulo 'led'
    disponiveis: verde(), vermelho(), apagar()
    led.roxo()
```
**Diverge da Fig. do artigo**, que mostra o trecho com `^^^^`, "linha 9, coluna 9" e uma linha em branco antes de "disponiveis". O código **não imprime a linha-fonte nem o cursor `^`**, só o trecho `led.roxo()`.

**Lacunas semânticas:**
- `_binaria` não valida tipos dos operandos: `1 == "a"` e `verdadeiro + 1` passam.
- Não checa `ao botao(N)` duplicado nem N máximo (só `< 1`).
- `ir` e `botao.pressionado()` são aceitos mesmo sem implementação.

### 2.4 Codegen (`codegen.py::GeradorC`)

- **Includes:** `#include <Arduino.h>` sempre. `<SPI.h>` e `<MFRC522.h>` só se o programa chama `nfc.*` (`_detectar_hardware` percorre a AST por reflexão em `__dict__`).
- **Pinos: FIXOS, hardcoded no gerador**, sem configuração, sem flag, sem arquivo de placa:

  | Símbolo | GPIO | Quando |
  |---|---|---|
  | `LED_VERDE` | 16 | sempre |
  | `LED_VERMELHO` | 17 | sempre |
  | `BOTAO_1` | 4 | sempre (**só o botão 1**) |
  | `NFC_SS` | 5 | se usa `nfc` |
  | `NFC_RST` | 22 | se usa `nfc` |
  | `IR_ENVIA` / `IR_RECEBE` | 25 / 26 | se usa `ir` |

  SPI usa os pinos padrão do ESP32 (SCK 18, MISO 19, MOSI 23), que o código não declara.
- **Globais:** `DeclVar` do topo viram variáveis globais C++ (`int tentativas = 3;`).
- **`setup()`:** `Serial.begin(115200)`, `SPI.begin()` e `PCD_Init()` (se NFC), `pinMode(BOTAO_1, INPUT_PULLUP)`, `pinMode` dos dois LEDs como OUTPUT, `ledApagar()`, e depois comandos soltos do topo do programa.
- **`loop()`:** polling. Cada `ao botao(n)` vira
  ```cpp
  if (digitalRead(BOTAO_n) == LOW) {
    delay(30); // debounce
    ...corpo...
    while (digitalRead(BOTAO_n) == LOW) delay(10);
  }
  ```
  Os eventos são **polled em sequência dentro do `loop()`**. Não há interrupção, máquina de estados nem `millis()`.
- **`nfc.ler()`:** chama o helper gerado `Cartao nfcLer()`. Na atribuição implícita `cartao = nfc.ler();` o gerador declara `Cartao cartao = nfcLer();` (`_inferir_ctipo`).
- **`cartao.valido`:** vira `cartao.valido` direto. `cartao.valido == verdadeiro` → `(cartao.valido == true)`.
- **Validação do cartão:** `nfcLer()` compara o UID com a constante **`UID_AUTORIZADO = {0xDE,0xAD,0xBE,0xEF}`** (placeholder fixo, 4 bytes).
- **Métodos de hardware:** `modulo + Metodo` em camelCase (`led.verde()` → `ledVerde()`). `esperar(x)` → `delay(x)`. `repetir(n)` → `for (int _i = 0; _i < n; _i++)` (**variável `_i` fixa: `repetir` aninhado redeclara `_i` e sombreia**, válido em C++ mas ruim).
- **Comandos não traduzidos** viram comentário `// (comando não traduzido: X)`.

### 2.5 CLI (`cli.py`, `tupa.py`)

```
python tupa.py build  <arquivo.tupa> [-o saida.ino]   # gera .ino (padrão: output/<nome>.ino)
python tupa.py tokens <arquivo.tupa>                  # lista tokens
python tupa.py ast    <arquivo.tupa>                  # imprime a AST
```
- **Não existe o executável `tupa`**: não há `setup.py`/`pyproject.toml`/entry point. É `python tupa.py ...`. O artigo e o pitch escrevem `tupa build controle.tupa`.
- **Flags:** só `-o/--saida` no `build`. Não há `--porta`, `--fqbn`, `--upload`, `--pinos`, `--board`.
- **Integração com `arduino-cli`: nenhuma** (`grep` por `arduino`/`subprocess` em `src/` não acha nada).
- `main()` força UTF-8 no stdout/stderr (Windows). Códigos de saída: 0 ok, 1 erro de compilação, 2 arquivo não encontrado.
- O Arduino exige que o `.ino` fique numa pasta com o mesmo nome (`controle_nfc/controle_nfc.ino`). O `build` grava `output/controle_nfc.ino` solto, então **`arduino-cli compile` direto nele reclamaria** (o sketch precisa estar em pasta homônima). O `-o` não cria essa estrutura.

---

## 3. Testes

`python -m pytest tests -q` → **11 passed in 0.07s** (0 falhas).

Cobertura: lexer (3: tipos de token, comentários/valores, caractere inválido), parser (2), semântica (3: ok, método inexistente, variável não declarada), codegen (3: `.ino` do exemplo, sem NFC não inclui MFRC, `repetir` vira `for`).
Isso bate com o "11 testes" do artigo.
**Não há teste** de: `ao botao(2)`, `ir`, `botao.pressionado()`, `cartao.id`, tipos em operadores binários, CLI, nem compilação C++ real.

---

## 4. Compilação do exemplo canônico

`python tupa.py build examples/controle_nfc.tupa -o build/controle_nfc.ino` → exit 0, salvo em `build/controle_nfc.ino`.

| Métrica | Valor |
|---|---|
| Linhas totais | **64** |
| Linhas não vazias | 55 |
| Linhas de código (sem vazias e sem comentário `//`) | **50** |
| `#include` | **3** (`Arduino.h`, `SPI.h`, `MFRC522.h`) |
| `#define` (definições de pino) | **5** (`LED_VERDE`, `LED_VERMELHO`, `BOTAO_1`, `NFC_SS`, `NFC_RST`) |
| Fonte `.tupa` | 17 linhas totais, 13 não vazias, **12 de código** (1 comentário) |

O `.ino` gerado é um pouco maior que a razão que o artigo cita: 12 → 64 (≈5,3×) ou 12 → 50 de código (≈4,2×). Já 12 → 75 (≈6,3×) usa o `.ino` manual.
O `.ino` gerado (`build/`) é diferente de `examples/controle_nfc.ino` (manual, 94 linhas). Confira com `diff` se quiser.

---

## 5. `arduino-cli`

**Não instalado** (`which arduino-cli` falhou; também não existe `%LOCALAPPDATA%\Arduino15`). Não rodei o `compile`, então **não sei se o `.ino` compila**.

Instalação no Windows (**não verificado nesta máquina**):
```powershell
winget install ArduinoSA.CLI                    # ou: choco install arduino-cli
arduino-cli config init
arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32            # ~ centenas de MB
arduino-cli lib install MFRC522
# sketch precisa estar em pasta com o mesmo nome:
mkdir build\controle_nfc ; copy build\controle_nfc.ino build\controle_nfc\
arduino-cli compile --fqbn esp32:esp32:esp32 build\controle_nfc
arduino-cli upload  -p COMx --fqbn esp32:esp32:esp32 build\controle_nfc   # COMx via `arduino-cli board list`
```

---

## 6. Problemas encontrados no `.ino` gerado / geração

Lidos do código gerado. A "hipótese" é minha análise, não rodei na placa.

**Alta gravidade (quebra ou engana na demo)**
1. **Validação de cartão é fake.** `valido` = UID igual ao `{DE AD BE EF}` embutido. Nenhum cartão real vai bater, então **o LED verde nunca acende com um cartão real** até trocar o UID. Nada imprime o UID no Serial para o usuário descobrir qual colocar. (Dica: um `Serial.println` do UID resolveria.)
2. **`nfcLer()` só tenta uma vez.** `PICC_IsNewCardPresent()` é chamado logo após o botão. O cartão tem que já estar sobre o leitor quando o botão é apertado, senão cai no vermelho. **Hipótese:** na prática, isso pode fazer a demo falhar de forma intermitente.
3. **`ao botao(n)` com n ≠ 1 gera `BOTAO_n` sem `#define`/`pinMode`** → erro de compilação C++. Só um botão é suportado de fato.
4. **LED fica aceso para sempre** depois do evento: `ledVerde()` + `delay(1500)` não apaga depois. O LED só muda no próximo clique, e o `ledApagar()` só roda no `setup()`. O exemplo `.tupa` não chama `led.apagar()`, então o "esperar 1500" não tem efeito visível além de travar.
5. `.ino` gerado em `output/nome.ino` solto, **fora da pasta homônima** exigida pelo `arduino-cli` (ver §2.5).
6. **Pinos hardcoded** (§2.4), sem alternativa por flag. Se a protoboard foi montada em outros GPIOs, o `.ino` não funciona sem editar o compilador. `GPIO 16/17` no ESP32 DevKit v1 clássico são livres, mas conflitam em módulos WROVER (PSRAM). **(não verificado para a sua placa)**.

**Média / baixa**
7. **Bloqueios com `delay`:** `delay(30)` de debounce, `delay(10)` no `while` de soltura do botão, e o `esperar(1500)`, que vira `delay(1500)`. Enquanto isso o `loop()` não processa mais nada (outros botões, IR). Aceitável para a demo; ruim para "eventos de primeira classe".
8. **Debounce:** existe, mas simples (`delay(30)` só na borda de descida; sem debounce na soltura). Funciona para a demo. O `while (... == LOW) delay(10)` **bloqueia** enquanto o botão estiver pressionado.
9. **Sem timeout** no `while` do botão: um botão preso/curto-circuitado trava o firmware (sem watchdog tratado).
10. `PICC_HaltA()` sem `PCD_StopCrypto1()`: para MIFARE com autenticação pode deixar o leitor em estado ruim. Para ler só UID costuma funcionar.
11. `int tentativas = 3;` é declarada e **nunca usada**. Gera aviso de variável global não usada? (Em C++ global não gera warning por padrão.)
12. Sem `Serial.println` de depuração em nenhum lugar (o `Serial.begin(115200)` existe, mas nada escreve).
13. `ir.enviar/receber` são stubs TODO. `botao.pressionado()` não existe no C++. `cartao.id` não existe no `struct Cartao`.
14. Sem checagem do retorno de `PCD_Init()` nem do firmware do leitor (`PCD_DumpVersionToSerial`): se o RC522 estiver mal ligado, o resultado é silencioso (sempre vermelho).
15. Cabeçalho do `.ino` hardcoded como `// controle.ino`, não usa o nome do arquivo.
16. Strings do `.tupa` em C++ viram `"..."` sem escape de `"`/`\`. (Hoje o lexer não permite `"` dentro da string, então não quebra.)

---

## 7. Onde está o artigo e o que mais está solto

**Artigo**
- Fonte: `artigo/IEEE-conference-template-062824.tex` (430 linhas, IEEEtran, `lstlisting` com `language=Tupa`).
- PDF compilado: `artigo/IEEE-conference-template-062824.pdf`. Classe: `artigo/IEEEtran.cls`. Guia: `artigo/IEEEtran_HOWTO.pdf`.
- **Figuras:** só `artigo/fig1.png` (13,5 KB). A Fig. de fluxo (`figure*`, linha ~276) e a de erro/gramática são `lstlisting`/TikZ-like inline, não imagens. Não há foto da protoboard.
- `artigo/Tupã.zip` é uma cópia zipada dos 5 arquivos acima (redundante, e o nome com `ã` pode dar trabalho em ferramentas).
- O `.tex` tem `% TODO` marcando: e-mail dos autores, nome do professor, descrição da técnica do lexer/parser, tabela dos 43 tokens, mapeamento de pinos, contagens exatas do `.ino`, foto do protótipo, referências, testes com usuários.

**Solto na raiz / dentro de pastas**
- `tupa.py` (entrada do CLI), `README.md`, `.gitignore`.
- `output/` (saída do build, no `.gitignore`) e `build/` (idem).
- `obsidian-compilador-esp32/` com: pitch (`4-Pitch/Tupa-Pitch.pptx` 25 MB, `.pdf`), `Tupa-Plano-de-Negocios.pdf`, `Tupa-Analise-Lexica-Sintatica.pdf`, `artes/*.png`, storyboards `.pptx/.pdf` em `3-Recursos/`, geradores (`gerar-pitch.js`, `gerar_apresentacao.py`, `gerar_pdf_completo.py`), `package.json` e `node_modules/` (ignorado pelo git). Está tudo **sem commit** (`git status`: `??`).
- **Estado do git:** só 2 commits (README e docs léxicos). `src/`, `tests/`, `artigo/`, `examples/*.tupa`, `obsidian-…` e os docs novos estão **todos não rastreados**. Nada do compilador está commitado.
- O `.gitignore` tem a linha `controle_nfc.ino` e ela se aplica a qualquer pasta, o que conflita com `examples/controle_nfc.ino` (o git mostra o arquivo como `??`, então confirme se ele realmente entrará num commit).

---

## 8. Divergências entre artigo/pitch e código

| # | Artigo / pitch diz | Código / realidade |
|---|---|---|
| 1 | "43 tipos de token" | 43 = 42 enviados ao parser + `EOF`, sem espaço/comentário. A `docs/tabela-de-tokens.md` documenta 42 (+2 ignorados). Explicar a convenção. |
| 2 | "12 linhas de Tupã geram cerca de 75 de C++ (68 de código)" | `.ino` **gerado**: **64 linhas, 50 de código**. O 75/68 vem do `.ino` manual (94 linhas no arquivo). Tabela de resultados deve ser refeita com os números reais. |
| 3 | Tabela de comparação: "Inclusões: sim; Pinos: sim" | Contagens exatas: **3 `#include`, 5 `#define`**. |
| 4 | `tupa build controle.tupa` | O comando é `python tupa.py build ...`. Não há executável `tupa` instalado. |
| 5 | "compilado e gravado na placa por meio da Arduino CLI" (resumo) | O compilador **não chama** `arduino-cli`. Compilar/gravar é manual. O artigo admite em "trabalhos futuros", mas o resumo soa como se já existisse. |
| 6 | "as quatro fases do compilador implementadas" | Verdade. Mas falta: `ir` (stub), `botao.pressionado()`, `cartao.id`, múltiplos botões. |
| 7 | "O exemplo é compilado de ponta a ponta até um `.ino` válido para a Arduino CLI" | Gera o `.ino`, mas **nenhuma compilação C++ foi executada** (`arduino-cli` ausente). "Válido" não está comprovado. |
| 8 | Gramática EBNF do artigo | Não bate (§2.2): evento é só `botao`, `= expr` é opcional, faltam `repetir`/`esperar`/`retornar`/expressões. O `% TODO` do `.tex` já pede essa conferência. |
| 9 | Fig. de erro: `linha 9, coluna 9`, trecho com `^^^^` e linha em branco | Saída real: `linha 11, coluna 16` para o `.tupa` atual, trecho `led.roxo()` **sem cursor `^`**, sem linha em branco. Ou ajusta o artigo, ou implementa o cursor em `errors.py`. |
| 10 | "Apenas os módulos usados são incluídos" | Verdade para `#include`, `MFRC522` e pinos NFC/IR. **LEDs e `BOTAO_1` são sempre emitidos**, mesmo se o programa não usa. |
| 11 | "Plataforma: emissor e receptor infravermelho, LEDs e botões" | O IR é só stub no codegen. Só 1 botão tem pino. |
| 12 | Exemplo no artigo é o `.tupa` | O `.dsl` na pasta `examples/` é a versão antiga. Remover ou deixar claro para não confundir (o `README`/pitch podem citar o `.dsl`). |
| 13 | "Evento `ao ID(expr)`" | Só `ao botao(INT)`. |
| 14 | Tabela de tokens do artigo (5 categorias) | O código separa Hardware (5) de palavras-chave (12), e os tipos `inteiro/decimal/texto/booleano` fazem parte das 12. Ajustar quando completar a tabela. |
| 15 | Pitch: "análise léxica em andamento (AP1)" e parser/semântica/codegen "próximas fases" (Slide-10, Perguntas-Provaveis) | O código das 4 fases já existe e passa 11 testes. O vault (`Painel.md`) já marca "Compilador funcionando", mas os slides ainda dizem "em andamento". |

---

## 9. Perguntas para o João

**Hardware (o que mais importa para a demo)**
1. **Pinagem real da protoboard:** em quais GPIOs estão o LED verde, o LED vermelho, o botão 1, e os pinos do MFRC522 (SDA/SS, RST, SCK, MOSI, MISO)? O compilador assume LED_VERDE=16, LED_VERMELHO=17, BOTAO_1=4, NFC_SS=5, NFC_RST=22 e SPI padrão (SCK 18 / MISO 19 / MOSI 23). Se a montagem diferir, quer que eu torne os pinos configuráveis (flag, arquivo `.json` de placa ou diretivas na própria DSL)?
2. O botão está ligado entre o GPIO e o GND (usa `INPUT_PULLUP`, ativo em LOW), ou tem resistor externo/pull-down?
3. O LED tem resistor em série (220–330 Ω)? E qual é o módulo exato do leitor (RC522 a 3,3 V)? Qual é a variante da placa (ESP32 DevKit v1 com 30 ou 38 pinos, WROOM ou WROVER)?
4. Qual é o UID do cartão que deve contar como "válido"? Podemos ler o UID pelo Serial e colocar no `.tupa`/`.ino`? Hoje está `DE AD BE EF`.
5. Quer que a demo use a lógica "cartão tem que estar sobre o leitor quando aperta o botão", ou "apertar o botão e aproximar depois" (espera com timeout)?
6. O IR já está montado/vai entrar no MVP, ou posso tirar do escopo (stub atual)?

**Software / ambiente**
7. Posso instalar o `arduino-cli` + core `esp32:esp32` + lib `MFRC522` nesta máquina (e qual porta COM a placa usa)? Sem isso não dá para provar que o `.ino` compila.
8. Qual é a versão do pacote `esp32` do Arduino que vocês usaram/testaram (2.x ou 3.x)? Pode afetar o `MFRC522`.
9. Quer que `tupa build` passe a chamar o `arduino-cli` (`--compilar`, `--gravar --porta COMx`) e criar a pasta homônima do sketch automaticamente?
10. Quer um executável `tupa` (via `pyproject.toml` com entry point) para que o comando do artigo seja literalmente `tupa build ...`?

**Artigo / pitch**
11. Qual convenção de "43 tokens" vocês preferem: manter 43 (42 + EOF, com nota) ou trocar para 42 / 44?
12. Atualizo o artigo e o pitch com os números reais (64 linhas / 50 de código / 3 includes / 5 defines), ou querem manter 75/68 vindos do `.ino` manual (e dizer explicitamente que é a versão manual)?
13. Qual figura de erro vale: a do artigo (com `^^^^`) ou a saída real? Implemento o cursor `^` com a linha do código no `errors.py`?
14. E-mails dos autores e nome do professor (TODOs do `.tex`), e se `artigo/Tupã.zip` pode sair do repo.
15. Posso commitar `src/`, `tests/`, `artigo/` e `examples/` (hoje tudo está sem commit)? Devo remover `controle_nfc.dsl` e a linha `controle_nfc.ino` do `.gitignore`?
