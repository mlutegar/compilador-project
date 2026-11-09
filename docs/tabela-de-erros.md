# Tabela de erros do compilador Tupã

> Arquivo gerado por `python tools/gerar_tabela_erros.py` a partir de `compilador/catalogo_erros.py`.
> Não edite à mão. `tests/test_erros.py` executa o exemplo de cada linha e exige o código da linha,
> e confere que este arquivo é idêntico ao gerado.

Cada erro tem um código estável: **L** léxico, **S** sintático, **E** semântico, **G** geração/placa.
O código aparece no CLI (`erro semantico [E19] - linha 3, coluna 5`), na API (campo `codigo` de cada item de `erros`)
e no site (aba Erros). O compilador para no primeiro erro. As mensagens têm partes variáveis entre `{chaves}`.

Notas:
- O gerador de código (`codegen.py`) não emite erros: o que chega a ele já passou pela análise semântica.
- Os erros G01 a G05 vêm da leitura da placa e dos arquivos pelo CLI (saída com status 2); L, S e E saem com status 1.
- Erros HTTP da API (413 código maior que 20 KB, 408 tempo limite) não são erros do compilador e não têm código.
- Linhas `interno` são defesas do compilador que nenhum programa Tupã dispara; não têm exemplo.
- Nos exemplos, `dispositivo d { ... }` envolve o trecho mínimo que dispara o erro.

| Código | Fase | Condição que dispara | Mensagem exata | Exemplo mínimo | Como corrigir |
|---|---|---|---|---|---|
| **L01** | léxico | caractere que nenhum token reconhece | <code>caractere inesperado: {trecho}</code> | <code>dispositivo d {<br>    @<br>}</code> | Remova o caractere ou use um símbolo da linguagem (ver tabela de tokens). |
| **S01** | sintático | o programa não começa com `dispositivo` | <code>esperado 'dispositivo', encontrado {lexema}</code> | <code>ao botao(1) { }</code> | Comece o arquivo com `dispositivo nome { ... }`. |
| **S02** | sintático | falta o nome depois de `dispositivo` | <code>esperado nome do dispositivo, encontrado {lexema}</code> | <code>dispositivo { }</code> | Dê um nome: `dispositivo controle { ... }`. |
| **S03** | sintático | falta `{` (abre bloco) | <code>esperado '{', encontrado {lexema}</code> | <code>dispositivo d }</code> | Abra o bloco com `{`. |
| **S04** | sintático | falta `}` (fecha bloco) | <code>esperado '}', encontrado {lexema}</code> | <code>dispositivo d {</code> | Feche o bloco com `}`. |
| **S05** | sintático | falta `(` | <code>esperado '(', encontrado {lexema}</code> | <code>dispositivo d {<br>    ao botao 1 { }<br>}</code> | Escreva `ao botao(1)`, `repetir(n)`, `esperar(ms)` ou `escrever(x)` com parênteses. |
| **S06** | sintático | `ao botao(...)` sem número inteiro | <code>esperado número do botão, encontrado {lexema}</code> | <code>dispositivo d {<br>    ao botao(x) { }<br>}</code> | Use o número do botão: `ao botao(1)`. |
| **S07** | sintático | falta `)` | <code>esperado ')', encontrado {lexema}</code> | <code>dispositivo d {<br>    ao botao(1 { }<br>}</code> | Feche o parêntese. |
| **S08** | sintático | tipo sem nome de variável | <code>esperado nome da variável, encontrado {lexema}</code> | <code>dispositivo d {<br>    inteiro 5;<br>}</code> | Dê um nome: `inteiro tentativas = 3;`. |
| **S09** | sintático | falta `;` no fim do comando | <code>esperado ';', encontrado {lexema}</code> | <code>dispositivo d {<br>    inteiro x = 1<br>}</code> | Termine o comando com `;`. |
| **S10** | sintático | falta o nome depois do `.` | <code>esperado nome do membro, encontrado {lexema}</code> | <code>dispositivo d {<br>    led.;<br>}</code> | Escreva `modulo.metodo()`, por exemplo `led.verde();`. |
| **S11** | sintático | `ao` seguido de algo que não é nome de evento | <code>esperado nome do evento (botao, iniciar, obstaculo, cartao), encontrado {lexema}</code> | <code>dispositivo d {<br>    ao 5 { }<br>}</code> | Use `ao iniciar`, `ao botao(N)`, `ao obstaculo` ou `ao cartao`. |
| **S12** | sintático | faltou uma expressão | <code>expressão esperada, encontrado {lexema}</code> | <code>dispositivo d {<br>    x = ;<br>}</code> | Escreva um valor, variável ou chamada depois do `=`. |
| **S13** | sintático | sobrou código depois do `}` final | <code>código inesperado após o fim do programa: {lexema}</code> | <code>dispositivo d { }<br>x</code> | Remova o que vem depois do `}` final (só existe um `dispositivo` por arquivo). |
| **E01** | semântico | `ao obstaculo` e a placa não declara o pino `ir` | <code>a placa '{placa}' não tem sensor IR configurado</code> | <code>dispositivo d {<br>    ao obstaculo { }<br>}</code> | Declare `pinos.ir` no JSON da placa ou remova o evento. |
| **E02** | semântico | nome de evento que não existe | <code>evento desconhecido: 'ao {nome}'<br>    eventos disponiveis: ao iniciar, ao botao(N), ao obstaculo, ao cartao</code> | <code>dispositivo d {<br>    ao teclado { }<br>}</code> | Use um dos quatro eventos listados. |
| **E03** | semântico | número de botão menor que 1 | <code>número de botão inválido: {n}</code> | <code>dispositivo d {<br>    ao botao(0) { }<br>}</code> | Botões começam em 1. |
| **E04** | semântico | o botão não tem GPIO no arquivo da placa | <code>a placa '{placa}' não tem pino configurado para o botao {n}<br>    botoes com pino: {lista}<br>    para usar o botao {n}, ligue-o a um GPIO e declare em "pinos.botoes" de compilador/placas/{placa}.json</code> | <code>dispositivo d {<br>    ao botao(2) { }<br>}</code> | Use um botão com pino, ou declare o pino em `pinos.botoes`. |
| **E05** | semântico | o mesmo evento declarado duas vezes | <code>o evento '{evento}' já foi declarado na linha {linha}<br>    junte os dois blocos em um só</code> | <code>dispositivo d {<br>    ao iniciar { }<br>    ao iniciar { }<br>}</code> | Junte os blocos em um só. |
| **E06** | semântico (interno) | comando que o parser produziu mas o analisador não conhece (defesa interna) | <code>comando desconhecido: {tipo}</code> | <code>(inalcançável)</code> | Erro interno: reporte como bug. |
| **E07** | semântico | `escrever` de uma chamada que não devolve valor | <code>'escrever' precisa de um valor para imprimir, mas esta chamada não devolve nada</code> | <code>dispositivo d {<br>    ao iniciar { escrever(led.verde()); }<br>}</code> | Escreva um valor: texto, número, booleano ou propriedade (`cartao.uid`). |
| **E08** | semântico | `escrever` de um objeto inteiro (`cartao`) | <code>'escrever' não imprime um '{tipo}' inteiro, escolha uma propriedade<br>    por exemplo: escrever({tipo}.uid);  propriedades: {props}</code> | <code>dispositivo d {<br>    ao cartao { escrever(cartao); }<br>}</code> | Escreva `cartao.uid` ou `cartao.valido`. |
| **E09** | semântico | variável declarada duas vezes no mesmo escopo | <code>variável '{nome}' já declarada neste escopo</code> | <code>dispositivo d {<br>    inteiro x = 1;<br>    inteiro x = 2;<br>}</code> | Use outro nome ou apenas atribua: `x = 2;`. |
| **E10** | semântico | o lado esquerdo de `=` não é variável nem membro | <code>alvo de atribuição inválido</code> | <code>dispositivo d {<br>    1 = 2;<br>}</code> | Atribua a uma variável: `x = 2;`. |
| **E11** | semântico | condição do `se` que não é booleana | <code>condição do 'se' deve ser booleana, e não '{tipo}'</code> | <code>dispositivo d {<br>    se 1 { }<br>}</code> | Compare: `se x &gt; 0 { ... }`. |
| **E12** | semântico | variável usada sem declaração | <code>variável '{nome}' usada sem ser declarada</code> | <code>dispositivo d {<br>    escrever(y);<br>}</code> | Declare antes (`inteiro y = 0;`) ou atribua antes de usar. |
| **E13** | semântico | módulo de hardware usado sem método | <code>módulo '{modulo}' precisa de um método, ex.: {modulo}.algo()</code> | <code>dispositivo d {<br>    escrever(led);<br>}</code> | Chame um método: `led.verde();`. |
| **E14** | semântico | `!` aplicado a algo que não é booleano | <code>'!' exige valor booleano</code> | <code>dispositivo d {<br>    se !1 { }<br>}</code> | Aplique `!` a uma comparação ou booleano. |
| **E15** | semântico (interno) | expressão que o parser produziu mas o analisador não conhece (defesa interna) | <code>expressão desconhecida: {tipo}</code> | <code>(inalcançável)</code> | Erro interno: reporte como bug. |
| **E16** | semântico | propriedade que o tipo objeto não tem | <code>propriedade inexistente no tipo '{tipo}': '{membro}'<br>    disponiveis: {lista}</code> | <code>dispositivo d {<br>    ao cartao { escrever(cartao.nome); }<br>}</code> | Use `cartao.uid` ou `cartao.valido`. |
| **E17** | semântico | acesso a membro de um valor primitivo | <code>'{membro}' não é acessível neste valor</code> | <code>dispositivo d {<br>    inteiro x = 1;<br>    escrever(x.y);<br>}</code> | Só `cartao` e os módulos têm membros. |
| **E18** | semântico | número de argumentos errado em chamada de hardware | <code>'{modulo}.{metodo}()' espera {n} argumento(s), recebeu {m}</code> | <code>dispositivo d {<br>    led.verde(1);<br>}</code> | Remova ou acrescente argumentos conforme a API do módulo. |
| **E19** | semântico | método (ou propriedade) que o módulo não tem; no `ir` acrescenta aviso de que não há TX | <code>metodo inexistente no modulo '{modulo}'<br>    disponiveis: {lista}{dica}</code> | <code>dispositivo d {<br>    led.roxo();<br>}</code> | Use um método listado em `disponiveis` (`ir` só tem `detectado()`). |
| **E20** | semântico | `esperar`/`repetir` com valor que não é número | <code>'{comando}' exige um número, e não '{tipo}'</code> | <code>dispositivo d {<br>    esperar("a");<br>}</code> | Passe um inteiro ou decimal. |
| **E21** | semântico | atribuição de tipo incompatível | <code>não é possível atribuir '{origem}' a uma variável '{destino}'</code> | <code>dispositivo d {<br>    inteiro x = "a";<br>}</code> | Use um valor do tipo da variável (inteiro aceita só inteiro; decimal aceita inteiro). |
| **G01** | geração/placa | `--placa` com nome ou caminho que não existe | <code>placa '{nome}' não encontrada. Disponíveis: {lista}</code> | <code>tupa build examples/controle_nfc.tupa --placa inexistente</code> | Use um nome de `compilador/placas/` ou o caminho de um `.json`. |
| **G02** | geração/placa | UID da placa com byte que não é hexadecimal | <code>UID inválido na placa: {uid} (use bytes em hexadecimal, ex.: '33 7A 87 F7')</code> | <code>"uids_autorizados": ["ZZ"]</code> | Escreva bytes em hexadecimal separados por espaço. |
| **G03** | geração/placa | UID da placa com número de bytes diferente de 4, 7 ou 10 | <code>UID inválido na placa: {uid} (um UID tem 4, 7 ou 10 bytes)</code> | <code>"uids_autorizados": ["33 7A"]</code> | Use um UID de 4, 7 ou 10 bytes. |
| **G04** | geração/placa | arquivo de placa sem campo obrigatório | <code>arquivo de placa '{caminho}' sem o campo {campo}</code> | <code>JSON da placa sem a chave "spi"</code> | Acrescente o campo que falta (ver `esp32_wrover.json`). |
| **G05** | geração/placa | arquivo `.tupa` informado ao CLI não existe | <code>arquivo não encontrado: {arquivo}</code> | <code>tupa build nao_existe.tupa</code> | Confira o caminho do arquivo. |
