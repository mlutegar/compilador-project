import { useEffect, useRef } from "react";
import { EditorState, StateEffect, StateField } from "@codemirror/state";
import { EditorView, Decoration, keymap, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { defaultKeymap, history, historyKeymap } from "@codemirror/commands";
import { HighlightStyle, StreamLanguage, syntaxHighlighting } from "@codemirror/language";
import { cpp } from "@codemirror/lang-cpp";
import { tags as t } from "@lezer/highlight";

const LARANJA = "#FF7A1A";
const VERDE = "#2EE6A6";

const estilo = HighlightStyle.define([
  { tag: t.keyword, color: LARANJA, fontWeight: "600" },
  { tag: t.typeName, color: VERDE },
  { tag: t.atom, color: "#c792ea" },
  { tag: t.number, color: "#ffd479" },
  { tag: t.string, color: "#a6e22e" },
  { tag: t.comment, color: "#6b7686", fontStyle: "italic" },
  { tag: t.operator, color: "#9fb3c8" },
  { tag: t.meta, color: "#c792ea" },
  { tag: t.variableName, color: "#e6edf3" },
]);

const tema = EditorView.theme(
  {
    "&": { backgroundColor: "#0E1116", color: "#e6edf3", height: "100%" },
    ".cm-content": { fontFamily: "var(--mono)", caretColor: LARANJA },
    ".cm-gutters": { backgroundColor: "#0E1116", color: "#4b5563", border: "none" },
    ".cm-activeLine": { backgroundColor: "#161b22" },
    ".cm-activeLineGutter": { backgroundColor: "#161b22", color: LARANJA },
    "&.cm-focused .cm-cursor": { borderLeftColor: LARANJA },
    ".cm-selectionBackground, &.cm-focused .cm-selectionBackground": { backgroundColor: "#ff7a1a33" },
    ".cm-scroller": { fontFamily: "var(--mono)", lineHeight: "1.55" },
    ".cm-erro": {
      textDecoration: "underline wavy #ff5c5c",
      textUnderlineOffset: "3px",
      backgroundColor: "#ff5c5c22",
    },
  },
  { dark: true }
);

// Linguagem Tupã: palavras vindas do lexer real (GET /api/linguagem).
function linguagemTupa(palavras) {
  const nomes = Object.keys(palavras);
  const tipos = new Set(nomes.filter((n) => ["inteiro", "decimal", "texto", "booleano"].includes(n)));
  const hw = new Set(nomes.filter((n) => ["nfc", "ir", "led", "botao"].includes(n)));
  const atomos = new Set(["verdadeiro", "falso"]);
  const kw = new Set(nomes.filter((n) => !tipos.has(n) && !hw.has(n) && !atomos.has(n)));
  // Nomes de evento (ao iniciar / ao obstaculo / ao cartao) são palavras contextuais:
  // só ganham destaque logo depois de "ao", para não colorir a variável "cartao".
  const eventos = new Set(["iniciar", "obstaculo", "cartao"]);
  return StreamLanguage.define({
    startState: () => ({ aposAo: false }),
    token(stream, state) {
      if (stream.eatSpace()) return null;
      const aposAo = state.aposAo;
      state.aposAo = false;
      if (stream.peek() === "#") { stream.skipToEnd(); return "comment"; }
      if (stream.match(/^"[^"\n]*"/)) return "string";
      if (stream.match(/^[0-9]+(\.[0-9]+([eE][+-]?[0-9]+)?)?/)) return "number";
      if (stream.match(/^[a-zA-Z][a-zA-Z0-9_]*/)) {
        const w = stream.current();
        if (w === "ao") state.aposAo = true;
        if (aposAo && eventos.has(w)) return "keyword";
        if (kw.has(w)) return "keyword";
        if (tipos.has(w)) return "typeName";
        if (atomos.has(w)) return "atom";
        if (hw.has(w)) return "meta";
        return "variableName";
      }
      if (stream.match(/^(==|!=|>=|<=|&&|\|\||[=<>!+\-*/])/)) return "operator";
      stream.next();
      return null;
    },
  });
}

const definirErro = StateEffect.define();
const campoErro = StateField.define({
  create: () => Decoration.none,
  update(deco, tr) {
    deco = deco.map(tr.changes);
    if (tr.docChanged) deco = Decoration.none;
    for (const e of tr.effects) {
      if (e.is(definirErro)) {
        deco = e.value
          ? Decoration.set([Decoration.mark({ class: "cm-erro" }).range(e.value.from, e.value.to)])
          : Decoration.none;
      }
    }
    return deco;
  },
  provide: (f) => EditorView.decorations.from(f),
});

/** Calcula o trecho a sublinhar a partir de {linha, coluna, trecho}. */
function intervalo(state, erro) {
  if (!erro || !erro.linha || erro.linha > state.doc.lines) return null;
  const ln = state.doc.line(erro.linha);
  let ini = Math.min(Math.max((erro.coluna || 1) - 1, 0), ln.length);
  let fim;
  const trecho = erro.trecho && erro.trecho.trim();
  const i = trecho ? ln.text.indexOf(trecho) : -1;
  if (i >= 0) {
    ini = i;
    fim = i + trecho.length;
  } else {
    const m = /^[A-Za-z0-9_]+|^\S/.exec(ln.text.slice(ini));
    fim = ini + (m ? m[0].length : 1);
  }
  if (fim <= ini) { ini = 0; fim = ln.length; } // linha vazia/fim da linha: sublinha a linha toda
  if (fim <= ini) return { from: ln.from, to: ln.from };
  return { from: ln.from + ini, to: ln.from + fim };
}

/**
 * Editor CodeMirror 6.
 * Props: valor, aoMudar, aoCompilar, palavras (modo "tupa") ou modo="cpp" (somente leitura),
 * foco = {linha, coluna, trecho, n} -> leva o cursor ao erro e sublinha.
 */
export default function Editor({ valor, aoMudar, aoCompilar, palavras, modo = "tupa", foco }) {
  const host = useRef(null);
  const view = useRef(null);
  const cb = useRef({ aoMudar, aoCompilar });
  cb.current = { aoMudar, aoCompilar };

  useEffect(() => {
    const somenteLeitura = modo === "cpp";
    const lang = somenteLeitura ? cpp() : linguagemTupa(palavras || {});
    const extensoes = [
      lineNumbers(), history(), highlightActiveLine(),
      keymap.of([
        { key: "Mod-Enter", run: () => { cb.current.aoCompilar?.(); return true; } },
        ...defaultKeymap, ...historyKeymap,
      ]),
      lang, syntaxHighlighting(estilo), tema, campoErro, EditorView.lineWrapping,
      EditorState.readOnly.of(somenteLeitura), EditorView.editable.of(!somenteLeitura),
      EditorView.updateListener.of((u) => {
        if (u.docChanged) cb.current.aoMudar?.(u.state.doc.toString());
      }),
    ];
    view.current = new EditorView({
      state: EditorState.create({ doc: valor, extensions: extensoes }),
      parent: host.current,
    });
    return () => view.current.destroy();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [modo, palavras]);

  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== valor) {
      v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: valor } });
    }
  }, [valor]);

  useEffect(() => {
    const v = view.current;
    if (!v || !foco) return;
    const r = intervalo(v.state, foco);
    if (!r) return;
    v.dispatch({
      effects: [definirErro.of(r), EditorView.scrollIntoView(r.from, { y: "center" })],
      selection: { anchor: r.from },
    });
    v.focus();
  }, [foco]);

  return <div className="editor" ref={host} />;
}
