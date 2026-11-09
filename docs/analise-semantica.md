# Análise semântica

Fase 3 do compilador Tupã (`compilador/semantic.py`). Recebe a AST do parser e confere o que a gramática não consegue:
se os nomes existem, se os tipos combinam, se o hardware pedido existe na placa. Não altera a AST; só aceita ou
levanta `ErroSemantico` (códigos **E01 a E21**, ver [`tabela-de-erros.md`](tabela-de-erros.md)). Para no primeiro erro.

## O que a fase verifica

| Verificação | Regra | Erro |
|---|---|---|
| Tabela de símbolos e escopo | variável usada tem de estar declarada; não se declara duas vezes no mesmo escopo; `x = valor;` sem declaração cria a variável (é assim que `cartao = nfc.ler();` funciona) | E09, E12 |
| Tipos | `inteiro`, `decimal`, `texto`, `booleano` (e o tipo de hardware `cartao`). `decimal` aceita `inteiro`; os demais só o próprio tipo. `se` e `!` exigem booleano; `esperar` e `repetir` exigem número | E11, E14, E20, E21 |
| Atribuição | o alvo é variável ou membro | E10 |
| Módulos e métodos | `led`, `nfc`, `ir`, `botao` e seus métodos vêm de `HARDWARE_API`; confere existência e número de argumentos. O módulo sozinho não é valor. `ir` só tem `detectado()` (sensor de obstáculo, sem TX) | E13, E18, E19 |
| Propriedades de objeto | `cartao.valido` (booleano) e `cartao.uid` (texto), de `TIPOS_OBJETO` | E16, E17 |
| Eventos válidos | `ao iniciar`, `ao botao(N)`, `ao obstaculo`, `ao cartao`; qualquer outro nome é erro; cada evento no máximo uma vez | E02, E05 |
| Dependências da placa | `ao botao(N)` exige `N >= 1` e pino em `pinos.botoes` da placa; `ao obstaculo` exige `pinos.ir` | E01, E03, E04 |
| `escrever` | não imprime chamada sem retorno (`led.verde()`) nem o objeto `cartao` inteiro | E07, E08 |
| Defesas internas | comando ou expressão que o analisador não conhece | E06, E15 |

`ao cartao` já tem a variável `cartao` dentro do bloco; fora dele ela não existe (E12).

## Estruturas de dados

Todas em `AnalisadorSemantico`:

| Estrutura | Tipo | Para quê |
|---|---|---|
| `escopos` | pilha de `dict` nome → tipo | resolução de nomes: `_tipo_de` procura do escopo mais interno para o global; `_push`/`_pop` abrem e fecham escopo em cada evento, `se`, `senao` e `repetir` |
| `nomes_escopo` | pilha paralela de rótulos | nome do escopo de cada declaração (`global`, `ao botao(1)`) |
| `simbolos` | lista de registros `{nome, tipo, escopo, linha, coluna}` | tabela de símbolos permanente: os escopos somem ao fechar, a lista fica. É o que `tupa simbolos` imprime |
| `eventos_vistos` | `dict` chave do evento → linha | detectar evento repetido (E05) |
| `placa` | `Placa` (`compilador/placa.py`, lida de `placas/<nome>.json`) | pinos de botão e IR; nenhum pino fica fixo no analisador |
| `HARDWARE_API`, `TIPOS_OBJETO` | `dict` constantes | métodos (nº de argumentos, tipo de retorno) e propriedades |

## Ordem das verificações

1. Percorre `programa.corpo` na ordem do arquivo (declarações e eventos misturados).
2. **Evento:** nome do evento → (botão: número e pino da placa / `obstaculo`: pino IR) → evento repetido → abre escopo → corpo.
3. **Comando:** declaração (avalia a expressão, depois confere o tipo e declara), atribuição (avalia o valor, depois o alvo), `se`/`repetir`/`esperar`/`escrever` (avalia a expressão e confere o tipo exigido).
4. **Expressão:** sub-expressões antes da operação; o tipo sobe pela árvore. Em chamada de hardware: módulo → método → número de argumentos → argumentos.
5. O primeiro erro encontrado encerra a análise. Léxico e sintático já rodaram antes; o gerador de código só roda se a semântica passar.

## Exemplos reais

Saídas copiadas da execução (`python -m compilador build ...`, status 1).

Método inexistente (E19):

```
erro semantico [E19] - linha 3, coluna 12
    metodo inexistente no modulo 'led'
    disponiveis: verde(), vermelho(), apagar()
    led.roxo()

compilacao interrompida: 1 erro
```

Botão sem pino na placa (E04), entrada `dispositivo d { ao botao(2) { led.verde(); } }`:

```
erro semantico [E04] - linha 2, coluna 5
    a placa 'esp32_wrover' não tem pino configurado para o botao 2
    botoes com pino: 1
    para usar o botao 2, ligue-o a um GPIO e declare em "pinos.botoes" de compilador/placas/esp32_wrover.json
    ao botao(2)
```

`escrever` do objeto inteiro (E08), entrada `ao cartao { escrever(cartao); }`:

```
erro semantico [E08] - linha 3, coluna 9
    'escrever' não imprime um 'cartao' inteiro, escolha uma propriedade
    por exemplo: escrever(cartao.uid);  propriedades: cartao.uid, cartao.valido
    escrever(...)
```

Tipo incompatível (E21), entrada `inteiro x = "oi";`:

```
erro semantico [E21] - linha 2, coluna 5
    não é possível atribuir 'texto' a uma variável 'inteiro'
```

Na API, o mesmo erro vira `{"codigo": "E21", "fase": "erro semantico", "mensagem": "...", "linha": 2, "coluna": 5, "trecho": null, "texto": "..."}`.

## Tabela de símbolos do `controle_nfc.tupa`

Programa ([`examples/controle_nfc.tupa`](../examples/controle_nfc.tupa)): `tentativas` é declarada na linha 3, no escopo
global; `cartao` nasce na linha 8 por atribuição implícita (`cartao = nfc.ler();`) dentro de `ao botao(1)`.

Saída real de `python -m compilador simbolos examples/controle_nfc.tupa`:

```
nome         tipo       escopo           linha:coluna
tentativas   inteiro    global           3:5
cartao       cartao     ao botao(1)      8:16
```

A coluna é a do operador `=` na atribuição implícita (`cartao = nfc.ler()`) e a do tipo na declaração (`inteiro tentativas`).
Para `examples/teste_hardware.tupa` a tabela tem só `cartao` em `ao cartao` (28:5): o evento já a traz declarada.

## Onde está testado

`tests/test_erros.py` executa o exemplo mínimo de cada erro e exige o código da tabela; `tests/test_compilador.py`
cobre os casos felizes e `test_tabela_de_simbolos_do_controle_nfc` fixa a tabela acima.
