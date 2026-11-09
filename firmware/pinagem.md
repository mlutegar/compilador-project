# Pinagem da protoboard (ESP32-WROVER-DEV)

**Conferido em bancada em 26/10/2026** com `firmware/teste_hardware.ino` (escrito à mão),
fotos e Monitor Serial em `artigo/figuras/`.

Fonte única para o compilador: `compilador/placas/esp32_wrover.json` (flag `--placa`, padrão `esp32_wrover`).
Este arquivo é a versão legível do mesmo conteúdo.

- Placa na Arduino IDE: **ESP32 Wrover Module**
- FQBN: `esp32:esp32:esp32wrover`
- Biblioteca: **MFRC522** (GithubCommunity)
- Serial Monitor: 115200

| Função | GPIO | Observação (conferido em bancada) |
|---|---|---|
| RC522 SS (SDA) | 5 | `SPI.begin(18, 19, 23, 5)` = SCK, MISO, MOSI, SS |
| RC522 RST | 22 | |
| RC522 SCK / MISO / MOSI | 18 / 19 / 23 | alimentar o RC522 em 3,3 V |
| Botão 1 | 4 | `INPUT_PULLUP`, ativo em LOW (botão entre o GPIO e o GND) |
| LED verde | 25 | `OUTPUT`, ativo em HIGH |
| LED vermelho | 26 | `OUTPUT`, ativo em HIGH |
| Sensor IR de obstáculo | 34 | `INPUT`, ativo em LOW. GPIO 34 é só entrada e **não tem pull-up interno** |

## Sensor IR

É um **sensor IR de obstáculo** (emissor e receptor no mesmo módulo, saída digital), não um controle remoto.
**Não existe IR TX.** A saída vai a LOW quando há obstáculo.

## RC522: teste de presença

Ler o registrador `VersionReg`. Valor `0x00` ou `0xFF` indica falha (confira SPI, RST e 3,3 V).
O código gerado faz essa checagem no `setup()` e imprime o resultado no Serial.

## Cartões lidos no teste (UIDs reais)

`33 7A 87 F7`, `43 A3 6F F5`, `33 8F BD F7`.
Na demo, os dois primeiros ficam **autorizados** e `33 8F BD F7` fica **negado** (LED vermelho).
A lista está em `compilador/placas/esp32_wrover.json`, campo `nfc.uids_autorizados`.

## Arquivos

- `teste_hardware.ino`: firmware manual que provou o hardware.
- `controle_nfc_manual.ino`: versão manual antiga (referência para o pitch; usa pinos antigos).
- `controle_nfc_gerado/` e `teste_hardware_gerado/`: saídas do compilador (pasta homônima, formato do `arduino-cli`).
