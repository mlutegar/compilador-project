"""Análise semântica do Tupã.

Verifica:
- variáveis declaradas antes do uso (com atribuição implícita permitida);
- tipos básicos em declarações e condições;
- existência de módulos de hardware e de seus métodos/propriedades;
- número de argumentos das chamadas de hardware.

Erros conhecidos, ex.: `led.roxo()` -> método inexistente, listando os válidos.
"""

from . import ast_nodes as A
from .errors import ErroSemantico
from .placa import carregar_placa

# API de hardware: método -> (n_args, tipo_retorno)
HARDWARE_API = {
    "led": {
        "metodos": {"verde": (0, "vazio"), "vermelho": (0, "vazio"), "apagar": (0, "vazio")},
        "propriedades": {},
    },
    "nfc": {
        "metodos": {"ler": (0, "cartao")},
        "propriedades": {},
    },
    # Sensor IR de OBSTÁCULO (emissor + receptor no mesmo módulo, saída digital).
    # Não existe IR TX nem controle remoto.
    "ir": {
        "metodos": {"detectado": (0, "booleano")},
        "propriedades": {},
    },
    "botao": {
        "metodos": {"pressionado": (0, "booleano")},
        "propriedades": {},
    },
}

# Tipos "objeto" retornados por hardware e suas propriedades.
TIPOS_OBJETO = {
    "cartao": {"valido": "booleano", "uid": "texto"},
}

TIPOS_PRIMITIVOS = {"inteiro", "decimal", "texto", "booleano"}


class AnalisadorSemantico:
    def __init__(self, placa=None):
        self.placa = placa or carregar_placa()
        # pilha de escopos: nome -> tipo
        self.escopos = [{}]
        self.eventos_vistos = {}   # chave do evento -> linha da 1ª declaração

    # ---------- escopo ----------
    def _push(self):
        self.escopos.append({})

    def _pop(self):
        self.escopos.pop()

    def _declarar(self, nome, tipo, no):
        self.escopos[-1][nome] = tipo

    def _tipo_de(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    # ---------- entrada ----------
    def analisar(self, programa: A.Programa):
        for item in programa.corpo:
            self._item(item)
        return programa

    def _item(self, no):
        if isinstance(no, A.Evento):
            self._evento(no)
        else:
            self._comando(no)

    def _evento(self, no: A.Evento):
        rotulo = f"ao botao({no.numero})"
        if no.numero < 1:
            raise ErroSemantico(
                f"número de botão inválido: {no.numero}", no.linha, no.coluna, rotulo
            )
        if no.numero not in self.placa.botoes:
            disp = ", ".join(str(n) for n in sorted(self.placa.botoes)) or "nenhum"
            raise ErroSemantico(
                f"a placa '{self.placa.nome}' não tem pino configurado para o botao {no.numero}\n"
                f"    botoes com pino: {disp}\n"
                f"    para usar o botao {no.numero}, ligue-o a um GPIO e declare em "
                f'"pinos.botoes" de compilador/placas/{self.placa.nome}.json',
                no.linha, no.coluna, rotulo,
            )
        self._registra_evento(no, f"botao({no.numero})", rotulo)
        self._push()
        for c in no.corpo:
            self._comando(c)
        self._pop()

    def _registra_evento(self, no, chave, rotulo):
        if chave in self.eventos_vistos:
            raise ErroSemantico(
                f"o evento '{rotulo}' já foi declarado na linha {self.eventos_vistos[chave]}\n"
                f"    junte os dois blocos em um só",
                no.linha, no.coluna, rotulo,
            )
        self.eventos_vistos[chave] = no.linha

    # ---------- comandos ----------
    def _comando(self, no):
        if isinstance(no, A.DeclVar):
            self._decl(no)
        elif isinstance(no, A.Atribuicao):
            self._atrib(no)
        elif isinstance(no, A.Se):
            self._se(no)
        elif isinstance(no, A.Repetir):
            self._repetir(no)
        elif isinstance(no, A.Esperar):
            t = self._expr(no.tempo)
            self._exige_numerico(t, "esperar", no)
        elif isinstance(no, A.Retornar):
            if no.valor is not None:
                self._expr(no.valor)
        elif isinstance(no, A.ExprComando):
            self._expr(no.expr)
        else:
            raise ErroSemantico(f"comando desconhecido: {type(no).__name__}",
                                getattr(no, "linha", None), getattr(no, "coluna", None))

    def _decl(self, no: A.DeclVar):
        if no.nome in self.escopos[-1]:
            raise ErroSemantico(
                f"variável '{no.nome}' já declarada neste escopo", no.linha, no.coluna
            )
        tipo_decl = {"inteiro": "inteiro", "decimal": "decimal",
                     "texto": "texto", "booleano": "booleano"}[no.tipo]
        if no.valor is not None:
            tval = self._expr(no.valor)
            self._checa_atribuicao(tipo_decl, tval, no)
        self._declarar(no.nome, tipo_decl, no)

    def _atrib(self, no: A.Atribuicao):
        tval = self._expr(no.valor)
        alvo = no.alvo
        if isinstance(alvo, A.Identificador):
            existente = self._tipo_de(alvo.nome)
            if existente is None:
                # atribuição implícita cria a variável (útil p/ cartao = nfc.ler())
                self._declarar(alvo.nome, tval, no)
            else:
                self._checa_atribuicao(existente, tval, no)
        elif isinstance(alvo, A.AcessoMembro):
            self._expr(alvo)  # valida o acesso
        else:
            raise ErroSemantico("alvo de atribuição inválido", no.linha, no.coluna)

    def _se(self, no: A.Se):
        t = self._expr(no.condicao)
        if t not in ("booleano", "desconhecido"):
            raise ErroSemantico(
                f"condição do 'se' deve ser booleana, e não '{t}'",
                no.linha, no.coluna,
            )
        self._push()
        for c in no.entao:
            self._comando(c)
        self._pop()
        if no.senao is not None:
            self._push()
            for c in no.senao:
                self._comando(c)
            self._pop()

    def _repetir(self, no: A.Repetir):
        t = self._expr(no.vezes)
        self._exige_numerico(t, "repetir", no)
        self._push()
        for c in no.corpo:
            self._comando(c)
        self._pop()

    # ---------- expressões: retornam o tipo ----------
    def _expr(self, no):
        if isinstance(no, A.Literal):
            return {"int": "inteiro", "float": "decimal",
                    "texto": "texto", "booleano": "booleano"}[no.tipo]
        if isinstance(no, A.Identificador):
            t = self._tipo_de(no.nome)
            if t is None:
                raise ErroSemantico(
                    f"variável '{no.nome}' usada sem ser declarada",
                    no.linha, no.coluna, no.nome,
                )
            return t
        if isinstance(no, A.Hardware):
            # hardware "solto" (ex.: passar como valor) não é permitido
            raise ErroSemantico(
                f"módulo '{no.nome}' precisa de um método, ex.: {no.nome}.algo()",
                no.linha, no.coluna,
            )
        if isinstance(no, A.Unaria):
            t = self._expr(no.operando)
            if no.op == "!" and t not in ("booleano", "desconhecido"):
                raise ErroSemantico("'!' exige valor booleano", no.linha, no.coluna)
            return "booleano" if no.op == "!" else t
        if isinstance(no, A.Binaria):
            return self._binaria(no)
        if isinstance(no, A.AcessoMembro):
            return self._acesso(no)
        if isinstance(no, A.Chamada):
            return self._chamada(no)
        raise ErroSemantico(f"expressão desconhecida: {type(no).__name__}",
                            getattr(no, "linha", None), getattr(no, "coluna", None))

    def _binaria(self, no: A.Binaria):
        te = self._expr(no.esq)
        td = self._expr(no.dir)
        if no.op in ("==", "!=", ">", "<", ">=", "<="):
            return "booleano"
        if no.op in ("&&", "||"):
            return "booleano"
        # aritméticos
        if "decimal" in (te, td):
            return "decimal"
        if te == "texto" or td == "texto":
            if no.op == "+":
                return "texto"
        return "inteiro"

    def _acesso(self, no: A.AcessoMembro):
        # led.verde  -> validado quando chamado; aqui tratamos propriedade
        base = no.objeto
        if isinstance(base, A.Hardware):
            api = HARDWARE_API[base.nome]
            if no.membro in api["metodos"]:
                return "metodo"      # resolvido na Chamada
            if no.membro in api["propriedades"]:
                return api["propriedades"][no.membro]
            self._erro_membro_hw(base.nome, no.membro, no)
        # objeto do tipo 'cartao' etc.
        tbase = self._expr(base)
        if tbase in TIPOS_OBJETO:
            props = TIPOS_OBJETO[tbase]
            if no.membro in props:
                return props[no.membro]
            disp = ", ".join(sorted(props))
            raise ErroSemantico(
                f"propriedade inexistente no tipo '{tbase}': '{no.membro}'\n"
                f"    disponiveis: {disp}",
                no.linha, no.coluna, f".{no.membro}",
            )
        raise ErroSemantico(
            f"'{no.membro}' não é acessível neste valor", no.linha, no.coluna
        )

    def _chamada(self, no: A.Chamada):
        alvo = no.alvo
        # hardware.metodo(args)
        if isinstance(alvo, A.AcessoMembro) and isinstance(alvo.objeto, A.Hardware):
            modulo = alvo.objeto.nome
            metodo = alvo.membro
            api = HARDWARE_API[modulo]
            if metodo not in api["metodos"]:
                self._erro_membro_hw(modulo, metodo, alvo)
            n_esperado, retorno = api["metodos"][metodo]
            if len(no.args) != n_esperado:
                raise ErroSemantico(
                    f"'{modulo}.{metodo}()' espera {n_esperado} argumento(s), "
                    f"recebeu {len(no.args)}",
                    no.linha, no.coluna,
                )
            for a in no.args:
                self._expr(a)
            return retorno
        # chamada a identificador/função do usuário: valida args, tipo desconhecido
        for a in no.args:
            self._expr(a)
        return "desconhecido"

    # ---------- auxiliares ----------
    def _erro_membro_hw(self, modulo, membro, no):
        disp = ", ".join(f"{m}()" for m in HARDWARE_API[modulo]["metodos"])
        dica = ""
        if modulo == "ir":
            dica = ("\n    o 'ir' e um sensor de obstaculo (emissor e receptor no mesmo modulo): "
                    "nao existe IR TX nem controle remoto")
        raise ErroSemantico(
            f"metodo inexistente no modulo '{modulo}'\n    disponiveis: {disp}{dica}",
            no.linha, no.coluna, f"{modulo}.{membro}()",
        )

    def _exige_numerico(self, tipo, contexto, no):
        if tipo not in ("inteiro", "decimal", "desconhecido"):
            raise ErroSemantico(
                f"'{contexto}' exige um número, e não '{tipo}'", no.linha, no.coluna
            )

    def _checa_atribuicao(self, destino, origem, no):
        if origem == "desconhecido":
            return
        compat = {
            "inteiro": {"inteiro"},
            "decimal": {"inteiro", "decimal"},
            "texto": {"texto"},
            "booleano": {"booleano"},
        }
        if destino in compat and origem not in compat[destino]:
            raise ErroSemantico(
                f"não é possível atribuir '{origem}' a uma variável '{destino}'",
                no.linha, no.coluna,
            )


def analisar(programa, placa=None):
    return AnalisadorSemantico(placa).analisar(programa)
