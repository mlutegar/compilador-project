# Pinagem da protoboard (ESP32)

Valores **hardcoded** em `compilador/codegen.py` (ainda não configuráveis).
**Não verificado contra a montagem física**: confirmar com a protoboard.

| Símbolo | GPIO | Observação |
|---|---|---|
| `LED_VERDE` | 16 | sempre emitido |
| `LED_VERMELHO` | 17 | sempre emitido |
| `BOTAO_1` | 4 | `INPUT_PULLUP`, ativo em LOW (botão entre GPIO e GND) |
| `NFC_SS` (SDA) | 5 | MFRC522, só se o programa usa `nfc` |
| `NFC_RST` | 22 | MFRC522 |
| `IR_ENVIA` / `IR_RECEBE` | 25 / 26 | só se usa `ir` (stub) |
| SPI SCK / MISO / MOSI | 18 / 19 / 23 | pinos padrão do ESP32 |

## Arquivos

- `controle_nfc_gerado.ino`: saída de `tupa build examples/controle_nfc.tupa`.
- `controle_nfc_manual.ino`: versão escrita à mão (referência para comparação no pitch).

O Arduino exige o sketch em pasta homônima (`controle_nfc/controle_nfc.ino`) para `arduino-cli compile`.
