# Análise Semântica e Geração de Código (back-end)

Documenta as **fases 3 e 4** do compilador Tupã.

- Semântica: `compilador/semantic.py`
- Geração de código (back-end): `compilador/codegen.py`

---

## Análise Semântica

Percorre a AST validando:

1. **Variáveis** declaradas antes do uso (atribuição implícita cria a variável, ex.: `cartao = nfc.ler();`).
2. **Tipos** em declarações, condições (`se` exige booleano) e comandos (`esperar`/`repetir` exigem número).
3. **Hardware** — existência do módulo e do método/propriedade, e número de argumentos.

### API de hardware validada

| Módulo | Métodos | Propriedades (via objeto) |
|--------|---------|---------------------------|
| `led`  | `verde()`, `vermelho()`, `apagar()` | — |
| `nfc`  | `ler()` → objeto `cartao` | `cartao.valido`, `cartao.id` |
| `ir`   | `enviar(codigo)`, `receber()` | — |
| `botao`| `pressionado()` | — |

### Exemplo de erro amigável

```
$ python tupa.py build erro.tupa

erro semantico - linha 3, coluna 12
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
| `ao botao(1) { ... }` | `if (digitalRead(BOTAO_1)==LOW) { ...debounce... }` dentro do `loop()` |
| `cartao = nfc.ler();` | `Cartao cartao = nfcLer();` |
| `cartao.valido == verdadeiro` | `(cartao.valido == true)` |
| `led.verde();` | `ledVerde();` |
| `esperar(1500);` | `delay(1500);` |
| `se/senao` | `if/else` |
| `repetir(n) { }` | `for (int _i=0; _i<n; _i++) { }` |

O back-end emite automaticamente os `#include`, os `#define` de pinos, os
helpers (`ledVerde`, `nfcLer`, …) e o `setup()` — código que o usuário nunca
escreve. Bibliotecas de hardware entram só quando usadas (ex.: `MFRC522` apenas
se `nfc` aparecer).

### Rodar o back-end

```bash
python tupa.py build examples/controle_nfc.tupa
# -> output/controle_nfc.ino
```

Depois, compilar/enviar para a placa (fora do compilador):

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 output/
arduino-cli upload  --fqbn esp32:esp32:esp32 -p COM3 output/
```

---

## Testes

`tests/test_compilador.py` cobre lexer, parser, semântica e codegen (11 testes).

```bash
python tests/test_compilador.py     # runner embutido, sem dependências
# ou
python -m pytest tests/ -q
```
