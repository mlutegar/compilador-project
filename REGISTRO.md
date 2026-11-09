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

## P06 · Deploy no VPS · pendente

Bloqueado em 08/11/2026 porque o push não tinha sido feito e faltava `docs/deploy-kvm8.md`. Destravado pelo P09 e P10.

---

## P09 · Preparação para deploy (08/11/2026) · concluído · commit 5a0ae57

**Resultado**
- `.gitignore`: `obsidian-compilador-esp32/` e `tupa_pacote_08-11.zip` ficam fora do repositório.
- `REGISTRO.md`: entrada do P01 adicionada.
- `artigo/main.pdf` recompilado e versionado (124544 -> 386994 bytes).
