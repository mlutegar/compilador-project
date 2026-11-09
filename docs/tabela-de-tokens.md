# Tabela de Tokens da Linguagem

Documento de referência com todos os tokens reconhecidos pelo analisador léxico (lexer) do compilador.

---

## 1. Palavras Reservadas

| Token | Lexema | Padrão | Descrição |
|-------|--------|--------|-----------|
| `TK_DISPOSITIVO` | `dispositivo` | `dispositivo` | Declara o dispositivo/programa principal |
| `TK_AO` | `ao` | `ao` | Declara um evento |
| `TK_SE` | `se` | `se` | Inicia estrutura condicional |
| `TK_SENAO` | `senao` | `senao` | Bloco alternativo da condição |
| `TK_REPETIR` | `repetir` | `repetir` | Inicia estrutura de repetição |
| `TK_INTEIRO` | `inteiro` | `inteiro` | Declara variável inteira |
| `TK_DECIMAL` | `decimal` | `decimal` | Declara variável de ponto flutuante |
| `TK_TEXTO` | `texto` | `texto` | Declara variável textual |
| `TK_BOOLEANO` | `booleano` | `booleano` | Declara variável lógica |
| `TK_VERDADEIRO` | `verdadeiro` | `verdadeiro` | Literal booleano verdadeiro |
| `TK_FALSO` | `falso` | `falso` | Literal booleano falso |
| `TK_RETORNAR` | `retornar` | `retornar` | Retorna um valor de uma função |

---

## 2. Comandos e Recursos Embarcados

Tokens que dão identidade à linguagem, representando hardware e comandos específicos do domínio embarcado.

| Token | Lexema | Padrão | Descrição |
|-------|--------|--------|-----------|
| `TK_NFC` | `nfc` | `nfc` | Acesso ao módulo NFC/RFID |
| `TK_IR` | `ir` | `ir` | Acesso ao infravermelho |
| `TK_LED` | `led` | `led` | Acesso ao LED do dispositivo |
| `TK_BOTAO` | `botao` | `botao` | Representa um botão físico |
| `TK_ESPERAR` | `esperar` | `esperar` | Interrompe a execução por determinado tempo |
| `TK_ESCREVER` | `escrever` | `escrever` | Envia um valor para o Serial (`escrever("texto");`) |

> **Contagem:** 43 tipos enviados ao parser (18 palavras reservadas + `TK_ID` + 3 literais + 14 operadores + 7 delimitadores) + `TK_EOF` = **44**. `TK_ESPACO` e `TK_COMENTARIO` são reconhecidos e descartados. O `TK_ESCREVER` é o único token novo (antes eram 43 com o `EOF`).
>
> **Nomes de evento não são tokens:** em `ao iniciar`, `ao obstaculo` e `ao cartao`, a palavra depois de `ao` chega como `TK_ID` e é conferida pelo parser/semântica. Assim `cartao` continua livre como nome de variável.

> **Nota:** Métodos como `ler`, `verde`, `vermelho` e propriedades como `valido` **não** são palavras reservadas. Eles são tratados como identificadores (`TK_ID`), o que torna a linguagem mais flexível. Expressões como `nfc.ler()` são decompostas em `TK_NFC TK_PONTO TK_ID TK_ABRE_PAR TK_FECHA_PAR`, e a validação de nomes de métodos fica a cargo da **análise semântica**.

---

## 3. Identificadores

| Token | Lexema (exemplo) | Regex | Descrição |
|-------|-------------------|-------|-----------|
| `TK_ID` | `cartao` | `[a-zA-Z][a-zA-Z0-9_]*` | Nome de variável, função ou propriedade |

**Exemplos válidos:**
```
cartao
cartao1
temperatura
sensor_2
tentativas
```

**Exemplos inválidos:**
```
2cartao    → começa com dígito
@sensor    → caractere especial inválido
```

---

## 4. Literais Numéricos

| Token | Lexema (exemplo) | Regex | Descrição |
|-------|-------------------|-------|-----------|
| `TK_INT` | `1500` | `[0-9]+` | Número inteiro |
| `TK_FLOAT` | `1.5` | `[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?` | Número decimal (com suporte a notação científica) |

**Exemplos de `TK_INT`:**
```
0
1
38
1500
```

**Exemplos de `TK_FLOAT`:**
```
1.5
38.0
0.9
0.9e-2
2.5E+3
```

---

## 5. Strings

| Token | Lexema (exemplo) | Regex | Descrição |
|-------|-------------------|-------|-----------|
| `TK_STRING` | `"Cartão detectado"` | `"[^"\n]*"` | Cadeia de caracteres delimitada por aspas duplas |

**Exemplos:**
```
"Controle"
"Cartão detectado"
"Erro de leitura"
```

---

## 6. Operadores

### Operadores Aritméticos

| Token | Lexema | Padrão | Descrição |
|-------|--------|--------|-----------|
| `TK_SOMA` | `+` | `\+` | Soma |
| `TK_SUB` | `-` | `-` | Subtração |
| `TK_MULT` | `*` | `\*` | Multiplicação |
| `TK_DIV` | `/` | `/` | Divisão |

### Operadores de Atribuição e Comparação

| Token | Lexema | Padrão | Descrição |
|-------|--------|--------|-----------|
| `TK_ATRIB` | `=` | `=` | Atribuição |
| `TK_IGUAL` | `==` | `==` | Comparação de igualdade |
| `TK_DIFERENTE` | `!=` | `!=` | Comparação de diferença |
| `TK_MAIOR` | `>` | `>` | Maior que |
| `TK_MENOR` | `<` | `<` | Menor que |
| `TK_MAIOR_IGUAL` | `>=` | `>=` | Maior ou igual |
| `TK_MENOR_IGUAL` | `<=` | `<=` | Menor ou igual |

### Operadores Lógicos

| Token | Lexema | Padrão | Descrição |
|-------|--------|--------|-----------|
| `TK_E` | `&&` | `&&` | Operador lógico AND |
| `TK_OU` | `\|\|` | `\|\|` | Operador lógico OR |
| `TK_NAO` | `!` | `!` | Negação lógica |

---

## 7. Delimitadores

| Token | Lexema | Regex/Padrão | Descrição |
|-------|--------|--------------|-----------|
| `TK_ABRE_PAR` | `(` | `\(` | Abre parênteses |
| `TK_FECHA_PAR` | `)` | `\)` | Fecha parênteses |
| `TK_ABRE_CHAVE` | `{` | `\{` | Inicia bloco |
| `TK_FECHA_CHAVE` | `}` | `\}` | Encerra bloco |
| `TK_VIRGULA` | `,` | `,` | Separa parâmetros |
| `TK_PONTO` | `.` | `\.` | Acesso a membro/propriedade |
| `TK_PONTO_VIRGULA` | `;` | `;` | Finaliza instrução |

---

## 8. Comentários e Espaços em Branco

Estes elementos são reconhecidos pelo lexer, mas **não são enviados ao parser**.

| Token | Lexema (exemplo) | Regex | Ação |
|-------|-------------------|-------|------|
| `TK_COMENTARIO` | `# liga o LED` | `#[^\n]*` | Ignorar |
| `TK_ESPACO` | espaço / tab / quebra de linha | `[ \t\r\n]+` | Ignorar |

---

## Tabela Consolidada

Versão compacta para referência rápida:

| Token | Categoria | Exemplo de Lexema | Padrão / Regex |
|-------|-----------|-------------------|----------------|
| `TK_DISPOSITIVO` | Palavra reservada | `dispositivo` | `dispositivo` |
| `TK_AO` | Palavra reservada | `ao` | `ao` |
| `TK_SE` | Palavra reservada | `se` | `se` |
| `TK_SENAO` | Palavra reservada | `senao` | `senao` |
| `TK_REPETIR` | Palavra reservada | `repetir` | `repetir` |
| `TK_INTEIRO` | Tipo | `inteiro` | `inteiro` |
| `TK_DECIMAL` | Tipo | `decimal` | `decimal` |
| `TK_TEXTO` | Tipo | `texto` | `texto` |
| `TK_BOOLEANO` | Tipo | `booleano` | `booleano` |
| `TK_VERDADEIRO` | Booleano | `verdadeiro` | `verdadeiro` |
| `TK_FALSO` | Booleano | `falso` | `falso` |
| `TK_RETORNAR` | Palavra reservada | `retornar` | `retornar` |
| `TK_NFC` | Hardware | `nfc` | `nfc` |
| `TK_IR` | Hardware | `ir` | `ir` |
| `TK_LED` | Hardware | `led` | `led` |
| `TK_BOTAO` | Hardware | `botao` | `botao` |
| `TK_ESPERAR` | Comando | `esperar` | `esperar` |
| `TK_ESCREVER` | Comando | `escrever` | `escrever` |
| `TK_ID` | Identificador | `cartao1` | `[a-zA-Z][a-zA-Z0-9_]*` |
| `TK_INT` | Literal | `1500` | `[0-9]+` |
| `TK_FLOAT` | Literal | `1.5` | `[0-9]+\.[0-9]+([eE][+-]?[0-9]+)?` |
| `TK_STRING` | Literal | `"teste"` | `"[^"\n]*"` |
| `TK_ATRIB` | Operador | `=` | `=` |
| `TK_IGUAL` | Operador | `==` | `==` |
| `TK_DIFERENTE` | Operador | `!=` | `!=` |
| `TK_MAIOR` | Operador | `>` | `>` |
| `TK_MENOR` | Operador | `<` | `<` |
| `TK_MAIOR_IGUAL` | Operador | `>=` | `>=` |
| `TK_MENOR_IGUAL` | Operador | `<=` | `<=` |
| `TK_SOMA` | Operador | `+` | `\+` |
| `TK_SUB` | Operador | `-` | `-` |
| `TK_MULT` | Operador | `*` | `\*` |
| `TK_DIV` | Operador | `/` | `/` |
| `TK_E` | Operador lógico | `&&` | `&&` |
| `TK_OU` | Operador lógico | `\|\|` | `\|\|` |
| `TK_NAO` | Operador lógico | `!` | `!` |
| `TK_ABRE_PAR` | Delimitador | `(` | `\(` |
| `TK_FECHA_PAR` | Delimitador | `)` | `\)` |
| `TK_ABRE_CHAVE` | Delimitador | `{` | `\{` |
| `TK_FECHA_CHAVE` | Delimitador | `}` | `\}` |
| `TK_VIRGULA` | Delimitador | `,` | `,` |
| `TK_PONTO` | Delimitador | `.` | `\.` |
| `TK_PONTO_VIRGULA` | Delimitador | `;` | `;` |
| `TK_COMENTARIO` | Comentário | `# exemplo` | `#[^\n]*` |
| `TK_ESPACO` | Ignorado | espaço/tab/newline | `[ \t\r\n]+` |
