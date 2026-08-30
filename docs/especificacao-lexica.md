# Especificação Léxica

Documento que define as regras formais do analisador léxico (lexer) da linguagem DSL para dispositivos embarcados baseados em ESP32.

Este é o primeiro estágio do pipeline de compilação:

```
DSL (.dsl) → Lexer → Tokens → Parser → AST → Semântica → C++/Arduino → ESP32
             ^^^^^
             (este documento)
```

---

## 1. Visão Geral

O analisador léxico é a primeira fase do compilador. Ele recebe o **código-fonte** (escrito na DSL) como uma sequência de caracteres e produz uma **sequência de tokens**, onde cada token é um par `<tipo, valor>`.

```
Código-fonte (caracteres) → Lexer → Sequência de tokens
```

---

## 2. Regras de Prioridade

O lexer deve respeitar a seguinte ordem de prioridade ao reconhecer padrões:

### 2.1. Padrões mais longos primeiro (Maximal Munch)

O lexer sempre tenta consumir o maior lexema possível. Por exemplo:

| Entrada | Token correto | Token incorreto |
|---------|---------------|-----------------|
| `==` | `TK_IGUAL` | `TK_ATRIB` + `TK_ATRIB` |
| `>=` | `TK_MAIOR_IGUAL` | `TK_MAIOR` + `TK_ATRIB` |
| `<=` | `TK_MENOR_IGUAL` | `TK_MENOR` + `TK_ATRIB` |
| `!=` | `TK_DIFERENTE` | `TK_NAO` + `TK_ATRIB` |
| `&&` | `TK_E` | erro |
| `\|\|` | `TK_OU` | erro |

### 2.2. Palavras reservadas sobre identificadores

Quando o lexer reconhece uma sequência como `inteiro`, ele deve verificar se é uma **palavra reservada** antes de classificá-la como `TK_ID`.

| Entrada | Token correto | Token incorreto |
|---------|---------------|-----------------|
| `se` | `TK_SE` | `TK_ID` |
| `inteiro` | `TK_INTEIRO` | `TK_ID` |
| `nfc` | `TK_NFC` | `TK_ID` |
| `led` | `TK_LED` | `TK_ID` |
| `sensor` | `TK_ID` | — |

**Estratégia de implementação:** Após reconhecer um lexema que casa com `[a-zA-Z][a-zA-Z0-9_]*`, o lexer consulta uma **tabela de palavras reservadas**. Se o lexema estiver na tabela, retorna o token correspondente; caso contrário, retorna `TK_ID`.

---

## 3. Tabela de Palavras Reservadas

```
dispositivo → TK_DISPOSITIVO
ao          → TK_AO
se          → TK_SE
senao       → TK_SENAO
repetir     → TK_REPETIR
inteiro     → TK_INTEIRO
decimal     → TK_DECIMAL
texto       → TK_TEXTO
booleano    → TK_BOOLEANO
verdadeiro  → TK_VERDADEIRO
falso       → TK_FALSO
retornar    → TK_RETORNAR
nfc         → TK_NFC
ir          → TK_IR
led         → TK_LED
botao       → TK_BOTAO
esperar     → TK_ESPERAR
```

---

## 4. Regras de Reconhecimento

### 4.1. Identificadores e Palavras Reservadas

```
Regex: [a-zA-Z][a-zA-Z0-9_]*
```

1. O lexer lê caracteres enquanto forem letras, dígitos ou underscore
2. O primeiro caractere **deve** ser uma letra
3. O lexema resultante é comparado com a tabela de palavras reservadas
4. Se encontrado → retorna o token da palavra reservada
5. Se não encontrado → retorna `TK_ID`

### 4.2. Números Inteiros

```
Regex: [0-9]+
```

1. O lexer lê caracteres enquanto forem dígitos
2. Se o próximo caractere **não for** um ponto (`.`) → retorna `TK_INT`
3. Se o próximo caractere **for** um ponto → trata como decimal (ver 4.3)

### 4.3. Números Decimais (Float)

```
Regex: [0-9]+\.[0-9]+([eE][+-]?[0-9]+)?
```

1. O lexer lê a parte inteira (dígitos antes do ponto)
2. Lê o ponto (`.`)
3. Lê a parte fracionária (dígitos após o ponto)
4. Opcionalmente lê o expoente: `e` ou `E`, seguido opcionalmente de `+` ou `-`, seguido de dígitos
5. Retorna `TK_FLOAT`

### 4.4. Strings

```
Regex: "[^"\n]*"
```

1. O lexer encontra uma aspa dupla (`"`) de abertura
2. Lê caracteres até encontrar outra aspa dupla de fechamento
3. Quebra de linha (`\n`) dentro da string é um **erro léxico**
4. Retorna `TK_STRING` com o conteúdo entre aspas

### 4.5. Operadores de Dois Caracteres

O lexer deve tentar reconhecer operadores de dois caracteres **antes** de operadores de um caractere:

```
== → TK_IGUAL
!= → TK_DIFERENTE
>= → TK_MAIOR_IGUAL
<= → TK_MENOR_IGUAL
&& → TK_E
|| → TK_OU
```

**Estratégia:** Ao encontrar `=`, `!`, `>`, `<`, `&` ou `|`, o lexer faz **lookahead** de um caractere para verificar se forma um operador de dois caracteres.

### 4.6. Operadores de Um Caractere

Se o lookahead não formar um operador de dois caracteres:

```
=  → TK_ATRIB
>  → TK_MAIOR
<  → TK_MENOR
!  → TK_NAO
+  → TK_SOMA
-  → TK_SUB
*  → TK_MULT
/  → TK_DIV
```

### 4.7. Delimitadores

```
(  → TK_ABRE_PAR
)  → TK_FECHA_PAR
{  → TK_ABRE_CHAVE
}  → TK_FECHA_CHAVE
,  → TK_VIRGULA
.  → TK_PONTO
;  → TK_PONTO_VIRGULA
```

### 4.8. Comentários

```
Regex: #[^\n]*
```

1. Ao encontrar `#`, o lexer lê até o final da linha
2. O conteúdo é descartado (não gera token para o parser)

### 4.9. Espaços em Branco

```
Regex: [ \t\r\n]+
```

1. Espaços, tabs, retornos de carro e quebras de linha são consumidos
2. Não geram tokens para o parser
3. Quebras de linha são contabilizadas para **rastreamento de número de linha** (útil para mensagens de erro)

---

## 5. Tratamento de Erros

O lexer deve ser capaz de lidar com erros léxicos:

| Situação | Tipo de erro | Exemplo |
|----------|--------------|---------|
| Caractere inválido | Caractere não reconhecido | `@`, `$`, `~` |
| String não fechada | Falta aspa de fechamento | `"texto sem fechar` |
| Número malformado | Ponto sem parte decimal | `3.` |

**Comportamento recomendado:**
1. Reportar o erro com número da linha e caractere/posição
2. Tentar se recuperar (avançar para o próximo caractere válido)
3. Continuar a análise para encontrar outros possíveis erros

Exemplo de mensagem de erro:
```
Erro léxico na linha 5, coluna 12: caractere inesperado '@'
```

---

## 6. Estrutura de um Token

Cada token produzido pelo lexer contém, no mínimo:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tipo` | enum | Tipo do token (e.g., `TK_INTEIRO`, `TK_ID`) |
| `lexema` | string | O texto original do código-fonte |
| `linha` | inteiro | Número da linha onde o token aparece |
| `coluna` | inteiro | Posição na linha onde o token começa |

Exemplo de representação:
```
Token {
    tipo: TK_INTEIRO,
    lexema: "inteiro",
    linha: 3,
    coluna: 5
}
```

---

## 7. Diagrama do Fluxo Léxico

```
┌─────────────────────────────────────────┐
│            Código-Fonte                 │
│  "inteiro tentativas = 3;"              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│           Leitura de Caracteres         │
│  Lê caractere por caractere do input    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Agrupamento em Lexemas          │
│  Agrupa caracteres em unidades lógicas  │
│  (usa maximal munch)                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│       Classificação do Token            │
│  Compara com palavras reservadas        │
│  Identifica tipo do token               │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│         Emissão do Token                │
│  <TK_INTEIRO, "inteiro", linha:1>       │
│  <TK_ID, "tentativas", linha:1>         │
│  <TK_ATRIB, "=", linha:1>              │
│  <TK_INT, "3", linha:1>                │
│  <TK_PONTO_VIRGULA, ";", linha:1>      │
└─────────────────────────────────────────┘
```
