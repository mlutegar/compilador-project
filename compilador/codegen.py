"""Geração de código: AST do Tupã -> C++/Arduino (.ino) para ESP32."""

from . import ast_nodes as A

CTIPO = {"inteiro": "int", "decimal": "float", "texto": "String", "booleano": "bool"}


class GeradorC:
    def __init__(self, programa: A.Programa):
        self.prog = programa
        self.usa_nfc = False
        self.usa_ir = False
        self.declaradas = set()   # variáveis já declaradas no código gerado

    # ---------- entrada ----------
    def gerar(self):
        self._detectar_hardware(self.prog)

        globais = [c for c in self.prog.corpo if isinstance(c, A.DeclVar)]
        eventos = [c for c in self.prog.corpo if isinstance(c, A.Evento)]
        outros = [c for c in self.prog.corpo
                  if not isinstance(c, (A.DeclVar, A.Evento))]

        linhas = []
        linhas += self._preambulo()
        linhas.append("")

        # globais
        for g in globais:
            self.declaradas.add(g.nome)
            linhas.append(self._decl_var(g, indent=0))
        if globais:
            linhas.append("")

        # setup()
        linhas += self._setup(outros)
        linhas.append("")

        # loop()
        linhas += self._loop(eventos)
        return "\n".join(linhas) + "\n"

    # ---------- deteção ----------
    def _detectar_hardware(self, no):
        if isinstance(no, A.Chamada) and isinstance(no.alvo, A.AcessoMembro) \
                and isinstance(no.alvo.objeto, A.Hardware):
            mod = no.alvo.objeto.nome
            if mod == "nfc":
                self.usa_nfc = True
            elif mod == "ir":
                self.usa_ir = True
        for v in getattr(no, "__dict__", {}).values():
            if isinstance(v, A.No):
                self._detectar_hardware(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, A.No):
                        self._detectar_hardware(it)

    # ---------- preâmbulo / helpers ----------
    def _preambulo(self):
        L = [
            f"// controle.ino — gerado automaticamente pelo compilador Tupã",
            f"// Dispositivo: {self.prog.nome}",
            f"// Alvo: ESP32 DevKit v1",
            "",
            "#include <Arduino.h>",
        ]
        if self.usa_nfc:
            L += ["#include <SPI.h>", "#include <MFRC522.h>"]
        L += [
            "",
            "// ---- Pinos ----",
            "#define LED_VERDE     16",
            "#define LED_VERMELHO  17",
            "#define BOTAO_1        4",
        ]
        if self.usa_nfc:
            L += ["#define NFC_SS         5", "#define NFC_RST       22"]
        if self.usa_ir:
            L += ["#define IR_ENVIA      25", "#define IR_RECEBE     26"]
        L.append("")

        if self.usa_nfc:
            L += [
                "MFRC522 leitorNFC(NFC_SS, NFC_RST);",
                "byte UID_AUTORIZADO[4] = { 0xDE, 0xAD, 0xBE, 0xEF };",
                "",
                "struct Cartao {",
                "  bool valido;",
                "};",
                "",
                "Cartao nfcLer() {",
                "  Cartao c; c.valido = false;",
                "  if (!leitorNFC.PICC_IsNewCardPresent() || !leitorNFC.PICC_ReadCardSerial())",
                "    return c;",
                "  bool igual = (leitorNFC.uid.size == 4);",
                "  for (byte i = 0; i < leitorNFC.uid.size && igual; i++)",
                "    if (leitorNFC.uid.uidByte[i] != UID_AUTORIZADO[i]) igual = false;",
                "  c.valido = igual;",
                "  leitorNFC.PICC_HaltA();",
                "  return c;",
                "}",
                "",
            ]
        # LED helpers (sempre)
        L += [
            "void ledVerde()    { digitalWrite(LED_VERDE, HIGH); digitalWrite(LED_VERMELHO, LOW); }",
            "void ledVermelho() { digitalWrite(LED_VERMELHO, HIGH); digitalWrite(LED_VERDE, LOW); }",
            "void ledApagar()   { digitalWrite(LED_VERDE, LOW); digitalWrite(LED_VERMELHO, LOW); }",
        ]
        if self.usa_ir:
            L += [
                "void irEnviar(int codigo) { /* TODO: enviar via biblioteca IR */ }",
                "int  irReceber() { return 0; /* TODO: ler via biblioteca IR */ }",
            ]
        return L

    def _setup(self, outros):
        L = ["void setup() {", "  Serial.begin(115200);"]
        if self.usa_nfc:
            L += ["  SPI.begin();", "  leitorNFC.PCD_Init();"]
        L += [
            "  pinMode(BOTAO_1, INPUT_PULLUP);",
            "  pinMode(LED_VERDE, OUTPUT);",
            "  pinMode(LED_VERMELHO, OUTPUT);",
            "  ledApagar();",
        ]
        for c in outros:
            L.append(self._comando(c, 1))
        L.append("}")
        return L

    def _loop(self, eventos):
        L = ["void loop() {"]
        if not eventos:
            L.append("  // sem eventos definidos")
        for ev in eventos:
            L.append(f"  // evento: ao botao({ev.numero})")
            L.append(f"  if (digitalRead(BOTAO_{ev.numero}) == LOW) {{")
            L.append("    delay(30); // debounce")
            for c in ev.corpo:
                L.append(self._comando(c, 2))
            L.append(f"    while (digitalRead(BOTAO_{ev.numero}) == LOW) delay(10);")
            L.append("  }")
        L.append("}")
        return L

    # ---------- comandos ----------
    def _comando(self, no, indent):
        pad = "  " * indent
        if isinstance(no, A.DeclVar):
            return pad + self._decl_var(no, indent).lstrip()
        if isinstance(no, A.Atribuicao):
            return pad + self._atrib(no)
        if isinstance(no, A.Se):
            return self._se(no, indent)
        if isinstance(no, A.Repetir):
            return self._repetir(no, indent)
        if isinstance(no, A.Esperar):
            return f"{pad}delay({self._expr(no.tempo)});"
        if isinstance(no, A.Retornar):
            return f"{pad}return;" if no.valor is None else f"{pad}return {self._expr(no.valor)};"
        if isinstance(no, A.ExprComando):
            return f"{pad}{self._expr(no.expr)};"
        return f"{pad}// (comando não traduzido: {type(no).__name__})"

    def _decl_var(self, no: A.DeclVar, indent):
        self.declaradas.add(no.nome)
        ctipo = CTIPO[no.tipo]
        if no.valor is None:
            return f"{ctipo} {no.nome};"
        return f"{ctipo} {no.nome} = {self._expr(no.valor)};"

    def _atrib(self, no: A.Atribuicao):
        val = self._expr(no.valor)
        if isinstance(no.alvo, A.Identificador):
            nome = no.alvo.nome
            if nome not in self.declaradas:
                self.declaradas.add(nome)
                ctipo = self._inferir_ctipo(no.valor)
                return f"{ctipo} {nome} = {val};"
            return f"{nome} = {val};"
        return f"{self._expr(no.alvo)} = {val};"

    def _se(self, no: A.Se, indent):
        pad = "  " * indent
        L = [f"{pad}if ({self._expr(no.condicao)}) {{"]
        for c in no.entao:
            L.append(self._comando(c, indent + 1))
        if no.senao is not None:
            L.append(f"{pad}}} else {{")
            for c in no.senao:
                L.append(self._comando(c, indent + 1))
        L.append(f"{pad}}}")
        return "\n".join(L)

    def _repetir(self, no: A.Repetir, indent):
        pad = "  " * indent
        n = self._expr(no.vezes)
        L = [f"{pad}for (int _i = 0; _i < {n}; _i++) {{"]
        for c in no.corpo:
            L.append(self._comando(c, indent + 1))
        L.append(f"{pad}}}")
        return "\n".join(L)

    # ---------- expressões ----------
    def _expr(self, no):
        if isinstance(no, A.Literal):
            if no.tipo == "booleano":
                return "true" if no.valor else "false"
            if no.tipo == "texto":
                return '"' + str(no.valor) + '"'
            return str(no.valor)
        if isinstance(no, A.Identificador):
            return no.nome
        if isinstance(no, A.AcessoMembro):
            return f"{self._expr(no.objeto)}.{no.membro}"
        if isinstance(no, A.Unaria):
            return f"{no.op}{self._expr(no.operando)}"
        if isinstance(no, A.Binaria):
            return f"({self._expr(no.esq)} {no.op} {self._expr(no.dir)})"
        if isinstance(no, A.Chamada):
            return self._chamada(no)
        if isinstance(no, A.Hardware):
            return no.nome  # não deveria acontecer sozinho
        return f"/*expr?{type(no).__name__}*/"

    def _chamada(self, no: A.Chamada):
        alvo = no.alvo
        if isinstance(alvo, A.AcessoMembro) and isinstance(alvo.objeto, A.Hardware):
            mod = alvo.objeto.nome
            met = alvo.membro
            nome_c = mod + met[:1].upper() + met[1:]  # led.verde -> ledVerde
            args = ", ".join(self._expr(a) for a in no.args)
            return f"{nome_c}({args})"
        args = ", ".join(self._expr(a) for a in no.args)
        return f"{self._expr(alvo)}({args})"

    def _inferir_ctipo(self, no):
        if isinstance(no, A.Chamada) and isinstance(no.alvo, A.AcessoMembro) \
                and isinstance(no.alvo.objeto, A.Hardware):
            mod, met = no.alvo.objeto.nome, no.alvo.membro
            if mod == "nfc" and met == "ler":
                return "Cartao"
            if mod == "ir" and met == "receber":
                return "int"
        if isinstance(no, A.Literal):
            return {"int": "int", "float": "float",
                    "texto": "String", "booleano": "bool"}[no.tipo]
        if isinstance(no, A.Binaria):
            if no.op in ("==", "!=", ">", "<", ">=", "<=", "&&", "||"):
                return "bool"
        if isinstance(no, A.Unaria) and no.op == "!":
            return "bool"
        return "auto"


def gerar_ino(programa):
    return GeradorC(programa).gerar()
