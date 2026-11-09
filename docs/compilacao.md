# Evidência: código compilando para o ESP32

O compilador Tupã gera `.ino`; quem o transforma em binário para a placa é o `arduino-cli`. Esta página registra
que o C++ gerado compila de fato para a placa-alvo (ESP32-WROVER), com o resultado real de cada sketch.

## Ambiente

| Item | Versão |
|---|---|
| arduino-cli | 1.5.1 (commit 01f3d4f2b, 2026-06-05) |
| core `esp32:esp32` | 3.3.12 |
| biblioteca MFRC522 | 1.4.12 |
| FQBN | `esp32:esp32:esp32wrover` (campo `fqbn` de `compilador/placas/esp32_wrover.json`) |

O `arduino-cli` foi instalado no P03 em `C:\Users\mlute\arduino-cli-bin\arduino-cli.exe` e não está no PATH do terminal.

## Comandos

```bash
arduino-cli version
arduino-cli core list                 # esp32:esp32  3.3.12
arduino-cli lib list MFRC522          # MFRC522      1.4.12

# gera o .ino a partir do Tupã (pasta homônima, como o arduino-cli exige)
python -m compilador build examples/controle_nfc.tupa   -o firmware/controle_nfc_gerado
python -m compilador build examples/teste_hardware.tupa -o firmware/teste_hardware_gerado

# compila
arduino-cli compile --fqbn esp32:esp32:esp32wrover firmware/controle_nfc_gerado
arduino-cli compile --fqbn esp32:esp32:esp32wrover firmware/teste_hardware_gerado
arduino-cli compile --fqbn esp32:esp32:esp32wrover <pasta com controle_nfc_manual.ino>
arduino-cli compile --fqbn esp32:esp32:esp32wrover <pasta com teste_hardware.ino>
```

Os `.ino` gerados em `firmware/` foram regenerados a partir dos `.tupa` atuais e são idênticos aos versionados.

## Saída real

Execução de 08/11/2026. As quatro compilações terminaram sem erro nem aviso.

### `controle_nfc_gerado` (gerado de `examples/controle_nfc.tupa`)

```
Sketch uses 293740 bytes (22%) of program storage space. Maximum is 1310720 bytes.
Global variables use 22308 bytes (6%) of dynamic memory, leaving 305372 bytes for local variables. Maximum is 327680 bytes.
```

### `teste_hardware_gerado` (gerado de `examples/teste_hardware.tupa`)

```
Sketch uses 293880 bytes (22%) of program storage space. Maximum is 1310720 bytes.
Global variables use 22308 bytes (6%) of dynamic memory, leaving 305372 bytes for local variables. Maximum is 327680 bytes.
```

### `controle_nfc_manual.ino` (escrito à mão, referência de comparação)

```
Sketch uses 291776 bytes (22%) of program storage space. Maximum is 1310720 bytes.
Global variables use 22284 bytes (6%) of dynamic memory, leaving 305396 bytes for local variables. Maximum is 327680 bytes.
```

### `teste_hardware.ino` (escrito à mão, fonte da verdade do hardware)

```
Sketch uses 292548 bytes (22%) of program storage space. Maximum is 1310720 bytes.
Global variables use 22300 bytes (6%) of dynamic memory, leaving 305380 bytes for local variables. Maximum is 327680 bytes.
```

## Resumo

| Sketch | Flash | RAM |
|---|---:|---:|
| `controle_nfc_gerado` | 293 740 B (22%) | 22 308 B (6%) |
| `teste_hardware_gerado` | 293 880 B (22%) | 22 308 B (6%) |
| `controle_nfc_manual` | 291 776 B (22%) | 22 284 B (6%) |
| `teste_hardware` (manual) | 292 548 B (22%) | 22 300 B (6%) |

O código gerado custa cerca de 2 KB de flash e 24 bytes de RAM a mais que o manual equivalente (diferença de
`controle_nfc`: 1 964 B de flash e 24 B de RAM). A maior parte dos ~290 KB é o core do ESP32.

## O que ainda não foi feito

Compilar prova que o C++ é válido para a placa; **gravar e testar na placa física ainda não foi feito** com o `.ino` gerado.
