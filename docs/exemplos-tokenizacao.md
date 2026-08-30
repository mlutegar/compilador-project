# Exemplos de Tokenização

Este documento apresenta exemplos detalhados de como o analisador léxico (lexer) processa o código-fonte da linguagem, transformando caracteres em uma sequência de tokens.

---

## Exemplo 1 — Declaração de variável

**Entrada:**
```
inteiro tentativas = 3;
```

**Saída do lexer:**
```
<TK_INTEIRO, "inteiro">
<TK_ID, "tentativas">
<TK_ATRIB, "=">
<TK_INT, 3>
<TK_PONTO_VIRGULA, ";">
```

**Passo a passo:**

| Posição | Caracteres lidos | Token gerado | Lexema |
|---------|------------------|--------------|--------|
| 1–7 | `inteiro` | `TK_INTEIRO` | `inteiro` |
| 8 | ` ` | (ignorado) | — |
| 9–19 | `tentativas` | `TK_ID` | `tentativas` |
| 20 | ` ` | (ignorado) | — |
| 21 | `=` | `TK_ATRIB` | `=` |
| 22 | ` ` | (ignorado) | — |
| 23 | `3` | `TK_INT` | `3` |
| 24 | `;` | `TK_PONTO_VIRGULA` | `;` |

---

## Exemplo 2 — Condicional com acesso a propriedade

**Entrada:**
```
se cartao.valido == verdadeiro {
    led.verde();
}
```

**Saída do lexer:**
```
<TK_SE, "se">
<TK_ID, "cartao">
<TK_PONTO, ".">
<TK_ID, "valido">
<TK_IGUAL, "==">
<TK_VERDADEIRO, "verdadeiro">
<TK_ABRE_CHAVE, "{">
<TK_LED, "led">
<TK_PONTO, ".">
<TK_ID, "verde">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">
<TK_FECHA_CHAVE, "}">
```

**Observações:**
- `cartao` é um identificador (`TK_ID`), não uma palavra reservada
- `valido` também é `TK_ID` — a verificação se é uma propriedade válida fica para a análise semântica
- `led` **é** palavra reservada (`TK_LED`), diferente de `cartao`
- `verde` é `TK_ID` — o lexer não verifica se `led.verde()` é um método válido

---

## Exemplo 3 — Chamada de método com acesso a hardware

**Entrada:**
```
led.verde();
```

**Saída do lexer:**
```
<TK_LED, "led">
<TK_PONTO, ".">
<TK_ID, "verde">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">
```

**Decomposição:** `LED DOT ID ABRE_PAR FECHA_PAR PONTO_VIRGULA`

---

## Exemplo 4 — Leitura NFC com atribuição

**Entrada:**
```
cartao = nfc.ler();
```

**Saída do lexer:**
```
<TK_ID, "cartao">
<TK_ATRIB, "=">
<TK_NFC, "nfc">
<TK_PONTO, ".">
<TK_ID, "ler">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">
```

---

## Exemplo 5 — Expressão com operadores lógicos

**Entrada:**
```
se cartao.valido == verdadeiro && tentativas > 0 {
```

**Saída do lexer:**
```
<TK_SE, "se">
<TK_ID, "cartao">
<TK_PONTO, ".">
<TK_ID, "valido">
<TK_IGUAL, "==">
<TK_VERDADEIRO, "verdadeiro">
<TK_E, "&&">
<TK_ID, "tentativas">
<TK_MAIOR, ">">
<TK_INT, 0>
<TK_ABRE_CHAVE, "{">
```

---

## Exemplo 6 — Código com comentário

**Entrada:**
```
# lê o cartão NFC
cartao = nfc.ler();
```

**Saída do lexer:**
```
<TK_ID, "cartao">
<TK_ATRIB, "=">
<TK_NFC, "nfc">
<TK_PONTO, ".">
<TK_ID, "ler">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">
```

> **Nota:** O comentário `# lê o cartão NFC` é reconhecido como `TK_COMENTARIO` pelo lexer, mas é **descartado** e não aparece na saída final. O mesmo ocorre com espaços, tabs e quebras de linha (`TK_ESPACO`).

---

## Exemplo 7 — Programa completo

**Entrada:**
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

**Saída do lexer (tokens significativos):**
```
<TK_DISPOSITIVO, "dispositivo">
<TK_ID, "controle">
<TK_ABRE_CHAVE, "{">

<TK_INTEIRO, "inteiro">
<TK_ID, "tentativas">
<TK_ATRIB, "=">
<TK_INT, 3>
<TK_PONTO_VIRGULA, ";">

<TK_AO, "ao">
<TK_BOTAO, "botao">
<TK_ABRE_PAR, "(">
<TK_INT, 1>
<TK_FECHA_PAR, ")">
<TK_ABRE_CHAVE, "{">

<TK_ID, "cartao">
<TK_ATRIB, "=">
<TK_NFC, "nfc">
<TK_PONTO, ".">
<TK_ID, "ler">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">

<TK_SE, "se">
<TK_ID, "cartao">
<TK_PONTO, ".">
<TK_ID, "valido">
<TK_IGUAL, "==">
<TK_VERDADEIRO, "verdadeiro">
<TK_ABRE_CHAVE, "{">

<TK_LED, "led">
<TK_PONTO, ".">
<TK_ID, "verde">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">

<TK_ESPERAR, "esperar">
<TK_ABRE_PAR, "(">
<TK_INT, 1500>
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">

<TK_FECHA_CHAVE, "}">

<TK_SENAO, "senao">
<TK_ABRE_CHAVE, "{">

<TK_LED, "led">
<TK_PONTO, ".">
<TK_ID, "vermelho">
<TK_ABRE_PAR, "(">
<TK_FECHA_PAR, ")">
<TK_PONTO_VIRGULA, ";">

<TK_FECHA_CHAVE, "}">

<TK_FECHA_CHAVE, "}">

<TK_FECHA_CHAVE, "}">
```

---

## Fluxo de Reconhecimento do Lexer

```
caracteres
    ↓
encontra lexema
    ↓
compara com os padrões
    ↓
classifica o token
    ↓
<nome, valor>
```

O lexer lê o código-fonte caractere por caractere e agrupa os caracteres em lexemas, que são então classificados nos tokens correspondentes.
