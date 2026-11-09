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

## 2026-11-08: P07, artigo atualizado
- `artigo/main.tex`: figura do protótipo (prototipo.jpg, 3 painéis), pinagem da placa ESP32-WROVER, EBNF e tokens com `escrever` e eventos novos (44 tokens com EOF), tabela com controle_nfc e teste_hardware (Tupã, gerado, manual), razões 8,3 e 4,9, 50 testes. 5 páginas, latexmk sem erros.
- Pendente: gravar o .ino gerado na placa; TODOs de e-mails e nome do professor.
