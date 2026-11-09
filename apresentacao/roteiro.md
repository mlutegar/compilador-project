# Roteiro da apresentação final do Tupã

Banca de Linguagens Formais e Compiladores, IBMEC. Deck em `apresentacao/index.html` (setas navegam, tecla N mostra as notas), versão impressa em `apresentacao.pdf`.

**Tempo:** 9 min 55 s de fala + demo ao vivo de 3 a 4 min no slide 11.
**Equipe:** Michel Lutegar (M), André Costa (A), Felipe Dutrain (F), Guilherme Lopes (G).

| # | Slide | Quem | Tempo | Fala |
|---|---|---|---|---|
| 1 | Capa | M | 0:30 | Boa tarde, banca. Somos Michel, André, Felipe e Guilherme. Tupã é uma linguagem em português que vira firmware de ESP32. Na primeira entrega mostramos a ideia; hoje mostramos o que foi entregue: compilador completo, site no ar e protótipo montado. Vamos percorrer as fases do compilador e terminar na placa. |
| 2 | Problema | M | 1:00 | À esquerda, o teste de hardware que provou nossa bancada, escrito à mão em C++: 51 linhas. Para tratar botão, obstáculo e cartão o estudante precisa de pinos, modos de entrada, SPI e leitura do RC522. À direita, o mesmo comportamento em Tupã, 23 linhas, com eventos em português. O log de botão e de IR sai sozinho. Detalhe honesto: o manual acende o vermelho enquanto o botão está apertado; o Tupã acende por 300 ms a cada aperto. |
| 3 | Lacuna | M | 0:45 | Arduino IDE exige C++ e pinos desde o primeiro dia. MakeCode e Blockly usam blocos e não treinam texto. Flipper Zero é um produto pronto, não uma ferramenta de ensino. Portugol Studio ensina lógica em português, mas não chega a uma placa. O espaço livre é texto em português gerando firmware para hardware real. |
| 4 | A linguagem | A | 1:00 | Três princípios: legível, orientada a evento, sem pino à vista (o pino mora no arquivo da placa). Quatro eventos: ao iniciar (vira o setup), ao botao (a cada aperto, com debounce), ao obstaculo (sensor IR passa de livre para bloqueado) e ao cartao (cartão novo lido). No controle_nfc: apertou, lê o cartão; válido acende verde por 1,5 s, senão vermelho. `iniciar`, `obstaculo` e `cartao` não são palavras reservadas: só têm sentido depois de `ao`, então `cartao` segue livre como variável. |
| 5 | Léxico | A | 0:50 | Uma regex mestre, montada juntando um grupo nomeado por token; a ordem importa (operadores de dois caracteres antes dos de um). São 44 tokens: 18 palavras reservadas, 1 identificador, 3 literais, 14 operadores, 7 delimitadores e o fim de arquivo. Espaço e comentário são descartados. Erro léxico informa linha e coluna. Nomes de métodos como `ler` são identificadores; quem valida é o semântico. |
| 6 | Sintático | A | 1:10 | Parser descendente recursivo com um token de lookahead, uma função por regra. A precedência está na cadeia ou, e, igualdade, comparação, termo, fator, unária, posfixo. A AST tem 17 tipos de nó. A árvore mostrada é a do controle_nfc: declaração, evento, atribuição com `nfc.ler()` e um `se` com condição, ramo então e ramo senão. O comando `tupa ast` imprime a árvore completa. |
| 7 | Semântico | F | 1:10 | Estas mensagens saíram do compilador real. Primeiro `led.roxo()`: o método não existe e ele lista `verde()`, `vermelho()` e `apagar()`. Depois `ir.enviar()`: a mensagem explica que o `ir` é um sensor de obstáculo, sem transmissor. Foi decisão após conferir o hardware: saíram `ir.enviar` e `ir.receber`, entrou `ir.detectado`. A fase também barra evento repetido e botão sem pino na placa. O compilador para no primeiro erro e não gera código. |
| 8 | Geração de código | F | 1:10 | O gerador percorre a AST e produz um `.ino` pronto para o arduino-cli. Pinagem, SPI, FQBN, biblioteca e a lista de UIDs vêm de `esp32_wrover.json`; trocar de placa é trocar o arquivo. `ao iniciar` vira o corpo do `setup()`, os demais eventos viram blocos no `loop()`. O botão tem debounce de 50 ms por `millis()`, sem `delay`. `nfc.ler()` espera até 3 s; sem cartão, resultado inválido. A lista de UIDs fica na placa, não na linguagem, porque pedia menos mudança. Os três sketches compilam com arduino-cli. |
| 9 | Métricas | F | 0:50 | Linhas de código sem brancos nem comentários. controle_nfc: 12 de Tupã viram 100 de C++, razão 8,3. teste_hardware: 23 viram 112, razão 4,9; o manual equivalente tem 51. O gerado é maior que o manual porque inclui debounce, checagem do RC522, UIDs e logs. A razão mede quanto o estudante deixa de escrever. A suíte tem 50 testes passando. |
| 10 | Playground | G | 0:45 | O compilador roda em tupa.mlutegar.com: FastAPI no servidor, React e CodeMirror no navegador. Abas de tokens, AST, erros, C++, métricas e Como gravar. Erro clicável leva à linha; dá para copiar ou baixar o `.ino`. O QR code abre o site no celular de quem quiser testar. Código aberto, licença MIT. |
| 11 | Hardware e demo | G | demo 3 a 4 min | Hardware: ESP32-WROVER-DEV, RC522, sensor IR de obstáculo, botão e dois LEDs, cerca de R$ 120. Passos: abrir o site, compilar `controle_nfc`, baixar o `.ino`, gravar com a placa ESP32 Wrover Module a 115200. Serial mostra a checagem do RC522. Botão com cartão `33 7A 87 F7`: LED verde, acesso liberado. Botão com `33 8F BD F7`: LED vermelho, acesso negado. Botão sem cartão: após 3 s, nenhum detectado e negado. |
| 12 | Conclusão | M | 0:45 | Entregamos uma linguagem com 44 tokens, lexer por regex mestre, parser descendente recursivo, AST de 17 tipos, erros didáticos, gerador para ESP32, 50 testes, site no ar e protótipo de cerca de R$ 120. Próximos passos: atualização OTA, IR transmissor com hardware novo e testes com estudantes. Tudo em licença MIT. Perguntas? A placa está aqui do lado. |

## Divisão por pessoa

| Quem | Slides | Tempo de fala |
|---|---|---|
| Michel Lutegar | 1, 2, 3, 12 | 3:00 |
| André Costa | 4, 5, 6 | 3:00 |
| Felipe Dutrain | 7, 8, 9 | 3:10 |
| Guilherme Lopes | 10, 11 | 0:45 + demo |

Total de fala: 9:55, mais a demo.

## Antes da banca

- [ ] % TODO (placa): gravar o `.ino` gerado por `controle_nfc.tupa` na placa e testar os três casos (liberado, negado, sem cartão). Até hoje só o `teste_hardware.ino` manual foi validado em bancada (26/10/2026).
- [ ] Compilar o `controle_nfc` no site e baixar o `.ino` com antecedência, como cópia local.
- [ ] Placa ligada por USB, Arduino IDE aberta em ESP32 Wrover Module, Monitor Serial em 115200, cartões à mão.
- [ ] Abrir `apresentacao/index.html` em tela cheia (F11) e testar a tecla N.

## Plano B da demo

1. **Gravação falhou, mas a placa está viva:** manter gravada a placa com o `.ino` gerado antes da banca; se a regravação ao vivo falhar, usar a placa como está e seguir para os cartões.
2. **Placa ou USB não respondem:** passar o vídeo tutorial (`roteiro-video-tutorial`) e narrar por cima.
3. **Sem internet:** abrir o `.ino` baixado antes, mostrar o `index.html` (autocontido, só as fontes dependem de rede) e o vídeo tutorial.
4. **Playground fora do ar:** usar `python -m compilador build examples/controle_nfc.tupa` no terminal e mostrar o C++ gerado; o vídeo cobre o resto.
5. **Em qualquer falha:** mostrar no playground a aba C++ e a aba Como gravar, que provam o fluxo sem a placa.
