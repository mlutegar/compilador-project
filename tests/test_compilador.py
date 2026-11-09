"""Testes do compilador Tupã: lexer, parser, semântica e codegen.

Rodar:
    python -m pytest tests/ -q      (se tiver pytest)
    python tests/test_compilador.py (execução direta, sem dependências)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from compilador.lexer import tokenizar          # noqa: E402
from compilador.parser import parsear           # noqa: E402
from compilador.semantic import analisar        # noqa: E402
from compilador.compiler import compilar        # noqa: E402
from compilador.errors import ErroSemantico, ErroLexico, ErroSintatico  # noqa: E402

EXEMPLO = """
dispositivo controle {
    inteiro tentativas = 3;
    ao botao(1) {
        cartao = nfc.ler();
        se cartao.valido == verdadeiro {
            led.verde();
            esperar(1500);
        } senao {
            led.vermelho();
        }
    }
}
"""


# ---------- Lexer ----------
def test_lexer_tipos_de_token():
    toks = tokenizar(EXEMPLO)
    tipos = [t.tipo for t in toks]
    assert tipos[0] == "TK_DISPOSITIVO"
    assert "TK_NFC" in tipos
    assert "TK_LED" in tipos
    assert "TK_SE" in tipos and "TK_SENAO" in tipos
    assert tipos[-1] == "TK_EOF"


def test_lexer_ignora_comentarios_e_valores():
    toks = tokenizar('inteiro x = 1500; # comentario\n')
    assert not any(t.tipo == "TK_COMENTARIO" for t in toks)
    intliteral = [t for t in toks if t.tipo == "TK_INT"][0]
    assert intliteral.valor == 1500


def test_lexer_caractere_invalido():
    try:
        tokenizar("inteiro x = @;")
        assert False, "deveria ter lançado ErroLexico"
    except ErroLexico:
        pass


# ---------- Parser / AST ----------
def test_parser_estrutura():
    ast = parsear(tokenizar(EXEMPLO))
    assert ast.nome == "controle"
    tipos = [type(n).__name__ for n in ast.corpo]
    assert "DeclVar" in tipos and "Evento" in tipos


def test_parser_erro_sintatico():
    try:
        parsear(tokenizar("dispositivo x { ao botao(1) { }"))  # falta '}'
        assert False, "deveria ter lançado ErroSintatico"
    except ErroSintatico:
        pass


# ---------- Semântica ----------
def test_semantica_ok():
    analisar(parsear(tokenizar(EXEMPLO)))  # não deve lançar


def test_semantica_metodo_inexistente():
    codigo = "dispositivo t { ao botao(1) { led.roxo(); } }"
    try:
        analisar(parsear(tokenizar(codigo)))
        assert False, "deveria ter lançado ErroSemantico"
    except ErroSemantico as e:
        assert "led" in str(e) and "roxo" in str(e)
        assert "verde()" in str(e)  # lista os métodos válidos


def test_semantica_variavel_nao_declarada():
    codigo = "dispositivo t { ao botao(1) { esperar(x); } }"
    try:
        analisar(parsear(tokenizar(codigo)))
        assert False
    except ErroSemantico:
        pass


# ---------- Codegen (back-end) ----------
def test_codegen_produz_ino_valido():
    ino = compilar(EXEMPLO)
    # boilerplate Arduino essencial
    assert "void setup()" in ino
    assert "void loop()" in ino
    # tradução das construções
    assert "nfcLer()" in ino
    assert "ledVerde()" in ino
    assert "ledVermelho()" in ino
    assert "delay(1500)" in ino
    assert "digitalRead(BOTAO_1)" in ino
    assert "cartao.valido == true" in ino
    assert "#include <MFRC522.h>" in ino


def test_codegen_sem_nfc_nao_inclui_mfrc():
    codigo = "dispositivo t { ao botao(1) { led.verde(); } }"
    ino = compilar(codigo)
    assert "MFRC522" not in ino
    assert "ledVerde()" in ino


def test_repetir_gera_for():
    codigo = "dispositivo t { ao botao(1) { repetir(3) { led.verde(); } } }"
    ino = compilar(codigo)
    assert "for (int _i = 0; _i < 3; _i++)" in ino


# ---------- Parte B: correções do .ino gerado ----------
import json  # noqa: E402

from compilador.cli import main as cli_main  # noqa: E402
from compilador.placa import carregar_placa  # noqa: E402


def _ino(codigo, **kw):
    return compilar(codigo, **kw)


def test_debounce_por_millis_com_borda():
    ino = _ino(EXEMPLO)
    assert "DEBOUNCE_MS" in ino and "millis()" in ino
    assert "botao1_estavel" in ino            # detecção de borda (estado estável)
    assert "delay(30)" not in ino             # o debounce antigo, bloqueante, sumiu
    assert "while (digitalRead" not in ino    # sem espera ocupada pela soltura


def test_nfc_ler_espera_com_timeout_e_encerra_cartao():
    ino = _ino(EXEMPLO)
    assert "#define NFC_TIMEOUT_MS 3000" in ino
    assert "(millis() - inicio) < NFC_TIMEOUT_MS" in ino
    assert "PICC_HaltA()" in ino and "PCD_StopCrypto1()" in ino
    assert "Cartao: nenhum detectado em 3 s" in ino   # sem cartão = inválido


def test_lista_de_uids_vem_da_placa():
    ino = _ino(EXEMPLO)
    assert "0x33, 0x7A, 0x87, 0xF7" in ino and "0x43, 0xA3, 0x6F, 0xF5" in ino
    assert "0x8F" not in ino                  # 33 8F BD F7 fica negado
    assert "DE, 0xAD" not in ino and "0xDE" not in ino


def test_lista_de_uids_troca_com_outra_placa(tmp_path):
    base = json.load(open(carregar_placa.__globals__["_DIR_PLACAS"] + "/esp32_wrover.json", encoding="utf-8"))
    base["nfc"]["uids_autorizados"] = ["33 8F BD F7"]
    arq = tmp_path / "outra.json"
    arq.write_text(json.dumps(base), encoding="utf-8")
    ino = _ino(EXEMPLO, placa=carregar_placa(str(arq)))
    assert "0x33, 0x8F, 0xBD, 0xF7" in ino and "0x7A" not in ino


def test_pinos_vem_da_placa():
    ino = _ino(EXEMPLO)
    for linha in ("#define LED_VERDE", "#define LED_VERMELHO"):
        assert linha in ino
    assert "LED_VERDE      25" in ino and "LED_VERMELHO   26" in ino
    assert "SPI.begin(18, 19, 23, 5)" in ino
    assert "pinMode(BOTAO_1, INPUT_PULLUP)" in ino
    assert " 16" not in ino and " 17" not in ino


def test_includes_so_dos_modulos_usados():
    sem_nfc = _ino("dispositivo t { ao botao(1) { led.verde(); } }")
    assert "#include" not in sem_nfc and "MFRC522" not in sem_nfc and "SPI" not in sem_nfc
    assert "NFC_SS" not in sem_nfc and "IR_PIN" not in sem_nfc
    com_nfc = _ino(EXEMPLO)
    assert "#include <SPI.h>" in com_nfc and "#include <MFRC522.h>" in com_nfc
    sem_led = _ino("dispositivo t { ao botao(1) { esperar(10); } }")
    assert "LED_VERDE" not in sem_led and "ledApagar" not in sem_led


def test_botao_sem_pino_e_erro_semantico_didatico():
    codigo = "dispositivo t {\n ao botao(2) { led.verde(); }\n}"
    try:
        compilar(codigo)
        assert False, "deveria ter lançado ErroSemantico"
    except ErroSemantico as e:
        msg = str(e)
        assert e.linha == 2
        assert "botao 2" in msg and "esp32_wrover" in msg
        assert "botoes com pino: 1" in msg and "esp32_wrover.json" in msg


def test_evento_duplicado_e_erro_semantico():
    codigo = "dispositivo t { ao botao(1) { } ao botao(1) { } }"
    try:
        compilar(codigo)
        assert False
    except ErroSemantico as e:
        assert "já foi declarado" in str(e)


def test_leds_comecam_e_terminam_apagados():
    ino = _ino(EXEMPLO)
    setup = ino[ino.index("void setup()"):ino.index("void loop()")]
    assert "ledApagar();  // LEDs começam apagados" in setup
    assert "ledApagar();  // LEDs apagam ao fim do evento" in ino
    ino2 = _ino("dispositivo t { ao botao(1) { led.verde(); esperar(5); led.apagar(); } }")
    assert "void ledApagar()" in ino2 and "        ledApagar();\n" in ino2


def test_serial_e_logs_em_portugues():
    ino = _ino(EXEMPLO)
    assert "Serial.begin(115200)" in ino
    for msg in ("Botao: PRESSIONADO", "Botao: solto", "Cartao UID: ", "acesso liberado", "acesso negado"):
        assert msg in ino


def test_checagem_do_rc522_no_setup():
    ino = _ino(EXEMPLO)
    assert "MFRC522::VersionReg" in ino
    assert "0x00 || versaoRC522 == 0xFF" in ino
    assert "FALHA: confira SPI, RST e 3.3V" in ino


def test_cabecalho_e_comentarios_ligam_ao_tupa():
    ino = _ino(EXEMPLO, fonte="controle_nfc.tupa")
    assert ino.startswith("// Gerado pelo compilador Tupã a partir de controle_nfc.tupa")
    assert "// [controle_nfc.tupa:4] ao botao(1)" in ino   # linha 4 do EXEMPLO
    assert "// [controle_nfc.tupa:3] int tentativas = 3;" in ino


def test_cli_grava_pasta_homonima(tmp_path):
    fonte = tmp_path / "meu_prog.tupa"
    fonte.write_text(EXEMPLO, encoding="utf-8")
    saida = tmp_path / "meu_prog"
    assert cli_main(["build", str(fonte), "-o", str(saida)]) == 0
    ino = saida / "meu_prog.ino"
    assert ino.is_file()
    assert "a partir de meu_prog.tupa" in ino.read_text(encoding="utf-8")


def test_cli_placa_inexistente_falha(tmp_path):
    fonte = tmp_path / "a.tupa"
    fonte.write_text(EXEMPLO, encoding="utf-8")
    assert cli_main(["build", str(fonte), "-o", str(tmp_path / "a"), "--placa", "nao_existe"]) == 2


def test_ir_so_tem_deteccao_de_obstaculo():
    ino = _ino("dispositivo t { ao botao(1) { se ir.detectado() { led.verde(); } } }")
    assert "#define IR_PIN" in ino and "pinMode(IR_PIN, INPUT)" in ino
    assert "INPUT_PULLUP);" in ino            # só o botão tem pull-up
    try:
        compilar("dispositivo t { ao botao(1) { ir.enviar(1); } }")
        assert False
    except ErroSemantico as e:
        assert "nao existe IR TX" in str(e)


# ---------- runner sem pytest ----------
if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"  ok  {t.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f" FAIL {t.__name__}: {e}")
        except Exception as e:
            falhas += 1
            print(f" ERR  {t.__name__}: {type(e).__name__}: {e}")
    total = len(testes)
    print(f"\n{total - falhas}/{total} testes passaram")
    sys.exit(1 if falhas else 0)
