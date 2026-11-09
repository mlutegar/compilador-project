"""Geração de código: AST do Tupã -> C++/Arduino (.ino) para ESP32.

Tudo que depende do hardware (pinos, SPI, UIDs autorizados, tempos) vem da placa
(compilador/placas/<nome>.json). Só entram no .ino os módulos que o programa usa.
"""

from contextlib import contextmanager

from . import ast_nodes as A
from .placa import carregar_placa

CTIPO = {"inteiro": "int", "decimal": "float", "texto": "String", "booleano": "bool"}

DEBOUNCE_MS = 50
OPERADORES_BOOL = ("==", "!=", ">", "<", ">=", "<=", "&&", "||")


def _hex(bs):
    return ", ".join(f"0x{b:02X}" for b in bs)


def _cstr(texto):
    """Literal de texto em C++ (escapa barra invertida e aspas)."""
    return '"' + str(texto).replace("\\", "\\\\").replace('"', '\\"') + '"'


class GeradorC:
    def __init__(self, programa: A.Programa, placa=None, fonte=None):
        self.prog = programa
        self.placa = placa or carregar_placa()
        self.fonte = fonte or "programa.tupa"
        self.usa_nfc = False       # qualquer uso de NFC (precisa de SPI + MFRC522)
        self.usa_nfc_ler = False   # nfc.ler() (leitura com espera)
        self.usa_led = False
        self.usa_ir = False
        self.usa_botao_pressionado = False
        self.tem_evento_ir = False  # 'ao obstaculo' (precisa de estado para a borda)
        self.botoes = []           # números dos botões usados em eventos
        self.declaradas = set()    # variáveis já declaradas no escopo C++ atual
        self.ativo_botao = self.placa.eletrica["botao"]["ativo_em"]
        self.ativo_ir = self.placa.eletrica["ir"]["ativo_em"]

    # ---------- escopo de declarações ----------
    @contextmanager
    def _escopo(self):
        salvo = set(self.declaradas)
        try:
            yield
        finally:
            self.declaradas = salvo

    @staticmethod
    def _inativo(ativo):
        return "HIGH" if ativo == "LOW" else "LOW"

    def _ref(self, no):
        return f"// [{self.fonte}:{no.linha}]"

    # ---------- entrada ----------
    def gerar(self):
        self._detectar_hardware(self.prog)

        globais = [c for c in self.prog.corpo if isinstance(c, A.DeclVar)]
        eventos = [c for c in self.prog.corpo
                   if isinstance(c, A.Evento) and c.tipo_evento != "iniciar"]
        # setup(): 'ao iniciar' e comandos soltos do topo, na ordem do fonte
        outros = [c for c in self.prog.corpo if not isinstance(c, (A.DeclVar,))
                  and (not isinstance(c, A.Evento) or c.tipo_evento == "iniciar")]
        for ev in eventos:
            if ev.tipo_evento == "botao" and ev.numero not in self.botoes:
                self.botoes.append(ev.numero)

        L = []
        L += self._cabecalho()
        L += self._definicoes()
        L += self._estado_botoes()

        if globais:
            L.append("// ---- Variáveis do programa ----")
            for g in globais:
                self.declaradas.add(g.nome)
                L.append(f"{self._ref(g)} {self._decl_var(g)}")
            L.append("")

        L += self._auxiliares()
        L += self._setup(outros)
        L.append("")
        L += self._loop(eventos)
        return "\n".join(L) + "\n"

    # ---------- deteção ----------
    def _detectar_hardware(self, no):
        if isinstance(no, A.Evento):
            if no.tipo_evento == "obstaculo":
                self.usa_ir = True
                self.tem_evento_ir = True
            elif no.tipo_evento == "cartao":
                self.usa_nfc = True
        if isinstance(no, A.Chamada) and isinstance(no.alvo, A.AcessoMembro) \
                and isinstance(no.alvo.objeto, A.Hardware):
            mod, met = no.alvo.objeto.nome, no.alvo.membro
            if mod == "nfc":
                self.usa_nfc = True
                if met == "ler":
                    self.usa_nfc_ler = True
            elif mod == "led":
                self.usa_led = True
            elif mod == "ir":
                self.usa_ir = True
            elif mod == "botao" and met == "pressionado":
                self.usa_botao_pressionado = True
        for v in getattr(no, "__dict__", {}).values():
            if isinstance(v, A.No):
                self._detectar_hardware(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, A.No):
                        self._detectar_hardware(it)

    # ---------- blocos fixos ----------
    def _cabecalho(self):
        L = [
            f"// Gerado pelo compilador Tupã a partir de {self.fonte}",
            f"// Dispositivo: {self.prog.nome}",
            f"// Placa: {self.placa.descricao or self.placa.nome} ({self.placa.fqbn})",
            "// Não edite à mão: altere o .tupa e gere de novo.",
            "// Os comentários // [arquivo:linha] ligam cada bloco à linha do .tupa.",
            "",
        ]
        if self.usa_nfc:
            L += ["#include <SPI.h>", f"#include <{self.placa.biblioteca_nfc}.h>", ""]
        return L

    def _definicoes(self):
        pinos = self.placa.pinos
        D = []
        if self.usa_led:
            D += [("LED_VERDE", pinos["led_verde"]), ("LED_VERMELHO", pinos["led_vermelho"])]
        botoes = list(self.botoes)
        if self.usa_botao_pressionado and 1 not in botoes:
            botoes.append(1)
        for n in sorted(botoes):
            D.append((f"BOTAO_{n}", self.placa.botoes[n]))
        if self.usa_nfc:
            D += [("NFC_SS", pinos["nfc_ss"]), ("NFC_RST", pinos["nfc_rst"])]
        if self.usa_ir:
            D.append(("IR_PIN", pinos["ir"]))
        if self.botoes:
            D.append(("DEBOUNCE_MS", DEBOUNCE_MS))
        if self.usa_nfc_ler:
            D.append(("NFC_TIMEOUT_MS", self.placa.timeout_nfc_ms))
        if not D:
            return []
        L = [f"// ---- Pinos e tempos (vêm de compilador/placas/{self.placa.nome}.json) ----"]
        L += [f"#define {nome:<15}{valor}" for nome, valor in D]
        L.append("")
        return L

    def _estado_botoes(self):
        L = []
        if self.botoes:
            ini = self._inativo(self.ativo_botao)
            L.append("// ---- Estado dos botões (debounce por millis, sem delay) ----")
            for n in self.botoes:
                L.append(f"int botao{n}_leitura = {ini}, botao{n}_estavel = {ini};")
                L.append(f"unsigned long botao{n}_mudou = 0;")
            L.append("")
        if self.tem_evento_ir:
            L += ["// ---- Estado do sensor IR (detecta a borda livre -> obstáculo) ----",
                  f"int ir_anterior = {self._inativo(self.ativo_ir)};", ""]
        return L

    def _auxiliares(self):
        L = []
        if self.usa_nfc:
            L += self._nfc_auxiliares()
        if self.usa_led:
            L += [
                "void ledApagar()   { digitalWrite(LED_VERDE, LOW);  digitalWrite(LED_VERMELHO, LOW); }",
                "void ledVerde()    { digitalWrite(LED_VERMELHO, LOW); digitalWrite(LED_VERDE, HIGH); }",
                "void ledVermelho() { digitalWrite(LED_VERDE, LOW);  digitalWrite(LED_VERMELHO, HIGH); }",
                "",
            ]
        if self.usa_ir:
            L += [f"bool irDetectado() {{ return digitalRead(IR_PIN) == {self.ativo_ir}; }}", ""]
        if self.usa_botao_pressionado:
            L += [f"bool botaoPressionado() {{ return digitalRead(BOTAO_1) == {self.ativo_botao}; }}", ""]
        return L

    def _nfc_auxiliares(self):
        uids = self.placa.uids_autorizados
        L = ["MFRC522 leitorNFC(NFC_SS, NFC_RST);", ""]
        L += ["struct Cartao {", "  bool valido = false;", '  String uid = "";', "};", ""]
        L.append("// UIDs autorizados (vêm da placa; os demais cartões ficam negados)")
        if uids:
            L += ["struct UidAutorizado { byte tamanho; byte bytes[10]; };",
                  "const UidAutorizado UIDS_AUTORIZADOS[] = {"]
            for u in uids:
                texto = " ".join(f"{b:02X}" for b in u)
                L.append(f"  {{ {len(u)}, {{ {_hex(u)} }} }},  // {texto}")
            L += ["};",
                  "const int N_UIDS = sizeof(UIDS_AUTORIZADOS) / sizeof(UIDS_AUTORIZADOS[0]);",
                  "",
                  "bool uidAutorizado(byte *uid, byte tamanho) {",
                  "  for (int i = 0; i < N_UIDS; i++) {",
                  "    if (UIDS_AUTORIZADOS[i].tamanho != tamanho) continue;",
                  "    if (memcmp(UIDS_AUTORIZADOS[i].bytes, uid, tamanho) == 0) return true;",
                  "  }",
                  "  return false;",
                  "}"]
        else:
            L += ["bool uidAutorizado(byte *uid, byte tamanho) { return false; }  // lista vazia"]
        L += [
            "",
            "// Uma tentativa de leitura. Sempre encerra a comunicação com o cartão.",
            "bool nfcTentar(Cartao &c) {",
            "  if (!leitorNFC.PICC_IsNewCardPresent() || !leitorNFC.PICC_ReadCardSerial()) return false;",
            '  c.uid = "";',
            "  for (byte i = 0; i < leitorNFC.uid.size; i++) {",
            "    if (i > 0) c.uid += ' ';",
            "    if (leitorNFC.uid.uidByte[i] < 0x10) c.uid += '0';",
            "    c.uid += String(leitorNFC.uid.uidByte[i], HEX);",
            "  }",
            "  c.uid.toUpperCase();",
            "  c.valido = uidAutorizado(leitorNFC.uid.uidByte, leitorNFC.uid.size);",
            "  leitorNFC.PICC_HaltA();",
            "  leitorNFC.PCD_StopCrypto1();",
            "  return true;",
            "}",
            "",
        ]
        if self.usa_nfc_ler:
            seg = self.placa.timeout_nfc_ms // 1000
            L += [
                "// nfc.ler(): espera até NFC_TIMEOUT_MS pelo cartão; sem cartão = inválido.",
                "Cartao nfcLer() {",
                "  Cartao c;",
                "  unsigned long inicio = millis();",
                "  bool lido = false;",
                "  while (!lido && (millis() - inicio) < NFC_TIMEOUT_MS) {",
                "    lido = nfcTentar(c);",
                "    if (!lido) delay(20);",
                "  }",
                "  if (lido) {",
                '    Serial.println("Cartao UID: " + c.uid);',
                "  } else {",
                f'    Serial.println("Cartao: nenhum detectado em {seg} s");',
                "  }",
                '  Serial.println(c.valido ? "acesso liberado" : "acesso negado");',
                "  return c;",
                "}",
                "",
            ]
        return L

    def _setup(self, outros):
        L = ["void setup() {", "  Serial.begin(115200);",
             "  delay(500);  // tempo para o Monitor Serial abrir"]
        for n in sorted(set(self.botoes + ([1] if self.usa_botao_pressionado else []))):
            L.append(f"  pinMode(BOTAO_{n}, {self.placa.eletrica['botao']['modo']});")
        if self.usa_led:
            L += ["  pinMode(LED_VERDE, OUTPUT);", "  pinMode(LED_VERMELHO, OUTPUT);",
                  "  ledApagar();  // LEDs começam apagados"]
        if self.usa_ir:
            L.append(f"  pinMode(IR_PIN, {self.placa.eletrica['ir']['modo']});")
        if self.usa_nfc:
            spi = self.placa.spi
            L += [
                f"  SPI.begin({spi['sck']}, {spi['miso']}, {spi['mosi']}, {spi['ss']});"
                "  // SCK, MISO, MOSI, SS",
                "  leitorNFC.PCD_Init();",
                "  delay(50);",
                "  byte versaoRC522 = leitorNFC.PCD_ReadRegister(MFRC522::VersionReg);",
                '  Serial.printf("RC522 versao: 0x%02X -> %s\\n", versaoRC522,',
                '                (versaoRC522 == 0x00 || versaoRC522 == 0xFF)',
                '                  ? "FALHA: confira SPI, RST e 3.3V" : "OK");',
            ]
        for c in outros:
            if isinstance(c, A.Evento):          # ao iniciar { ... }
                L.append(f"  {self._ref(c)} ao iniciar")
                L += self._corpo_evento(c, 1)
            else:
                L.append(self._comando(c, 1))
        L.append("}")
        return L

    def _loop(self, eventos):
        L = ["void loop() {"]
        if not eventos:
            L.append("  // sem eventos definidos")
        for ev in eventos:
            L += self._evento(ev)
        L += ["  delay(10);", "}"]
        return L

    # ---------- eventos ----------
    def _corpo_evento(self, ev, indent):
        """Corpo do evento em um escopo próprio; LEDs apagam ao fim."""
        L = []
        with self._escopo():
            for c in ev.corpo:
                L.append(self._comando(c, indent))
        if self.usa_led:
            L.append("  " * indent + "ledApagar();  // LEDs apagam ao fim do evento")
        return L

    def _evento(self, ev):
        if ev.tipo_evento == "botao":
            return self._evento_botao(ev)
        if ev.tipo_evento == "obstaculo":
            return self._evento_obstaculo(ev)
        if ev.tipo_evento == "cartao":
            return self._evento_cartao(ev)
        return [f"  // (evento não traduzido: {ev.tipo_evento})"]

    def _evento_obstaculo(self, ev):
        ativo = self.ativo_ir
        L = [
            f"  {self._ref(ev)} ao obstaculo (borda: livre -> obstáculo detectado)",
            "  {",
            "    int leitura = digitalRead(IR_PIN);",
            "    if (leitura != ir_anterior) {",
            "      ir_anterior = leitura;",
            f"      if (leitura == {ativo}) {{",
            '        Serial.println("IR: obstaculo detectado");',
        ]
        L += self._corpo_evento(ev, 4)
        L += ["      } else {", '        Serial.println("IR: livre");', "      }",
              "    }", "  }"]
        return L

    def _evento_cartao(self, ev):
        L = [
            f"  {self._ref(ev)} ao cartao (cartão novo lido; a variável 'cartao' existe no bloco)",
            "  {",
            "    Cartao cartao;",
            "    if (nfcTentar(cartao)) {",
        ]
        with self._escopo():
            self.declaradas.add("cartao")
            L += self._corpo_evento(ev, 3)
        L += ["    }", "  }"]
        return L

    def _evento_botao(self, ev):
        n = ev.numero
        ativo = self.ativo_botao
        nome_log = "Botao" if n == 1 else f"Botao {n}"
        L = [
            f"  {self._ref(ev)} ao botao({n})",
            "  {",
            f"    int leitura = digitalRead(BOTAO_{n});",
            f"    if (leitura != botao{n}_leitura) {{ botao{n}_leitura = leitura; botao{n}_mudou = millis(); }}",
            f"    if ((millis() - botao{n}_mudou) > DEBOUNCE_MS && leitura != botao{n}_estavel) {{",
            f"      botao{n}_estavel = leitura;  // borda confirmada: dispara uma vez por aperto",
            f"      if (botao{n}_estavel == {ativo}) {{",
            f'        Serial.println("{nome_log}: PRESSIONADO");',
        ]
        L += self._corpo_evento(ev, 4)
        L += ["      } else {", f'        Serial.println("{nome_log}: solto");', "      }",
              "    }", "  }"]
        return L

    # ---------- comandos ----------
    def _comando(self, no, indent):
        pad = "  " * indent
        if isinstance(no, A.DeclVar):
            return pad + self._decl_var(no)
        if isinstance(no, A.Atribuicao):
            return pad + self._atrib(no)
        if isinstance(no, A.Se):
            return self._se(no, indent)
        if isinstance(no, A.Repetir):
            return self._repetir(no, indent)
        if isinstance(no, A.Esperar):
            return f"{pad}delay({self._expr(no.tempo)});"
        if isinstance(no, A.Escrever):
            return f"{pad}Serial.println({self._expr(no.valor)});"
        if isinstance(no, A.Retornar):
            return f"{pad}return;" if no.valor is None else f"{pad}return {self._expr(no.valor)};"
        if isinstance(no, A.ExprComando):
            return f"{pad}{self._expr(no.expr)};"
        return f"{pad}// (comando não traduzido: {type(no).__name__})"

    def _decl_var(self, no: A.DeclVar):
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

    def _bloco(self, cmds, indent):
        with self._escopo():
            return [self._comando(c, indent) for c in cmds]

    def _se(self, no: A.Se, indent):
        pad = "  " * indent
        L = [f"{pad}if ({self._expr(no.condicao)}) {{"]
        L += self._bloco(no.entao, indent + 1)
        if no.senao is not None:
            L.append(f"{pad}}} else {{")
            L += self._bloco(no.senao, indent + 1)
        L.append(f"{pad}}}")
        return "\n".join(L)

    def _repetir(self, no: A.Repetir, indent):
        pad = "  " * indent
        n = self._expr(no.vezes)
        L = [f"{pad}for (int _i = 0; _i < {n}; _i++) {{"]
        L += self._bloco(no.corpo, indent + 1)
        L.append(f"{pad}}}")
        return "\n".join(L)

    # ---------- expressões ----------
    def _expr(self, no):
        if isinstance(no, A.Literal):
            if no.tipo == "booleano":
                return "true" if no.valor else "false"
            if no.tipo == "texto":
                return _cstr(no.valor)
            return str(no.valor)
        if isinstance(no, A.Identificador):
            return no.nome
        if isinstance(no, A.AcessoMembro):
            return f"{self._expr(no.objeto)}.{no.membro}"
        if isinstance(no, A.Unaria):
            return f"{no.op}{self._expr(no.operando)}"
        if isinstance(no, A.Binaria):
            return f"({self._operando(no, no.esq)} {no.op} {self._operando(no, no.dir)})"
        if isinstance(no, A.Chamada):
            return self._chamada(no)
        if isinstance(no, A.Hardware):
            return no.nome  # não deveria acontecer sozinho
        return f"/*expr?{type(no).__name__}*/"

    def _operando(self, pai, filho):
        # "a" + "b" não compila em C++ (ponteiro + ponteiro): vira String("a") + "b".
        if pai.op == "+" and isinstance(filho, A.Literal) and filho.tipo == "texto":
            return f"String({_cstr(filho.valor)})"
        return self._expr(filho)

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
            if mod in ("ir", "botao"):
                return "bool"
        if isinstance(no, A.Literal):
            return {"int": "int", "float": "float",
                    "texto": "String", "booleano": "bool"}[no.tipo]
        if isinstance(no, A.Binaria) and no.op in OPERADORES_BOOL:
            return "bool"
        if isinstance(no, A.Unaria) and no.op == "!":
            return "bool"
        return "auto"


def gerar_ino(programa, placa=None, fonte=None):
    return GeradorC(programa, placa, fonte).gerar()
