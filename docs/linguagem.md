# Linguagem Tupã: gramática (EBNF, extraída do código)

Fonte: `compilador/parser.py`. Parser descendente recursivo, 1 token de lookahead.

```ebnf
programa     ::= "dispositivo" ID "{" item* "}" EOF
item         ::= evento | comando
evento       ::= "ao" "botao" "(" INT ")" bloco
               | "ao" nome_evento bloco                      (* nome_evento é um ID contextual *)
nome_evento  ::= "iniciar" | "obstaculo" | "cartao"          (* conferido na análise semântica *)
bloco        ::= "{" comando* "}"
comando      ::= decl_var | se | repetir | esperar | escrever | retornar | atrib_ou_chamada
decl_var     ::= tipo ID ( "=" expr )? ";"
tipo         ::= "inteiro" | "decimal" | "texto" | "booleano"
se           ::= "se" expr bloco ( "senao" bloco )?
repetir      ::= "repetir" "(" expr ")" bloco
esperar      ::= "esperar" "(" expr ")" ";"
escrever     ::= "escrever" "(" expr ")" ";"
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

## Eventos

| Evento | Quando dispara | Vira, no `.ino` |
|---|---|---|
| `ao iniciar { }` | uma vez, ao ligar, depois de inicializar o hardware | corpo do `setup()` |
| `ao botao(N) { }` | uma vez por aperto (borda de solto para apertado, com debounce de 50 ms) | bloco no `loop()` |
| `ao obstaculo { }` | quando o sensor IR passa de livre para obstáculo detectado | bloco no `loop()` |
| `ao cartao { }` | quando um cartão novo é lido; dentro do bloco existe `cartao` (`.uid`, `.valido`) | bloco no `loop()` |

- `iniciar`, `obstaculo` e `cartao` **não são palavras reservadas**: são `TK_ID` que só têm significado logo
  depois de `ao`. Motivo: `cartao` já é nome de variável em `examples/controle_nfc.tupa` (`cartao = nfc.ler();`).
  Um nome desconhecido (`ao tocar`) dá erro semântico listando os eventos disponíveis.
- Cada evento só pode aparecer uma vez no programa (`ao botao(1)` duas vezes é erro semântico).
- `ao botao(N)` exige que a placa tenha pino para o botão N (hoje só o 1); senão é erro semântico didático.
- `ao botao`, `ao obstaculo` e `ao cartao` apagam os LEDs ao fim do bloco.
- `ao botao` e `ao obstaculo` já imprimem no Serial `Botao: PRESSIONADO` / `Botao: solto` e
  `IR: obstaculo detectado` / `IR: livre`. `ao cartao` não imprime nada sozinho: use `escrever`.

## Comando `escrever`

`escrever(expr);` envia o valor para o Serial (`Serial.println`, 115200 baud). Aceita texto, número e booleano;
texto se concatena com `+`: `escrever("Cartao UID: " + cartao.uid);`.
Não aceita um `cartao` inteiro (escolha `.uid` ou `.valido`) nem uma chamada que não devolve valor.

## Módulos de hardware

| Módulo | Métodos / propriedades |
|---|---|
| `led` | `verde()`, `vermelho()`, `apagar()` |
| `nfc` | `ler()` espera até 3 s por um cartão e retorna `cartao`; sem cartão, `cartao.valido` é falso. Imprime o UID e `acesso liberado` / `acesso negado` |
| `cartao` | `.valido` (UID está na lista de autorizados), `.uid` (texto, ex.: `33 7A 87 F7`) |
| `ir` | `detectado()` retorna `booleano`. É um **sensor IR de obstáculo**; não existe IR TX |
| `botao` | `pressionado()` retorna `booleano` (lê o botão 1) |

## Lista de UIDs autorizados

Fica no **arquivo da placa** (`compilador/placas/<placa>.json`, campo `nfc.uids_autorizados`), não na linguagem.
Foi a opção que pedia menos mudança (nenhum token, regra ou nó novo). Padrão da demo: `33 7A 87 F7` e
`43 A3 6F F5` liberados; qualquer outro (como `33 8F BD F7`) fica negado. Declarar a lista no próprio `.tupa`
é uma evolução possível.

## Tokens

44 tipos de token: 43 enviados ao parser (17 + `escrever` = 18 palavras reservadas, `ID`, 3 literais,
14 operadores, 7 delimitadores) mais `TK_EOF`. `TK_ESPACO` e `TK_COMENTARIO` são reconhecidos e descartados.
Antes eram 43 (42 + `EOF`); a diferença é `TK_ESCREVER`. Ver `tabela-de-tokens.md`.

Ver também: `tabela-de-tokens.md`, `especificacao-lexica.md`, `analise-sintatica-ast.md`, `analise-semantica-e-codegen.md`, `CONTEXTO.md`.
