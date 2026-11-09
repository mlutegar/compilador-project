# 🔧 Compilador DSL para ESP32

> **Desenvolvimento de uma linguagem de programação de domínio específico e de seu compilador para programação simplificada de dispositivos embarcados baseados em ESP32.**

Projeto da disciplina de **Compiladores** — criação de uma linguagem própria (DSL) e de todo o pipeline de compilação para controlar um dispositivo embarcado com **ESP32**, inspirado no conceito do [Flipper Zero](https://flipperzero.one/).

O diferencial do trabalho é o **compilador**: a linguagem é projetada para abstrair a complexidade do hardware e permitir que qualquer pessoa programe o dispositivo de forma intuitiva.

---

## 💡 Conceito

O projeto pode ser entendido como uma **plataforma programável** voltada para:

- **Makers** — prototipagem rápida de projetos com ESP32
- **Ensino de sistemas embarcados** — programação simplificada sem precisar saber C++
- **Segurança autorizada** — testes controlados com NFC/RFID e infravermelho

Em vez de um "clone do Flipper Zero", o foco está na **linguagem e no compilador** que traduzem código de alto nível diretamente para o hardware.

---

## 🔄 Pipeline de Compilação

```
Código escrito na nossa linguagem (.dsl)
        ↓
    ┌────────┐
    │  Lexer │  → Análise Léxica
    └───┬────┘
        ↓
     Tokens
        ↓
    ┌────────┐
    │ Parser │  → Análise Sintática
    └───┬────┘
        ↓
      AST (Árvore Sintática Abstrata)
        ↓
    ┌──────────────────┐
    │ Análise Semântica │  → Verificação de tipos, escopo, validação de hardware
    └───────┬──────────┘
        ↓
    ┌──────────────────┐
    │ Geração de Código │  → Transpilação para C++/Arduino
    └───────┬──────────┘
        ↓
    C++ / Arduino (.ino)
        ↓
    Compilação (Arduino CLI / PlatformIO)
        ↓
    Upload → ESP32
```

A escolha de **DSL → C++/Arduino → ESP32** (em vez de criar uma VM na placa) é a abordagem mais segura e prática: aproveita todo o ecossistema Arduino, as bibliotecas de hardware já existentes e a toolchain de compilação madura.

---

## 📝 A Linguagem

A DSL possui comandos próprios para controlar hardware de forma legível e declarativa:

```
dispositivo controle {

    inteiro tentativas = 3;

    ao botao(1) {

        # lê um cartão NFC
        cartao = nfc.ler();

        se cartao.valido == verdadeiro {
            led.verde();
            esperar(1000);
        }
        senao {
            led.vermelho();
        }
    }
}
```

### Características da linguagem

| Recurso | Descrição |
|---------|-----------|
| `dispositivo` | Declara o programa/dispositivo principal |
| `ao botao(n)` | Define eventos associados a botões físicos |
| `se` / `senao` | Estruturas condicionais |
| `repetir` | Estrutura de repetição |
| `inteiro`, `decimal`, `texto`, `booleano` | Tipos primitivos |
| `nfc`, `ir`, `led`, `botao` | Módulos de acesso ao hardware |
| `esperar(ms)` | Pausa a execução por N milissegundos |

---

## 🎯 Escopo do MVP

Para manter o projeto viável, o MVP foca em poucas capacidades:

| Módulo | Descrição | Exemplo de uso |
|--------|-----------|----------------|
| **NFC/RFID** | Leitura e validação de cartões | `nfc.ler()`, `cartao.valido` |
| **Infravermelho** | Envio/recepção de sinais IR | `ir.enviar()`, `ir.receber()` |
| **GPIO / LED** | Controle de LEDs e pinos digitais | `led.verde()`, `led.vermelho()` |
| **Botões** | Eventos de entrada do usuário | `ao botao(1) { ... }` |

**Hardware principal:** ESP32 (DevKit v1 ou similar)

---

## 📂 Estrutura do Projeto

```
compiladores-projeto/
├── docs/
│   ├── tabela-de-tokens.md       # Tabela completa de tokens da linguagem
│   ├── exemplos-tokenizacao.md   # Exemplos de tokenização passo a passo
│   └── especificacao-lexica.md   # Especificação léxica detalhada
├── src/                          # Código-fonte do compilador
│   ├── lexer/                    # Analisador léxico
│   ├── parser/                   # Analisador sintático
│   ├── semantic/                 # Analisador semântico
│   └── codegen/                  # Gerador de código C++/Arduino
├── examples/                     # Exemplos de código na linguagem
│   └── controle_nfc.dsl
├── output/                       # Código C++ gerado (saída do compilador)
├── .gitignore
└── README.md
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [Tabela de Tokens](docs/tabela-de-tokens.md) | Todos os 44 tokens da linguagem (43 + EOF) com lexemas, regex e descrições |
| [Exemplos de Tokenização](docs/exemplos-tokenizacao.md) | 7 exemplos completos de como o lexer processa o código |
| [Especificação Léxica](docs/especificacao-lexica.md) | Regras de reconhecimento, prioridade de padrões e tratamento de erros |

---

## 🚀 Fases do Compilador

| # | Fase | Status | Descrição | Código |
|---|------|--------|-----------|--------|
| 1 | **Análise Léxica** | ✅ Implementada | Tokenização do código-fonte | `src/tupac/lexer.py` |
| 2 | **Análise Sintática** | ✅ Implementada | Construção da AST a partir dos tokens | `src/tupac/parser.py` |
| 3 | **Análise Semântica** | ✅ Implementada | Verificação de tipos, escopo e validação de hardware | `src/tupac/semantic.py` |
| 4 | **Geração de Código** | ✅ Implementada | Transpilação da AST para C++/Arduino | `src/tupac/codegen.py` |
| 5 | **Integração ESP32** | ⏳ Pendente | Compilação e upload para o hardware | Arduino CLI |

---

## 🖥️ Como usar o compilador

```bash
# Análise léxica — lista os tokens
python -m compilador tokens examples/controle_nfc.tupa

# Análise sintática — imprime a AST
python -m compilador ast examples/controle_nfc.tupa

# Compilar (back-end) — grava <pasta>/<pasta>.ino (formato que o arduino-cli exige)
python -m compilador build examples/controle_nfc.tupa -o firmware/controle_nfc_gerado
python -m compilador build examples/teste_hardware.tupa -o firmware/teste_hardware_gerado
#   --placa esp32_wrover   placa-alvo (padrão); lê compilador/placas/<nome>.json ou um caminho .json

# Testes automatizados (compilador + API web)
python -m pytest tests -q
```

### Hardware real e placa

O protótipo é um **ESP32-WROVER-DEV** (placa "ESP32 Wrover Module", FQBN `esp32:esp32:esp32wrover`),
com RC522 (biblioteca MFRC522), botão, LEDs verde/vermelho e sensor IR de obstáculo. A pinagem conferida em
bancada está em [`firmware/pinagem.md`](firmware/pinagem.md) e em `compilador/placas/esp32_wrover.json`
(o compilador lê os pinos e a lista de UIDs autorizados desse arquivo).

### Instalar o arduino-cli, o core ESP32 e a biblioteca

```bash
# Windows (sem admin): baixe arduino-cli_<versao>_Windows_64bit.zip em
# https://github.com/arduino/arduino-cli/releases e coloque o arduino-cli.exe no PATH.
# Ou: winget install ArduinoSA.CLI   |   choco install arduino-cli

arduino-cli config init
arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core update-index
arduino-cli core install esp32:esp32        # ~ 1 GB; testado com esp32:esp32 3.3.12
arduino-cli lib install MFRC522             # testado com 1.4.12
```

### Compilar e gravar na placa

```bash
# compilar (valida o .ino sem a placa)
arduino-cli compile --fqbn esp32:esp32:esp32wrover firmware/controle_nfc_gerado
arduino-cli compile --fqbn esp32:esp32:esp32wrover firmware/teste_hardware_gerado

# descobrir a porta e gravar
arduino-cli board list
arduino-cli upload -p COMx --fqbn esp32:esp32:esp32wrover firmware/controle_nfc_gerado

# acompanhar o Serial (115200)
arduino-cli monitor -p COMx -c baudrate=115200
```

O firmware manual `firmware/teste_hardware.ino` também compila: copie-o para uma pasta `teste_hardware/`
(o arduino-cli exige pasta com o mesmo nome do `.ino`) e rode o mesmo `compile`.

Fases documentadas em [`docs/analise-sintatica-ast.md`](docs/analise-sintatica-ast.md) e [`docs/analise-semantica-e-codegen.md`](docs/analise-semantica-e-codegen.md).

---

## 🌐 Playground web

Editor online do Tupã (CodeMirror 6 + React) com abas de **Tokens**, **AST**, **Erros** (clique leva à linha e sublinha o trecho), **C++ gerado** (copiar / baixar `.ino`) e **Métricas** (linhas Tupã vs C++, valores reais medidos na compilação). Atalho: `Ctrl+Enter` compila.

- **Backend:** FastAPI em `web/api/`, importa o pacote `compilador` (sem duplicar lógica). Não executa `arduino-cli`.
  - `POST /api/compilar` `{codigo}` → `{tokens, ast, erros, cpp, metricas}` (limite 20 KB, timeout 5 s)
  - `GET /api/exemplos`, `GET /api/linguagem` (palavras-chave do lexer), `GET /api/saude`
- **Frontend:** Vite + React em `web/app/`; o build estático (`web/app/dist`) é servido pelo próprio FastAPI.

**Com Docker** (mesma imagem do deploy):

```bash
docker compose up --build        # http://127.0.0.1:8000
```

O serviço `tupa` escuta só em `127.0.0.1:8000` (publicar via proxy reverso no VPS), roda como usuário não root e tem healthcheck em `/api/saude`.

**Desenvolvimento local:**

```bash
pip install -r requirements-web.txt
uvicorn web.api.main:app --reload            # API em :8000
cd web/app && npm install && npm run dev     # front em :5173 (proxy /api -> :8000)
python -m pytest tests -q                    # inclui tests/test_web_api.py
```

Variáveis opcionais: `TUPA_LIMITE_BYTES`, `TUPA_TIMEOUT_S`, `TUPA_EXEMPLOS_DIR`, `TUPA_STATIC_DIR`.

---

## 🛠️ Tecnologias

| Componente | Tecnologia |
|------------|------------|
| Compilador | Python |
| Hardware | ESP32 (DevKit v1) |
| Código gerado | C++ / Arduino |
| Toolchain de upload | Arduino CLI / PlatformIO |
| Módulos de hardware | MFRC522 (NFC), IR receiver/sender, LEDs, botões |

---

## 👥 Equipe

Projeto desenvolvido para a disciplina de Compiladores.

---

## 📄 Licença

Projeto acadêmico — uso educacional.
