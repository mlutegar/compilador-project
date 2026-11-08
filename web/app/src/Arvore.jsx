import { useState } from "react";

function No({ no, nivel, abertoInicial }) {
  const [aberto, setAberto] = useState(abertoInicial);
  const tem = no.filhos.length > 0;
  return (
    <li>
      <div className="no-linha" onClick={() => tem && setAberto(!aberto)}>
        <span className="seta">{tem ? (aberto ? "▾" : "▸") : "·"}</span>
        {no.campo ? <span className="campo">{no.campo}: </span> : null}
        <span className="rotulo">{no.rotulo}</span>
        <span className="pos">L{no.linha}:C{no.coluna}</span>
      </div>
      {tem && aberto && (
        <ul>
          {no.filhos.map((f, i) => (
            <No key={i} no={f} nivel={nivel + 1} abertoInicial={abertoInicial} />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function Arvore({ raiz }) {
  // `modo` + `versao` recriam a árvore para aplicar "expandir tudo" / "recolher".
  const [modo, setModo] = useState({ aberto: true, versao: 0 });
  if (!raiz) return <p className="vazio">Sem AST (erro léxico ou sintático).</p>;
  const definir = (aberto) => setModo((m) => ({ aberto, versao: m.versao + 1 }));
  return (
    <div>
      <div className="barra">
        <button onClick={() => definir(true)}>Expandir tudo</button>
        <button onClick={() => definir(false)}>Recolher</button>
      </div>
      <ul className="arvore" key={modo.versao}>
        <No no={raiz} nivel={0} abertoInicial={modo.aberto} />
      </ul>
    </div>
  );
}
