# Análise Sintática e AST

Documento da **fase 2** do compilador Tupã: como os tokens viram uma **Árvore Sintática Abstrata (AST)**.

Implementação: `compilador/parser.py` (parser recursivo descendente) e `compilador/ast_nodes.py` (nós da AST).

---

## Gramática (EBNF)

```ebnf
programa   ::= "dispositivo" ID "{" item* "}"
item       ::= evento | comando
evento     ::= "ao" "botao" "(" INT ")" bloco
bloco      ::= "{" comando* "}"

comando    ::= decl_var
             | se
             | repetir
             | esperar
             | retornar
             | atrib_ou_chamada

decl_var   ::= tipo ID ( "=" expr )? ";"
tipo       ::= "inteiro" | "decimal" | "texto" | "booleano"
se         ::= "se" expr bloco ( "senao" bloco )?
repetir    ::= "repetir" "(" expr ")" bloco
esperar    ::= "esperar" "(" expr ")" ";"
retornar   ::= "retornar" expr? ";"
atrib_ou_chamada ::= expr ( "=" expr )? ";"

expr       ::= ou
ou         ::= e   ( "||" e )*
e          ::= igual ( "&&" igual )*
igual      ::= comp ( ("==" | "!=") comp )*
comp       ::= termo ( (">" | "<" | ">=" | "<=") termo )*
termo      ::= fator ( ("+" | "-") fator )*
fator      ::= unaria ( ("*" | "/") unaria )*
unaria     ::= ("!" | "-") unaria | posfixo
posfixo    ::= primario ( "." ID | "(" args? ")" )*
primario   ::= INT | FLOAT | STRING | "verdadeiro" | "falso"
             | ID | "nfc" | "ir" | "led" | "botao" | "(" expr ")"
args       ::= expr ( "," expr )*
```

A precedência dos operadores é codificada pela cadeia `ou → e → igual → comp → termo → fator → unaria → posfixo → primario` (do menor para o maior).

---

## Nós da AST

Definidos em `compilador/ast_nodes.py`:

`Programa`, `DeclVar`, `Evento`, `Atribuicao`, `Se`, `Repetir`, `Esperar`,
`Retornar`, `ExprComando`, `Binaria`, `Unaria`, `Literal`, `Identificador`,
`Hardware`, `AcessoMembro`, `Chamada`.

> Observação de projeto: `nfc.ler()` é decomposto em `Chamada(alvo=AcessoMembro(obj=Hardware(nfc), membro="ler"))`. Métodos e propriedades (`ler`, `valido`, `verde`) **não** são palavras reservadas — a validação deles é feita na análise semântica (`compilador/semantic.py`).

---

## AST do exemplo canônico

Para `examples/controle_nfc.tupa`, o comando `tupa ast` produz:

```
Programa(dispositivo controle)
├─ DeclVar(inteiro tentativas)
│  └─ valor: Literal(int=3)
└─ Evento(botao 1)
   ├─ Atribuicao(=)
   │  ├─ alvo: Id(cartao)
   │  └─ valor: Chamada()
   │     └─ alvo: Membro(.ler)
   │        └─ obj: Hardware(nfc)
   └─ Se
      ├─ cond: Binaria(==)
      │  ├─ esq: Membro(.valido)
      │  │  └─ obj: Id(cartao)
      │  └─ dir: Literal(booleano=True)
      ├─ entao: Comando
      │  └─ expr: Chamada()
      │     └─ alvo: Membro(.verde)
      │        └─ obj: Hardware(led)
      ├─ entao: Esperar
      │  └─ tempo: Literal(int=1500)
      └─ senao: Comando
         └─ expr: Chamada()
            └─ alvo: Membro(.vermelho)
               └─ obj: Hardware(led)
```

Gerar você mesmo:

```bash
python tupa.py ast examples/controle_nfc.tupa
```

---

## Erros sintáticos

O parser lança `ErroSintatico` (em `compilador/errors.py`) com linha/coluna e uma
mensagem do tipo *"esperado '}', encontrado ..."*. Exemplo: bloco não fechado,
parêntese faltando, expressão inválida.
