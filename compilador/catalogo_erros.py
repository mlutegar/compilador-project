"""Catálogo único dos erros do compilador Tupã.

É a fonte de `docs/tabela-de-erros.md` (gerada por `tools/gerar_tabela_erros.py`),
do endpoint `GET /api/erros` e do teste `tests/test_erros.py`, que executa o exemplo
de cada linha e exige o mesmo código. Tabela e compilador não podem divergir.

`gatilho` diz como o teste provoca o erro:
  ("tupa", fonte)            compila `fonte` com a placa padrão
  ("tupa_sem_ir", fonte)     compila `fonte` com uma placa sem o pino do sensor IR
  ("placa_json", dict)       carrega uma placa cujo JSON é a placa padrão com `dict` aplicado
                             (chave com valor None = remover o campo)
  ("placa_nome", nome)       carrega a placa pelo nome
  ("cli_arquivo", caminho)   `tupa build caminho` com arquivo inexistente
`interno=True`: defesa do compilador que nenhum programa Tupã consegue disparar.
"""


def _d(corpo):
    return "dispositivo d {\n" + corpo + "\n}"


def _e(codigo, fase, condicao, mensagem, exemplo, correcao, gatilho=None, interno=False):
    return {"codigo": codigo, "fase": fase, "condicao": condicao, "mensagem": mensagem,
            "exemplo": exemplo, "correcao": correcao, "gatilho": gatilho, "interno": interno}


_L, _S, _E, _G = "léxico", "sintático", "semântico", "geração/placa"


def _tupa(codigo, fase, condicao, mensagem, fonte, correcao, **kw):
    g = kw.pop("gatilho", None) or ("tupa", fonte)
    return _e(codigo, fase, condicao, mensagem, fonte, correcao, g, **kw)


CATALOGO = [
    _tupa("L01", _L, "caractere que nenhum token reconhece",
          "caractere inesperado: {trecho}", _d("    @"),
          "Remova o caractere ou use um símbolo da linguagem (ver tabela de tokens)."),

    _tupa("S01", _S, "o programa não começa com `dispositivo`",
          "esperado 'dispositivo', encontrado {lexema}", "ao botao(1) { }",
          "Comece o arquivo com `dispositivo nome { ... }`."),
    _tupa("S02", _S, "falta o nome depois de `dispositivo`",
          "esperado nome do dispositivo, encontrado {lexema}", "dispositivo { }",
          "Dê um nome: `dispositivo controle { ... }`."),
    _tupa("S03", _S, "falta `{` (abre bloco)",
          "esperado '{', encontrado {lexema}", "dispositivo d }",
          "Abra o bloco com `{`."),
    _tupa("S04", _S, "falta `}` (fecha bloco)",
          "esperado '}', encontrado {lexema}", "dispositivo d {",
          "Feche o bloco com `}`."),
    _tupa("S05", _S, "falta `(`",
          "esperado '(', encontrado {lexema}", _d("    ao botao 1 { }"),
          "Escreva `ao botao(1)`, `repetir(n)`, `esperar(ms)` ou `escrever(x)` com parênteses."),
    _tupa("S06", _S, "`ao botao(...)` sem número inteiro",
          "esperado número do botão, encontrado {lexema}", _d("    ao botao(x) { }"),
          "Use o número do botão: `ao botao(1)`."),
    _tupa("S07", _S, "falta `)`",
          "esperado ')', encontrado {lexema}", _d("    ao botao(1 { }"),
          "Feche o parêntese."),
    _tupa("S08", _S, "tipo sem nome de variável",
          "esperado nome da variável, encontrado {lexema}", _d("    inteiro 5;"),
          "Dê um nome: `inteiro tentativas = 3;`."),
    _tupa("S09", _S, "falta `;` no fim do comando",
          "esperado ';', encontrado {lexema}", _d("    inteiro x = 1"),
          "Termine o comando com `;`."),
    _tupa("S10", _S, "falta o nome depois do `.`",
          "esperado nome do membro, encontrado {lexema}", _d("    led.;"),
          "Escreva `modulo.metodo()`, por exemplo `led.verde();`."),
    _tupa("S11", _S, "`ao` seguido de algo que não é nome de evento",
          "esperado nome do evento (botao, iniciar, obstaculo, cartao), encontrado {lexema}",
          _d("    ao 5 { }"), "Use `ao iniciar`, `ao botao(N)`, `ao obstaculo` ou `ao cartao`."),
    _tupa("S12", _S, "faltou uma expressão",
          "expressão esperada, encontrado {lexema}", _d("    x = ;"),
          "Escreva um valor, variável ou chamada depois do `=`."),
    _tupa("S13", _S, "sobrou código depois do `}` final",
          "código inesperado após o fim do programa: {lexema}", "dispositivo d { }\nx",
          "Remova o que vem depois do `}` final (só existe um `dispositivo` por arquivo)."),

    _tupa("E01", _E, "`ao obstaculo` e a placa não declara o pino `ir`",
          "a placa '{placa}' não tem sensor IR configurado", _d("    ao obstaculo { }"),
          "Declare `pinos.ir` no JSON da placa ou remova o evento.",
          gatilho=("tupa_sem_ir", _d("    ao obstaculo { }"))),
    _tupa("E02", _E, "nome de evento que não existe",
          "evento desconhecido: 'ao {nome}'\n    eventos disponiveis: ao iniciar, ao botao(N), ao obstaculo, ao cartao",
          _d("    ao teclado { }"), "Use um dos quatro eventos listados."),
    _tupa("E03", _E, "número de botão menor que 1",
          "número de botão inválido: {n}", _d("    ao botao(0) { }"),
          "Botões começam em 1."),
    _tupa("E04", _E, "o botão não tem GPIO no arquivo da placa",
          "a placa '{placa}' não tem pino configurado para o botao {n}\n"
          "    botoes com pino: {lista}\n"
          "    para usar o botao {n}, ligue-o a um GPIO e declare em \"pinos.botoes\" de "
          "compilador/placas/{placa}.json",
          _d("    ao botao(2) { }"), "Use um botão com pino, ou declare o pino em `pinos.botoes`."),
    _tupa("E05", _E, "o mesmo evento declarado duas vezes",
          "o evento '{evento}' já foi declarado na linha {linha}\n    junte os dois blocos em um só",
          _d("    ao iniciar { }\n    ao iniciar { }"), "Junte os blocos em um só."),
    _e("E06", _E, "comando que o parser produziu mas o analisador não conhece (defesa interna)",
       "comando desconhecido: {tipo}", "(inalcançável)", "Erro interno: reporte como bug.",
       None, interno=True),
    _tupa("E07", _E, "`escrever` de uma chamada que não devolve valor",
          "'escrever' precisa de um valor para imprimir, mas esta chamada não devolve nada",
          _d("    ao iniciar { escrever(led.verde()); }"),
          "Escreva um valor: texto, número, booleano ou propriedade (`cartao.uid`)."),
    _tupa("E08", _E, "`escrever` de um objeto inteiro (`cartao`)",
          "'escrever' não imprime um '{tipo}' inteiro, escolha uma propriedade\n"
          "    por exemplo: escrever({tipo}.uid);  propriedades: {props}",
          _d("    ao cartao { escrever(cartao); }"), "Escreva `cartao.uid` ou `cartao.valido`."),
    _tupa("E09", _E, "variável declarada duas vezes no mesmo escopo",
          "variável '{nome}' já declarada neste escopo",
          _d("    inteiro x = 1;\n    inteiro x = 2;"), "Use outro nome ou apenas atribua: `x = 2;`."),
    _tupa("E10", _E, "o lado esquerdo de `=` não é variável nem membro",
          "alvo de atribuição inválido", _d("    1 = 2;"),
          "Atribua a uma variável: `x = 2;`."),
    _tupa("E11", _E, "condição do `se` que não é booleana",
          "condição do 'se' deve ser booleana, e não '{tipo}'", _d("    se 1 { }"),
          "Compare: `se x > 0 { ... }`."),
    _tupa("E12", _E, "variável usada sem declaração",
          "variável '{nome}' usada sem ser declarada", _d("    escrever(y);"),
          "Declare antes (`inteiro y = 0;`) ou atribua antes de usar."),
    _tupa("E13", _E, "módulo de hardware usado sem método",
          "módulo '{modulo}' precisa de um método, ex.: {modulo}.algo()", _d("    escrever(led);"),
          "Chame um método: `led.verde();`."),
    _tupa("E14", _E, "`!` aplicado a algo que não é booleano",
          "'!' exige valor booleano", _d("    se !1 { }"), "Aplique `!` a uma comparação ou booleano."),
    _e("E15", _E, "expressão que o parser produziu mas o analisador não conhece (defesa interna)",
       "expressão desconhecida: {tipo}", "(inalcançável)", "Erro interno: reporte como bug.",
       None, interno=True),
    _tupa("E16", _E, "propriedade que o tipo objeto não tem",
          "propriedade inexistente no tipo '{tipo}': '{membro}'\n    disponiveis: {lista}",
          _d("    ao cartao { escrever(cartao.nome); }"), "Use `cartao.uid` ou `cartao.valido`."),
    _tupa("E17", _E, "acesso a membro de um valor primitivo",
          "'{membro}' não é acessível neste valor", _d("    inteiro x = 1;\n    escrever(x.y);"),
          "Só `cartao` e os módulos têm membros."),
    _tupa("E18", _E, "número de argumentos errado em chamada de hardware",
          "'{modulo}.{metodo}()' espera {n} argumento(s), recebeu {m}", _d("    led.verde(1);"),
          "Remova ou acrescente argumentos conforme a API do módulo."),
    _tupa("E19", _E, "método (ou propriedade) que o módulo não tem; no `ir` acrescenta aviso de que não há TX",
          "metodo inexistente no modulo '{modulo}'\n    disponiveis: {lista}{dica}",
          _d("    led.roxo();"),
          "Use um método listado em `disponiveis` (`ir` só tem `detectado()`)."),
    _tupa("E20", _E, "`esperar`/`repetir` com valor que não é número",
          "'{comando}' exige um número, e não '{tipo}'", _d("    esperar(\"a\");"),
          "Passe um inteiro ou decimal."),
    _tupa("E21", _E, "atribuição de tipo incompatível",
          "não é possível atribuir '{origem}' a uma variável '{destino}'",
          _d("    inteiro x = \"a\";"), "Use um valor do tipo da variável (inteiro aceita só inteiro; decimal aceita inteiro)."),

    _e("G01", _G, "`--placa` com nome ou caminho que não existe",
       "placa '{nome}' não encontrada. Disponíveis: {lista}",
       "tupa build examples/controle_nfc.tupa --placa inexistente",
       "Use um nome de `compilador/placas/` ou o caminho de um `.json`.",
       ("placa_nome", "inexistente")),
    _e("G02", _G, "UID da placa com byte que não é hexadecimal",
       "UID inválido na placa: {uid} (use bytes em hexadecimal, ex.: '33 7A 87 F7')",
       "\"uids_autorizados\": [\"ZZ\"]", "Escreva bytes em hexadecimal separados por espaço.",
       ("placa_json", {"nfc": {"timeout_ms": 3000, "uids_autorizados": ["ZZ"]}})),
    _e("G03", _G, "UID da placa com número de bytes diferente de 4, 7 ou 10",
       "UID inválido na placa: {uid} (um UID tem 4, 7 ou 10 bytes)",
       "\"uids_autorizados\": [\"33 7A\"]", "Use um UID de 4, 7 ou 10 bytes.",
       ("placa_json", {"nfc": {"timeout_ms": 3000, "uids_autorizados": ["33 7A"]}})),
    _e("G04", _G, "arquivo de placa sem campo obrigatório",
       "arquivo de placa '{caminho}' sem o campo {campo}",
       "JSON da placa sem a chave \"spi\"", "Acrescente o campo que falta (ver `esp32_wrover.json`).",
       ("placa_json", {"spi": None})),
    _e("G05", _G, "arquivo `.tupa` informado ao CLI não existe",
       "arquivo não encontrado: {arquivo}", "tupa build nao_existe.tupa",
       "Confira o caminho do arquivo.", ("cli_arquivo", "nao_existe.tupa")),
]

# O codegen (`codegen.py`) não emite erro: tudo que ele recebe já passou pela semântica.
# Erros HTTP da API (413 código grande, 408 tempo limite) não são erros do compilador e não têm código.


def por_codigo():
    return {e["codigo"]: e for e in CATALOGO}


def publico():
    """Versão enviada pela API (sem o gatilho, que é detalhe de teste)."""
    return [{k: v for k, v in e.items() if k != "gatilho"} for e in CATALOGO]
