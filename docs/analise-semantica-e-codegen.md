# Análise Semântica e Geração de Código (back-end)

Documenta as **fases 3 e 4** do compilador Tupã.

- Semântica: `compilador/semantic.py`
- Geração de código (back-end): `compilador/codegen.py`

---

## Análise Semântica

> Documentação completa (tabela de símbolos, ordem das verificações, erros E01 a E21): [`analise-semantica.md`](analise-semantica.md) e [`tabela-de-erros.md`](tabela-de-erros.md).

Percorre a AST validando:

1. **Variáveis** declaradas antes do uso (atribuição implícita cria a variável, ex.: `cartao = nfc.ler();`).
2. **Tipos** em declarações, condições (`se` exige booleano) e comandos (`esperar`/`repetir` exigem número).
3. **Hardware** — existência do módulo e do método/propriedade, e número de argumentos.

### API de hardware validada

| Módulo | Métodos | Propriedades (via objeto) |
|--------|---------|---------------------------|
| `led`  | `verde()`, `vermelho()`, `apagar()` | — |
| `nfc`  | `ler()` → objeto `cartao` | `cartao.valido`, `cartao.uid` |
| `ir`   | `detectado()` (sensor de obstáculo; não existe IR TX) | — |
| `botao`| `pressionado()` | — |

Também valida: nome de evento (`ao iniciar`, `ao botao(N)`, `ao obstaculo`, `ao cartao`), evento repetido,
botão sem pino na placa e o argumento de `escrever` (não imprime `cartao` inteiro nem chamada sem valor).
Dentro de `ao cartao` a variável `cartao` já existe.

### Exemplo de erro amigável

```
$ python -m compilador build erro.tupa

erro semantico [E19] - linha 3, coluna 12
    metodo inexistente no modulo 'led'
    disponiveis: verde(), vermelho(), apagar()
    led.roxo()

compilacao interrompida: 1 erro
```

---

## Geração de Código (back-end)

Traduz a AST validada para **C++/Arduino (`.ino`)** pronto para a Arduino CLI.

### Mapeamento principal

| Tupã | C++/Arduino |
|------|-------------|
| `dispositivo X { ... }` | comentário + `setup()` + `loop()` |
| `inteiro/decimal/texto/booleano` | `int` / `float` / `String` / `bool` |
| `ao iniciar { ... }` | corpo do `setup()` (depois de inicializar o hardware) |
| `ao botao(1) { ... }` | debounce por `millis()` com detecção de borda, dentro do `loop()` |
| `ao obstaculo { ... }` | borda livre -> obstáculo em `digitalRead(IR_PIN)` |
| `ao cartao { ... }` | `Cartao cartao; if (nfcTentar(cartao)) { ... }` |
| `escrever(x);` | `Serial.println(x);` |
| `cartao = nfc.ler();` | `Cartao cartao = nfcLer();` (espera até 3 s; sem cartão = inválido) |
| `cartao.valido == verdadeiro` | `(cartao.valido == true)` |
| `led.verde();` | `ledVerde();` |
| `esperar(1500);` | `delay(1500);` |
| `se/senao` | `if/else` |
| `repetir(n) { }` | `for (int _i=0; _i<n; _i++) { }` |

O back-end emite automaticamente os `#include`, os `#define` de pinos, os
helpers (`ledVerde`, `nfcLer`, …) e o `setup()` — código que o usuário nunca
escreve. Só entram os módulos usados (ex.: `MFRC522`/`SPI` apenas se houver `nfc` ou `ao cartao`).
Pinos, SPI, FQBN, tempo de espera do NFC e UIDs autorizados vêm de `compilador/placas/<placa>.json`
(flag `--placa`, padrão `esp32_wrover`). O cabeçalho diz de qual `.tupa` o código veio e cada bloco
tem um comentário `// [arquivo.tupa:linha]`.

### Rodar o back-end

```bash
python -m compilador build examples/controle_nfc.tupa -o firmware/controle_nfc_gerado
# -> firmware/controle_nfc_gerado/controle_nfc_gerado.ino  (pasta homônima, como o arduino-cli exige)
```

Depois, compilar/enviar para a placa (fora do compilador):

```bash
arduino-cli compile --fqbn esp32:esp32:esp32wrover firmware/controle_nfc_gerado
arduino-cli upload -p COMx --fqbn esp32:esp32:esp32wrover firmware/controle_nfc_gerado
```

---

## Testes

`tests/test_compilador.py` cobre lexer, parser, semântica e codegen (inclui snapshots dos `.ino` gerados);
`tests/test_web_api.py` cobre a API do playground.

```bash
python -m pytest tests/ -q
```
```
