# REGISTRO

Diário de decisões e mudanças.

## 2026-11-08: P01, levantamento do estado real
- Levantamento do estado real do repositório, registrado em `docs/CONTEXTO.md` (conforme `PROMPTS.md`).

## 2026-11-08: P02, estrutura do repositório
- `src/tupac/` virou `compilador/` (imports relativos, sem quebra); `tupa.py` substituído por `pyproject.toml` (comando `tupa`) e `python -m compilador`.
- Artigo em `artigo/main.tex` (era `IEEE-conference-template-062824.tex`), figuras em `artigo/figuras/`.
- `examples/controle_nfc.ino` (manual) movido para `firmware/controle_nfc_manual.ino`.
- Testes: 11 passando, igual ao P01.

## 2026-11-08: P03, compilador ajustado ao hardware real
- Fonte da verdade `firmware/teste_hardware.ino` e as fotos estavam só em `tupa_pacote_08-11.zip`; extraídos para `firmware/` e `artigo/figuras/` (nada existente foi sobrescrito).
- Parte A: `compilador/placas/esp32_wrover.json` (pinos, SPI, FQBN, biblioteca, UIDs, timeout) + `--placa`; `firmware/pinagem.md` reescrito.
- Parte B: debounce por `millis()`, `nfc.ler()` com espera de 3 s, UIDs da placa, erro semântico para botão sem pino, LEDs apagados, logs em português, checagem do RC522, includes condicionais, cabeçalho com origem `.tupa`, saída `<pasta>/<pasta>.ino`.
- Parte C: `escrever` (token novo, total 44 com EOF), eventos `ao iniciar`, `ao obstaculo`, `ao cartao` (nomes contextuais, `TK_ID`), `examples/teste_hardware.tupa`.
- Decisões: lista de UIDs fica no arquivo da placa (nenhum token/regra extra); `cartao.id` virou `cartao.uid`; `ir.enviar/receber` removidos, entra `ir.detectado()` (sensor de obstáculo, sem TX).
- Diferença conhecida: o manual acende o LED vermelho enquanto o botão está apertado; o Tupã acende por 300 ms a cada aperto (LED apaga ao fim do evento).
- Validação: os 3 sketches compilam com `arduino-cli` (core esp32 3.3.12, MFRC522 1.4.12); 50 testes passando. Falta testar na placa.

## P04 · Playground web (08/11/2026) · concluído · commits cdc2720 e 1a480f3

**Resultado**
- `to_dict()` em Token, TupaError e nós da AST, sem mudar comportamento.
- FastAPI (`web/api/main.py`): `POST /api/compilar`, `GET /api/exemplos`, `GET /api/saude`, `GET /api/linguagem`. Limite de 20 KB (413) e timeout de 5 s.
- Front Vite + React + CodeMirror 6 no visual do pitch: abas Tokens, AST, Erros, C++, Métricas; clique no erro leva à linha; copiar/baixar `.ino`; `Ctrl+Enter` compila.
- Docker multi-stage, usuário não root, compose em `127.0.0.1:8000` com healthcheck.
- Não validado no navegador (visual, realce e clique no erro).

**Como testar**
1. `docker compose up --build` e abrir http://localhost:8000
2. `Ctrl+Enter` no exemplo canônico e conferir as 5 abas.
3. Trocar `led.verde();` por `led.roxo();`: aba Erros mostra o erro; clicar leva à linha.
4. Aba C++: baixar o `.ino`.
5. `curl http://localhost:8000/api/saude`

---

## P05 · Artigo IEEE (08/11/2026) · concluído parcial · commit 405c6c4

**Resultado**
- `latexmk -pdf` sem erros; corrigidos `\graphicspath` e babel (`brazilian`).
- Léxico e sintático descritos com a técnica real; EBNF real; erro semântico real.
- Subseção "Ambiente Web" nova.
- Números e hardware foram atualizados depois no P07.
- URLs das referências não conferidas online.

**Pendências do João**
- E-mails de Michel e André; confirmar `aluno` x `alunos` no e-mail do Guilherme.
- Nome do professor nos Agradecimentos.
- Datasheet do MFRC522 (ano, revisão, URL).

**Como testar**
1. `cd artigo && latexmk -pdf main.tex`
2. `grep -n "TODO" main.tex` para ver o que ainda falta.

---

## 2026-11-08: P07, artigo atualizado
- `artigo/main.tex`: figura do protótipo (prototipo.jpg, 3 painéis), pinagem da placa ESP32-WROVER, EBNF e tokens com `escrever` e eventos novos (44 tokens com EOF), tabela com controle_nfc e teste_hardware (Tupã, gerado, manual), razões 8,3 e 4,9, 50 testes. 5 páginas, latexmk sem erros.
- Pendente: gravar o .ino gerado na placa; TODOs de e-mails e nome do professor.

---

## P06 · Deploy no VPS (08/11/2026) · concluído

**Resultado**
- Container `tupa-tupa-1` rodando e `healthy`, publicado só em `127.0.0.1:8000` (proxy reverso na frente).
- Acesso ao repositório pelo VPS com deploy key `~/.ssh/tupa_deploy` e alias SSH `github-tupa`.
- URL pública: https://tupa.mlutegar.com
- Validações feitas: `/api/saude` responde `ok` pela URL pública; compilação do exemplo canônico pelo playground; healthcheck do container verde.
- `deploy-git.ps1`: `git push origin main`, depois `git pull`, build e `docker compose up -d` no VPS pelo alias `ssh kvm8`.
- Dados do servidor (IP, host, guia de deploy) ficam fora do repositório.

---

## P09 · Preparação para deploy (08/11/2026) · concluído · commit 5a0ae57

**Resultado**
- `.gitignore`: `obsidian-compilador-esp32/` e `tupa_pacote_08-11.zip` ficam fora do repositório.
- `REGISTRO.md`: entrada do P01 adicionada.
- `artigo/main.pdf` recompilado e versionado (124544 -> 386994 bytes).

---

## P10 · Push (08/11/2026) · concluído · commit fc1a250

**Resultado**
- Push de `main` para `origin` com o registro completo P01 a P10 (`fc1a250`), liberando o deploy do P06.

---

## P11 · README, registro do deploy e limpeza de infraestrutura (08/11/2026) · concluído

**Resultado**
- Parte A: varredura do repositório rastreado (IP, nome do host, provedor, `root@`, chaves SSH): nenhuma ocorrência de dado sensível; `docs/deploy-kvm8.md` não estava rastreado e agora está no `.gitignore`. Histórico do git limpo (`git log -S` sem resultados). Histórico não reescrito.
- Parte B: novo `README.md` (logo, link do playground, screenshot em `docs/img/playground.png`, exemplo, métricas, pipeline, linguagem, hardware, como começar).
- Parte C: P06 marcado como concluído; P10 e P11 adicionados.
- Licença ainda indefinida: README diz "Licença: a definir".

---

## P12 · URL oficial, licença MIT e site (08/11/2026) · concluído

**Resultado**
- URL oficial: https://tupa.mlutegar.com (substituída em README e REGISTRO; nenhuma ocorrência restante do domínio antigo).
- `LICENSE` MIT (Michel Lutegar, André Costa, Felipe Dutrain, Guilherme Lopes); `pyproject.toml` com `license = "MIT"` (setuptools>=77); README aponta para o LICENSE.
- Site: rodapé com licença, disciplina, autores e link do GitHub (repositório público); nova aba "Como gravar" (5 passos + tabela de pinagem do ESP32-WROVER).
- Download conferido: sai como `<programa>.ino` (ex.: `controle_nfc.ino`).
- Testes: 50 passed; build do front sem erro. Screenshot: `docs/img/site-como-gravar.png`.

---

## P13 · Apresentação final (08/11/2026) · concluído

**Resultado**
- `apresentacao/index.html`: deck autocontido de 12 slides, 16:9, setas navegam, tecla N mostra as notas, identidade do pitch (fundo #0E1116, laranja #FF7A1A, verde #2EE6A6, logo), código com realce das palavras reservadas reais. Fontes só do Google Fonts.
- `apresentacao/apresentacao.pdf`: 12 páginas, exportado do HTML com chromium headless (playwright). Conferido por screenshot de cada slide, sem sobreposição nem estouro.
- `apresentacao/roteiro.md`: fala por slide, tempo (9:55 + demo de 3 a 4 min), divisão entre os quatro autores e plano B da demo.
- Erros do slide 7 e métricas do slide 9 vieram de execução real (50 testes passando; controle_nfc 12 para 100, 8,3x; teste_hardware 23 para 112, 4,9x; manual com 51). Screenshot do playground tirado de https://tupa.mlutegar.com.
- `artigo/` não foi alterado. Fonte do deck: `fonte.html` + `build.py` (gera o `index.html`) e `pdf.py`.

**Avisos**
- Os números oficiais batem com o repositório. As cores do prompt (#FF7A1A, #2EE6A6) diferem em 2 unidades das do pitch (#FF7A18, #2EE6A8); usei as do prompt.
- `docs/Tupa-Pitch.pdf` está protegido por senha e não abriu; a identidade visual veio de `gerar-pitch.js` e da marca no Obsidian.
- % TODO (placa): o `.ino` gerado ainda pode não ter sido gravado na placa; o aviso está só nas notas dos slides 8 e 11 e no `roteiro.md`.

---

## P14 · Análise semântica, tabela de erros e compilação (08/11/2026) · concluído

**Resultado**
- Códigos de erro estáveis, sem mudar o texto das mensagens: L01; S01 a S13; E01 a E21 (E06 e E15 são defesas internas); G01 a G05 (placa e arquivo). `codegen.py` não emite erro.
- `TupaError` e `ErroPlaca` têm `codigo`. CLI: `erro semantico [E19] - linha 3, coluna 12` e `erro de placa [G01]: ...`. API: campo `codigo` em cada erro e `GET /api/erros`. Site: selo do código e tabela recolhível na aba Erros.
- Mudança visível: o cabeçalho do erro ganhou o código entre colchetes. Slides em `apresentacao/` e notas do Obsidian ainda mostram o formato antigo (sem código).
- `compilador/catalogo_erros.py` é a fonte única; `tools/gerar_tabela_erros.py` gera `docs/tabela-de-erros.md`.
- Tabela de símbolos: `AnalisadorSemantico.simbolos` e comando `tupa simbolos`.
- Docs novos: `docs/analise-semantica.md`, `docs/tabela-de-erros.md`, `docs/compilacao.md`; README com seção "Documentação".
- `tests/test_erros.py`: um teste por erro (o exemplo gera aquele código e mensagem), tabela sincronizada com o catálogo, todo código do fonte está no catálogo. Total: 98 passed. Build do front sem erro.
- Compilação real com arduino-cli 1.5.1, core esp32 3.3.12, MFRC522 1.4.12: 4 sketches compilam (gerados de controle_nfc e teste_hardware, mais os 2 manuais), cerca de 293 KB de flash (22%) e 22 KB de RAM (6%). O pedido falava em 3 sketches; há 4 em `firmware/`, registrei os 4.

**Avisos**
- `arduino-cli` não está no PATH; fica em `C:/Users/mlute/arduino-cli-bin/`.
- P08 e P15 não têm registro: ficaram como "sem registro" e "pendente" no `PROMPTS.md`.
- Falta gravar o `.ino` gerado na placa e conferir o site no navegador (só o build foi feito).

---

## P15 · Artigo expandido de 5 para 9 páginas (08/11/2026) · concluído

**Resultado**
- `artigo/main.tex` (IEEEtran conference) passou de 5 para **9 páginas**, `latexmk -pdf` sem erros, sem `??` e sem referência indefinida.
- Seções novas: Objetivos (geral e 6 específicos); Fundamentação (DSLs internas x externas, fases, transpilação, ESP32/Arduino); Metodologia (processo, cronograma, ferramentas, testes, Git); Ambiente Web; Plataforma de Hardware (pinagem, materiais, foto); Discussão e Limitações.
- Léxico: tabela dos 44 tokens (table*), regex mestre resumida, tokenização real de `cartao = nfc.ler();`. Sintático: EBNF, 17 nós, AST do controle_nfc em TikZ. Semântico: escopos, tabela de símbolos, API de hardware, resumo da Tabela de Erros (40 códigos: 1 L, 13 S, 21 E, 5 G) e erros E19 e E04 reais. Geração: trecho do JSON da placa, tabela evento para C++, trecho do `.ino` gerado.
- Resultados: 98 testes (41 + 46 + 11, número atual, não 41+9), memória flash/RAM de `docs/compilacao.md`, tabela de métricas.
- Referências conferidas no Crossref: Mernik et al. 2005, Resnick et al. 2009, Hudak 1996, Devine et al. 2019, Fraser 2015. Fowler (2010) é livro, sem DOI. Acrescentei FastAPI, React, Docker e MIT (URLs com HTTP 200).

**Avisos**
- A referência do Portugol Studio foi trocada: o artigo de 2014 que constava não foi achado no Crossref; usei o de 2019 (Esteves et al., WEI), que existe. Os autores listados vêm do Crossref.
- A figura de erro agora mostra o formato real com código, `[E19]`, linha 3 coluna 12 (antes era um exemplo antigo, linha 11).
- O cronograma usa só os meses do `Cronograma.md` (placeholder do Obsidian), sem datas exatas. O custo de R$ 120 é estimativa de varejo, não nota fiscal.
- Mantidos os `% TODO`: e-mails de Michel e André, domínio do e-mail do Guilherme, nome do professor, datasheet MFRC522, tempo de compilação/gravação, testes com usuários e `% TODO (placa)` (gravação do `.ino` gerado).

---

## P16 · Apresentação final refeita do zero (09/11/2026) · concluído

**Resultado**
- `apresentacao/` substituída: 14 slides em `index.html` autocontido (16:9, setas navegam, N mostra as notas, F tela cheia; só Google Fonts como recurso externo), `apresentacao.pdf` (14 páginas, 1 slide por página, playwright headless) e `roteiro.md` (fala por slide, 10:00 de fala mais 3:00 de demo, divisão entre os quatro, plano B da demo e 8 perguntas prováveis).
- Identidade do pitch: fundo #0E1116, laranja #FF7A1A, verde #2EE6A6 e logo. Código em mono com realce das 18 palavras reservadas reais do lexer.
- Fonte única do conteúdo: `slides.py` (HTML, quem fala, tempo e fala). `build.py` gera `index.html` e `roteiro.md` e **falha se algum número divergir do repositório**: 44 tokens (contados em `lexer.py`/`tokens.py`), 17 nós de AST, 40 códigos (1 L, 13 S, 21 E, 5 G, do catálogo), linhas de código dos `.tupa`, `.ino` gerados e manual (12, 100, 23, 112, 51), razões 8,3 e 4,9, flash e RAM de `docs/compilacao.md`. Diagramas (pipeline e AST), tokenização e trechos de código saem dos arquivos reais; a saída do erro [E19] é a do compilador.
- `shots.py` tira o screenshot de cada slide e checa estouro, sobreposição e palavras por slide; `pdf.py` gera o PDF. Todos os 14 slides sem estouro; textos entre 5 e 32 palavras fora de código, tabelas e diagramas (o resto está nas notas).
- QR code refeito para https://tupa.mlutegar.com (biblioteca `qrcode`, só no build).

**Avisos**
- Todos os números do prompt bateram com o repositório; nenhuma divergência.
- `docs/Tupa-Pitch.pdf` continua protegido por senha; a identidade visual veio das cores do prompt, do `gerar-pitch.js` e do logo em `web/app/public/tupa-icone.png`.
- A foto do slide 13 usa duas vistas de `artigo/figuras/` (vista superior e visão geral), e o screenshot do slide 12 é `docs/img/playground.png`; o thumbnail da aba Como gravar é `docs/img/site-como-gravar.png`.
- O arquivo do vídeo tutorial não está no repositório (só o roteiro `roteiro-video-tutorial.md.pdf`, não versionado): o plano B do `roteiro.md` pede que o vídeo esteja baixado na máquina da banca.
- % TODO (placa): o `.ino` gerado de `controle_nfc.tupa` ainda não foi gravado e testado nos três casos (liberado, negado, sem cartão). O aviso está só nas notas do slide 13 e no `roteiro.md`; a pergunta 8 da banca depende dele.
- Cada slide fala em média 2:30 por pessoa (Michel 2:30, André 2:25, Felipe 2:25, Guilherme 2:40).

---

## P17 · Autores, orientador e resultado na placa (09/11/2026) · concluído

**Resultado**
- Artigo: e-mails dos quatro autores (@alunos.ibmec.edu.br) e agradecimento ao Prof. William Barbosa, orientador. O e-mail do professor não aparece em lugar nenhum. Apresentação (capa, roteiro) e README (seção Autores) com "Orientador: Prof. William Barbosa".
- Resumo, Resultados (nova subseção "Validação do código gerado na placa"), Tabela de métricas, Discussão, Conclusão e Trabalhos futuros ajustados ao resultado da placa; todos os `% TODO (placa)` removidos do artigo e das notas da apresentação.
- `main.pdf` com 9 páginas, sem erros; `apresentacao.pdf` regerado (14 slides).

**Avisos**
- Não se afirma que o código gerado leu cartão nem acendeu o LED verde. Trabalho futuro: validar a leitura de cartões com o código gerado após substituir ou ressoldar o módulo RC522.
- Mantidos os `% TODO` de tempo de compilação e gravação (sem dado real), testes com usuários e datasheet do MFRC522.

## Validação na placa (09/11/2026)

`controle_nfc` gerado pelo Tupã, gravado com Arduino IDE (placa ESP32 Wrover, COM5) e executado no ESP32-WROVER-DEV. Monitor Serial a 115200:

- Leitor: `RC522 versao: 0xB2 -> OK` (chip compatível/clone).
- Botão com debounce: `Botao: PRESSIONADO` uma única vez por aperto e `Botao: solto`.
- Espera de 3 s: `Cartao: nenhum detectado em 3 s`, depois `acesso negado` e LED vermelho, repetido várias vezes de forma consistente.

O firmware manual (`teste_hardware.ino`) também foi regravado no mesmo dia: botão e sensor IR responderam (`IR: obstaculo detectado` / `IR: livre`).

Nesse dia o leitor não detectou cartões, nem com o firmware manual: indício de falha de contato ou antena no módulo RC522. A leitura de cartões e UIDs foi validada no teste de bancada de 26/10/2026, com o mesmo hardware.
