# Roteiro da apresentação final do Tupã (P16)

Banca de Linguagens Formais e Compiladores, IBMEC. Deck em `apresentacao/index.html` (setas navegam, **N** mostra as notas, **F** tela cheia) e versão impressa em `apresentacao.pdf`. Este arquivo é gerado por `python apresentacao/build.py`; as mesmas falas aparecem nas notas dos slides.

**Tempo:** 10:00 de fala em 14 slides, mais 3:00 de demonstração ao vivo no slide 13.
**Equipe:** Michel Lutegar (Michel), André Costa (André), Felipe Dutrain (Felipe), Guilherme Lopes (Guilherme). **Orientador:** Prof. William Barbosa.

## Fala por slide

| # | Slide | Quem | Tempo | Fala |
|---|---|---|---|---|
| 1 | Capa | Michel | 0:25 | Boa tarde, banca. Somos Michel, André, Felipe e Guilherme. O Tupã é uma linguagem em português que um compilador nosso transforma em firmware para ESP32. Em dez minutos, percorremos as quatro fases do compilador e terminamos na placa, ao vivo. |
| 2 | Problema | Michel | 0:55 | À esquerda, o teste de hardware que provou a nossa bancada, escrito à mão em C++: 51 linhas de código. Para ler um botão, um sensor e um cartão, o estudante precisa saber número de pino, modo de entrada, SPI e o protocolo do leitor RC522. À direita, o mesmo teste em Tupã, 23 linhas, com eventos em português. Detalhe honesto: o manual acende o vermelho enquanto o botão está apertado; o Tupã acende por 300 milissegundos a cada aperto, porque o LED apaga ao fim do evento. Os trechos são recortes reais dos arquivos, com reticências onde cortamos. |
| 3 | Lacuna | Michel | 0:35 | O Arduino IDE exige C++ e pinos desde o primeiro dia. MakeCode e Blockly usam blocos e não treinam texto. O Flipper Zero é um produto pronto, não uma ferramenta de ensino de programação. O Portugol Studio ensina lógica em português, mas não chega a uma placa. O espaço livre é texto em português gerando firmware para hardware real. É onde o Tupã se encaixa. A comparação completa está na seção de trabalhos relacionados do artigo. |
| 4 | A linguagem | André | 0:55 | Três princípios: texto legível em português, programa organizado por eventos e nenhum número de pino no código, porque o pino mora no arquivo da placa. São quatro eventos: ao iniciar vira o setup; ao botao dispara uma vez por aperto, com debounce; ao obstaculo, quando o sensor infravermelho passa de livre para bloqueado; ao cartao, quando um cartão novo é lido. No controle de acesso: apertou o botão, lê o cartão; se for válido, LED verde por 1,5 segundo; senão, vermelho. Detalhe de projeto: iniciar, obstaculo e cartao não são palavras reservadas, só têm sentido logo depois de ao, então cartao continua livre como nome de variável. |
| 5 | Arquitetura | André | 0:40 | O pipeline é o clássico: léxico, sintático, semântico e geração de código. Cada fase tem uma saída que dá para inspecionar na linha de comando: tokens, AST, tabela de símbolos e o C++. O compilador para no primeiro erro e mostra um código estável. O arquivo de placa, em JSON, alimenta o semântico e o gerador com pinos, SPI, FQBN e UIDs autorizados. O compilador entrega um .ino; quem o transforma em binário e grava na placa é o arduino-cli. É uma decisão de escopo: o trabalho está na linguagem, não no backend de máquina. |
| 6 | Léxico | André | 0:50 | O lexer é uma regex mestre: um grupo nomeado por token, unidos por barra vertical. A ordem importa: operadores de dois caracteres vêm antes dos de um, senão o igual-igual seria lido como dois iguais. São 44 tipos de token: 18 palavras reservadas, identificador, 3 literais, 14 operadores, 7 delimitadores e o fim de arquivo. Espaço e comentário são reconhecidos e descartados. À direita, a tokenização real de cartao igual nfc ponto ler: note que nfc é palavra reservada, mas ler é só identificador, e quem confere o método é o semântico. Caractere desconhecido gera o erro L01 com linha e coluna. |
| 7 | Sintático | Felipe | 0:55 | O parser é descendente recursivo, com um token de lookahead e uma função por regra da gramática. A precedência dos operadores está na cadeia de regras: ou, e, igualdade, comparação, soma, multiplicação, unário e posfixo; repetições viram laços. A AST tem 17 tipos de nó. A árvore é a do controle_nfc: uma declaração, o evento do botão com a atribuição de nfc.ler e um se com condição, ramo então e ramo senão. É a mesma árvore que o comando tupa ast imprime. Erro sintático informa o que era esperado e o que veio, com código S01 a S13. |
| 8 | Semântico | Felipe | 0:45 | O analisador semântico percorre a AST com uma tabela de símbolos por escopo. O comando tupa simbolos mostra o resultado: tentativas é um inteiro global, declarado na linha 3; cartao é uma variável do tipo cartao, que só existe dentro do evento ao botao. As verificações: variável declarada antes de usar, tipos em expressões e atribuições, evento repetido, botão sem pino na placa e método que o módulo de hardware não tem. A API de hardware é fechada: led, nfc, ir e botao, cada um com seus métodos. São 21 códigos E na tabela de erros; dois são defesas internas que nenhum programa dispara. |
| 9 | Tabela de erros | Felipe | 0:45 | Cada condição de erro tem um código estável: L de léxico, S de sintático, E de semântico e G de geração e arquivo de placa. São 1, 13, 21 e 5: 40 no total. À direita, uma saída verdadeira do compilador: led.roxo não existe, e a mensagem lista o que existe, com o código E19, linha e coluna. A tabela completa, com exemplo mínimo e como corrigir, está em docs/tabela-de-erros.md, e é gerada do mesmo catálogo que o compilador usa. A saída está sem acento porque o compilador imprime assim. |
| 10 | Geração de código | Guilherme | 1:00 | O gerador percorre a AST e produz um .ino pronto para o arduino-cli. Pinagem, SPI, FQBN, biblioteca e a lista de UIDs autorizados vêm do arquivo da placa: trocar de placa é trocar o JSON. O ao iniciar vira o corpo do setup; os outros eventos viram blocos no loop. O botão tem debounce de 50 milissegundos por millis, sem delay, e dispara só na borda de descida, uma vez por aperto. O nfc.ler espera até 3 segundos por um cartão; sem cartão, o resultado é inválido. O comentário com arquivo e linha liga cada bloco ao .tupa. O trecho à direita é recorte do arquivo gerado de verdade. A lista de UIDs ficou na placa e não na linguagem porque pedia menos mudança: nenhum token, regra ou nó novo. |
| 11 | Métricas e compilação | Guilherme | 0:45 | Linhas de código sem brancos nem comentários. O controle_nfc: 12 linhas de Tupã viram 100 de C++, razão de 8,3. O teste de hardware: 23 viram 112, razão de 4,9, contra 51 do manual. O gerado é maior que o manual porque inclui debounce, verificação do RC522, conferência de UIDs e logs, e nada disso o usuário precisa escrever. Compilado com arduino-cli 1.5.1, core esp32 3.3.12: cerca de 293 KB de flash, 22 por cento, e 22 KB de RAM, 6 por cento, praticamente iguais ao manual (291 KB). A suíte tem 98 testes passando, um por código de erro. Cuidado ao falar: a razão mede digitação poupada, não facilidade de aprender; isso está no artigo, na seção de limitações. |
| 12 | Playground | Guilherme | 0:30 | O compilador roda em tupa.mlutegar.com: FastAPI no servidor, React e CodeMirror no navegador. Abas de tokens, AST, erros, C++, métricas e Como gravar. Erro é clicável e leva à linha; dá para copiar ou baixar o .ino. O QR code abre o site no celular de quem quiser testar. O código está aberto, licença MIT. A aba Como gravar é o passo a passo que vamos seguir na demonstração. |
| 13 | Hardware e demo | Guilherme | 0:25 + demo 3:00 | O protótipo: ESP32-WROVER-DEV, leitor RC522, sensor infravermelho de obstáculo, um botão e dois LEDs, cerca de 120 reais de material. Demonstração, de 3 minutos: o André abre o site e compila o controle_nfc; baixa o .ino; o Guilherme grava na placa com Arduino IDE em ESP32 Wrover Module, 115200 no monitor serial. O Felipe lê o serial, que mostra a checagem do RC522. Botão com o cartão 33 7A 87 F7: LED verde, acesso liberado. Botão com 33 8F BD F7: vermelho, negado. Botão sem cartão: depois de 3 segundos, nenhum detectado, negado. O Michel narra e faz a ponte com a banca. Resultado na placa em 09/11/2026: o controle_nfc gerado foi gravado e executado; o serial mostrou RC522 versao 0xB2 OK, botão com debounce (uma linha por aperto) e, sem cartão, nenhum detectado em 3 segundos, acesso negado e LED vermelho. Nesse dia o leitor não detectou cartões (falha de contato ou antena no módulo RC522), então não afirmar leitura de cartão nem LED verde com o código gerado; a leitura de UIDs foi validada na bancada de 26/10/2026. Plano B no roteiro.md. |
| 14 | Conclusão | Michel | 0:35 | Entregamos uma linguagem com 44 tokens, lexer por regex mestre, parser descendente recursivo, AST de 17 tipos, 40 códigos de erro, gerador para ESP32, 98 testes, site no ar e um protótipo de cerca de 120 reais. Limitações, ditas com franqueza: só a ESP32-WROVER-DEV; o compilador reporta um erro por vez; o ir é só sensor de obstáculo; não há atualização OTA; não testamos com estudantes; e o código gerado compila com o arduino-cli, e a gravação na placa foi a demonstração que acabamos de fazer. Próximos passos: mais placas, OTA e teste em sala de aula. Tudo em licença MIT, repositório público. Perguntas? |

## Divisão entre os quatro

| Quem | Slides | Tempo de fala |
|---|---|---|
| Michel | 1, 2, 3, 14 | 2:30 |
| André | 4, 5, 6 | 2:25 |
| Felipe | 7, 8, 9 | 2:25 |
| Guilherme | 10, 11, 12, 13 | 2:40 |

Total: 10:00, mais a demonstração. Na demo: André abre o site, compila e baixa o `.ino`; Guilherme grava e mexe na placa; Felipe lê o Monitor Serial; Michel narra e faz a ponte com a banca. Cada um fala cerca de 2:30 e participa da demo.

## Demonstração (3 min)

1. Abrir tupa.mlutegar.com, escolher `controle_nfc.tupa`, compilar (Ctrl+Enter). Mostrar a aba C++ e a aba Como gravar.
2. Baixar o `.ino` e abrir na Arduino IDE: placa ESP32 Wrover Module, Monitor Serial em 115200. Gravar.
3. No Serial aparece a checagem do RC522 (`RC522 versao: 0x.. -> OK`).
4. Apertar o botão com o cartão `33 7A 87 F7`: LED verde, "acesso liberado".
5. Apertar o botão com o cartão `33 8F BD F7`: LED vermelho, "acesso negado".
6. Apertar o botão sem cartão: após 3 s, "Cartao: nenhum detectado em 3 s" e "acesso negado".

**Resultado na placa (09/11/2026):** o `controle_nfc` gerado foi gravado (Arduino IDE, ESP32 Wrover, COM5) e executado. No Serial a 115200: `RC522 versao: 0xB2 -> OK`; `Botao: PRESSIONADO` uma vez por aperto e `Botao: solto`; sem cartão, `Cartao: nenhum detectado em 3 s`, `acesso negado` e LED vermelho, repetido de forma consistente. Nesse dia o leitor não detectou cartões (nem com o firmware manual): falha de contato ou antena no módulo RC522. Por isso os passos 4 e 5 (cartão liberado e negado) não foram reproduzidos com o código gerado; a leitura de UIDs foi validada na bancada de 26/10/2026. Não afirmar que o código gerado leu cartão ou acendeu o LED verde.

## Plano B da demonstração

- **Vídeo tutorial:** deixar o vídeo (roteiro em `roteiro-video-tutorial.md.pdf`, na raiz do repositório) baixado no computador, fora do navegador, e abrir se a placa ou a USB falhar. O arquivo de vídeo não está no repositório: conferir que está na máquina da apresentação.
- **Playground:** se a placa falhar mas houver internet, compilar `controle_nfc` em tupa.mlutegar.com ao vivo e mostrar as abas Tokens, AST, Erros (provocar `led.roxo()` e ler o `[E19]`) e C++. Isso cobre as quatro fases sem hardware.
- **Sem internet:** usar `python -m compilador build examples/controle_nfc.tupa` no terminal e abrir `firmware/controle_nfc_gerado/controle_nfc_gerado.ino`, já versionado; mostrar as fotos do protótipo e o Serial da bancada em `artigo/figuras/`.
- **Decisão:** se em 30 s a gravação não funcionar, passar ao vídeo sem pedir desculpas e voltar ao slide 14.

## Antes da banca

- [ ] Validar a leitura de cartões com o código gerado após substituir ou ressoldar o módulo RC522.
- [ ] Compilar o `controle_nfc` no site e baixar o `.ino` com antecedência, como cópia local.
- [ ] Placa ligada por USB, Arduino IDE em ESP32 Wrover Module, Monitor Serial em 115200, cartões `33 7A 87 F7` (liberado) e `33 8F BD F7` (negado) à mão.
- [ ] Abrir `apresentacao/index.html` em tela cheia (F), testar a tecla N, ter o vídeo e o `apresentacao.pdf` à mão.

## Perguntas prováveis da banca

**1. Por que regex e não um autômato escrito à mão?**
Cada token do Tupã é uma linguagem regular, então a regex equivale a um autômato finito; usamos o motor de `re` em vez de escrever a tabela de transição, o que dá menos código e menos chance de erro. A especificação continua formal (cada um dos 44 tokens tem sua regex em `docs/especificacao-lexica.md`). A ordem das alternativas resolve os prefixos: `==` antes de `=`.

**2. Por que descendente recursivo?**
A gramática é pequena e cabe em um token de lookahead. Uma função por regra deixa o código quase igual à EBNF, a precedência fica explícita na cadeia de regras, e as mensagens de erro ("esperado X, encontrado Y") saem naturalmente. Um gerador de parser traria dependência e uma etapa extra de build sem ganho para este tamanho de linguagem.

**3. Como garantem que a tabela de erros bate com o código?**
`compilador/catalogo_erros.py` é a fonte única; `tools/gerar_tabela_erros.py` gera `docs/tabela-de-erros.md` a partir dele. `tests/test_erros.py` executa o exemplo de cada código e exige o código e a mensagem, confere que o arquivo gerado é idêntico ao versionado e que todo código usado no fonte existe no catálogo. Os 98 testes passam. E06 e E15 são defesas internas, sem exemplo.

**4. Por que transpilar para C++ e não gerar binário?**
O ecossistema do ESP32 (core Arduino, biblioteca MFRC522, `arduino-cli`) já resolve toolchain, bibliotecas e gravação. Gerar `.ino` mantém o trabalho na linguagem e nas fases do compilador, e o resultado é legível, com comentários `// [arquivo:linha]` ligando cada bloco ao `.tupa`. O custo em memória é pequeno: cerca de 293 KB de flash contra 291 KB do manual.

**5. Quais são as limitações?**
Só a ESP32-WROVER-DEV (outra placa pede um JSON novo); um erro por vez, sem recuperação; o módulo `ir` é só sensor de obstáculo; sem OTA; a linguagem não foi avaliada com estudantes; e a redução de linhas mede digitação poupada, não facilidade de aprender. Tudo isso está na seção de limitações do artigo.

**6. Por que o compilador para no primeiro erro?**
Porque a linguagem é pequena, o programa típico tem poucas linhas e um erro de sintaxe costuma gerar erros em cascata. Parar no primeiro, com código, linha, coluna e o que era esperado, é mais claro para o iniciante. Recuperação de erros está nos próximos passos.

**7. Por que pinos e UIDs ficam no arquivo da placa e não na linguagem?**
Para o programa ficar portátil e legível: `ao botao(1)` não diz em que GPIO o botão está. A lista de UIDs ficou na placa porque era a opção que pedia menos mudança (nenhum token, regra ou nó novo). Declarar a lista no `.tupa` é uma evolução possível.

**8. O código gerado já foi testado na placa?**
Compila de verdade com arduino-cli 1.5.1 e core esp32 3.3.12 (4 sketches, sem erro nem aviso), e o hardware e a pinagem foram validados em bancada com o `teste_hardware.ino` manual em 26/10/2026. Em 09/11/2026 o `controle_nfc` gerado foi gravado e executado no ESP32-WROVER-DEV: inicialização do RC522 (`0xB2 -> OK`), botão com debounce, espera de 3 s, lógica de negação e LED vermelho funcionaram. A leitura de cartões com o código gerado não foi verificada, porque o módulo RC522 não detectou cartões nesse dia (nem com o firmware manual); a leitura de UIDs foi validada na bancada de 26/10/2026. Próximo passo: substituir ou ressoldar o módulo.

## Fontes dos números

44 tokens e regex mestre (`compilador/lexer.py`, `docs/tabela-de-tokens.md`); 17 nós de AST (`compilador/ast_nodes.py`); 40 códigos de erro (`docs/tabela-de-erros.md`); 98 testes (`pytest`); linhas e razões (`artigo/main.tex`, tabela de comparação, recontadas por `build.py`); flash e RAM (`docs/compilacao.md`); hardware e custo (`artigo/main.tex`).
