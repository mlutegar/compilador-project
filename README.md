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
| [Tabela de Tokens](docs/tabela-de-tokens.md) | Todos os 43 tokens da linguagem com lexemas, regex e descrições |
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
python tupa.py tokens examples/controle_nfc.tupa

# Análise sintática — imprime a AST
python tupa.py ast examples/controle_nfc.tupa

# Compilar (back-end) — gera output/controle_nfc.ino
python tupa.py build examples/controle_nfc.tupa

# Testes automatizados (11)
python tests/test_compilador.py
```

Depois de gerar o `.ino`, compilar e gravar na placa:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 output/
arduino-cli upload  --fqbn esp32:esp32:esp32 -p COM3 output/
```

Fases documentadas em [`docs/analise-sintatica-ast.md`](docs/analise-sintatica-ast.md) e [`docs/analise-semantica-e-codegen.md`](docs/analise-semantica-e-codegen.md).

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
