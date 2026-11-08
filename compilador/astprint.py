"""Renderiza a AST do Tupã como texto em árvore (para docs e depuração)."""

from . import ast_nodes as A


def render(no, prefixo="", ultimo=True, campo=None, raiz=True):
    linhas = []
    conector = "" if raiz else ("└─ " if ultimo else "├─ ")
    rotulo = _rotulo(no) if isinstance(no, A.No) else repr(no)
    if campo:
        rotulo = f"{campo}: {rotulo}"
    linhas.append(prefixo + conector + rotulo)

    novo_prefixo = prefixo + ("" if raiz else ("   " if ultimo else "│  "))
    filhos = _filhos(no)
    for i, (rot, filho) in enumerate(filhos):
        e_ultimo = i == len(filhos) - 1
        linhas.append(render(filho, novo_prefixo, e_ultimo, rot, raiz=False))
    return "\n".join(linhas)


def _rotulo(no):
    if isinstance(no, A.Programa):
        return f"Programa(dispositivo {no.nome})"
    if isinstance(no, A.DeclVar):
        return f"DeclVar({no.tipo} {no.nome})"
    if isinstance(no, A.Evento):
        return f"Evento(botao {no.numero})"
    if isinstance(no, A.Atribuicao):
        return "Atribuicao(=)"
    if isinstance(no, A.Se):
        return "Se"
    if isinstance(no, A.Repetir):
        return "Repetir"
    if isinstance(no, A.Esperar):
        return "Esperar"
    if isinstance(no, A.Retornar):
        return "Retornar"
    if isinstance(no, A.ExprComando):
        return "Comando"
    if isinstance(no, A.Binaria):
        return f"Binaria({no.op})"
    if isinstance(no, A.Unaria):
        return f"Unaria({no.op})"
    if isinstance(no, A.Literal):
        return f"Literal({no.tipo}={no.valor!r})"
    if isinstance(no, A.Identificador):
        return f"Id({no.nome})"
    if isinstance(no, A.Hardware):
        return f"Hardware({no.nome})"
    if isinstance(no, A.AcessoMembro):
        return f"Membro(.{no.membro})"
    if isinstance(no, A.Chamada):
        return "Chamada()"
    return type(no).__name__


def _filhos(no):
    f = []
    if isinstance(no, A.Programa):
        f = [("", c) for c in no.corpo]
    elif isinstance(no, A.DeclVar):
        if no.valor is not None:
            f = [("valor", no.valor)]
    elif isinstance(no, A.Evento):
        f = [("", c) for c in no.corpo]
    elif isinstance(no, A.Atribuicao):
        f = [("alvo", no.alvo), ("valor", no.valor)]
    elif isinstance(no, A.Se):
        f = [("cond", no.condicao)]
        f += [("entao", c) for c in no.entao]
        if no.senao is not None:
            f += [("senao", c) for c in no.senao]
    elif isinstance(no, A.Repetir):
        f = [("vezes", no.vezes)] + [("corpo", c) for c in no.corpo]
    elif isinstance(no, A.Esperar):
        f = [("tempo", no.tempo)]
    elif isinstance(no, A.Retornar):
        if no.valor is not None:
            f = [("valor", no.valor)]
    elif isinstance(no, A.ExprComando):
        f = [("expr", no.expr)]
    elif isinstance(no, A.Binaria):
        f = [("esq", no.esq), ("dir", no.dir)]
    elif isinstance(no, A.Unaria):
        f = [("op", no.operando)]
    elif isinstance(no, A.AcessoMembro):
        f = [("obj", no.objeto)]
    elif isinstance(no, A.Chamada):
        f = [("alvo", no.alvo)] + [("arg", a) for a in no.args]
    return f


def render_programa(programa):
    return render(programa)
