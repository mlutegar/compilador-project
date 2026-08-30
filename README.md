# Compilador — Linguagem DSL para Dispositivos Embarcados

Projeto da disciplina de **Compiladores** — implementação de um compilador para uma linguagem de domínio específico (DSL) voltada ao controle de dispositivos embarcados (NFC/RFID, LEDs, infravermelho, botões).

## Visão Geral

A linguagem permite descrever o comportamento de dispositivos embarcados de forma declarativa e legível, com suporte a:

- Declaração de dispositivos e eventos
- Tipos primitivos (`inteiro`, `decimal`, `texto`, `booleano`)
- Estruturas de controle (`se`/`senao`, `repetir`)
- Acesso a módulos de hardware (`nfc`, `led`, `ir`, `botao`)
- Comandos específicos (`esperar`)

### Exemplo de código

```
dispositivo controle {

    inteiro tentativas = 3;

    ao botao(1) {

        # lê um cartão NFC
        cartao = nfc.ler();

        se cartao.valido == verdadeiro {
            led.verde();
            esperar(1500);
        }
        senao {
            led.vermelho();
        }
    }
}
```

## Estrutura do Projeto

```
compiladores-projeto/
├── docs/
│   ├── tabela-de-tokens.md      # Tabela completa de tokens da linguagem
│   ├── exemplos-tokenizacao.md  # Exemplos de tokenização passo a passo
│   └── especificacao-lexica.md  # Especificação léxica detalhada
├── src/                         # Código-fonte do compilador (futuro)
├── examples/                    # Exemplos de código na linguagem
│   └── controle_nfc.dsl
└── README.md
```

## Documentação

| Documento | Descrição |
|-----------|-----------|
| [Tabela de Tokens](docs/tabela-de-tokens.md) | Todos os tokens da linguagem com lexemas, regex e descrições |
| [Exemplos de Tokenização](docs/exemplos-tokenizacao.md) | Exemplos completos de como o lexer processa o código |
| [Especificação Léxica](docs/especificacao-lexica.md) | Regras de reconhecimento, prioridade e tratamento de erros |

## Fases do Compilador

| Fase | Status | Descrição |
|------|--------|-----------|
| Análise Léxica | 🔄 Em andamento | Tokenização do código-fonte |
| Análise Sintática | ⏳ Pendente | Verificação da estrutura gramatical |
| Análise Semântica | ⏳ Pendente | Verificação de tipos e escopo |
| Geração de Código | ⏳ Pendente | Geração de código intermediário/final |

## Equipe

Projeto desenvolvido para a disciplina de Compiladores.

## Licença

Projeto acadêmico — uso educacional.
