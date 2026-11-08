# Linguagem Tupã: gramática (EBNF, extraída do código)

Fonte: `compilador/parser.py`. Parser descendente recursivo, 1 token de lookahead.

```ebnf
programa     ::= "dispositivo" ID "{" item* "}" EOF
item         ::= evento | comando
evento       ::= "ao" "botao" "(" INT ")" bloco
bloco        ::= "{" comando* "}"
comando      ::= decl_var | se | repetir | esperar | retornar | atrib_ou_chamada
decl_var     ::= tipo ID ( "=" expr )? ";"
tipo         ::= "inteiro" | "decimal" | "texto" | "booleano"
se           ::= "se" expr bloco ( "senao" bloco )?
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

## Módulos de hardware

| Módulo | Métodos |
|---|---|
| `led` | `verde()`, `vermelho()`, `apagar()` |
| `nfc` | `ler()` retorna `cartao` (`.valido`, `.id`) |
| `ir` | `enviar(x)`, `receber()` (stubs no codegen) |
| `botao` | `pressionado()` (sem suporte no codegen) |

Ver também: `tabela-de-tokens.md`, `especificacao-lexica.md`, `analise-sintatica-ast.md`, `analise-semantica-e-codegen.md`, `CONTEXTO.md`.
