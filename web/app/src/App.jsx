import { useCallback, useEffect, useState } from "react";
import Editor from "./Editor.jsx";
import Arvore from "./Arvore.jsx";

const ABAS = ["Tokens", "AST", "Erros", "C++", "Métricas"];

async function api(caminho, opcoes) {
  const r = await fetch(caminho, opcoes);
  if (!r.ok) {
    let msg = `HTTP ${r.status}`;
    try { msg = (await r.json()).detail || msg; } catch { /* corpo não-JSON */ }
    throw new Error(msg);
  }
  return r.json();
}

export default function App() {
  const [exemplos, setExemplos] = useState([]);
  const [palavras, setPalavras] = useState(null);
  const [nome, setNome] = useState("");
  const [codigo, setCodigo] = useState("");
  const [res, setRes] = useState(null);
  const [aba, setAba] = useState("Tokens");
  const [carregando, setCarregando] = useState(false);
  const [falha, setFalha] = useState(null);
  const [foco, setFoco] = useState(null);
  const [copiado, setCopiado] = useState(false);

  useEffect(() => {
    Promise.all([api("/api/exemplos"), api("/api/linguagem")])
      .then(([ex, lg]) => {
        setExemplos(ex.exemplos);
        setPalavras(lg.palavras);
        const padrao = ex.exemplos.find((e) => e.nome === ex.padrao) || ex.exemplos[0];
        if (padrao) { setNome(padrao.nome); setCodigo(padrao.codigo); }
      })
      .catch((e) => setFalha(e.message));
  }, []);

  const compilar = useCallback(async () => {
    setCarregando(true);
    setFalha(null);
    try {
      const d = await api("/api/compilar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigo }),
      });
      setRes(d);
      setAba(d.erros.length ? "Erros" : "C++");
      if (d.erros.length) setFoco({ ...d.erros[0], n: Date.now() });
    } catch (e) {
      setFalha(e.message);
    } finally {
      setCarregando(false);
    }
  }, [codigo]);

  const escolher = (n) => {
    const ex = exemplos.find((e) => e.nome === n);
    if (ex) { setNome(n); setCodigo(ex.codigo); setRes(null); setFoco(null); }
  };

  const copiar = async () => {
    await navigator.clipboard.writeText(res.cpp);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 1500);
  };

  const baixar = () => {
    const base = (nome || "programa").replace(/\.[^.]+$/, "");
    const url = URL.createObjectURL(new Blob([res.cpp], { type: "text/plain;charset=utf-8" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: `${base}.ino` });
    a.click();
    URL.revokeObjectURL(url);
  };

  const nErros = res ? res.erros.length : 0;

  return (
    <div className="app">
      <header>
        <img src="/tupa-icone.png" alt="Tupã" className="logo" />
        <div className="titulo">
          <h1>Tupã <span>playground</span></h1>
          <p>Escreva Tupã, veja o C++ do ESP32.</p>
        </div>
        <div className="acoes">
          <select value={nome} onChange={(e) => escolher(e.target.value)} aria-label="Exemplos">
            {exemplos.map((e) => <option key={e.nome} value={e.nome}>{e.nome}</option>)}
          </select>
          <button className="primario" onClick={compilar} disabled={carregando || !palavras} title="Ctrl+Enter">
            {carregando ? "Compilando…" : "▶ Compilar"}
          </button>
        </div>
      </header>

      {falha && <div className="falha" role="alert">Falha: {falha}</div>}

      <main>
        <section className="painel painel-editor">
          <div className="painel-titulo">Tupã <small>Ctrl+Enter compila</small></div>
          {palavras && (
            <Editor valor={codigo} aoMudar={setCodigo} aoCompilar={compilar} palavras={palavras} foco={foco} />
          )}
        </section>

        <section className="painel painel-saida">
          <nav className="abas" role="tablist">
            {ABAS.map((a) => (
              <button key={a} role="tab" aria-selected={aba === a} className={aba === a ? "ativa" : ""} onClick={() => setAba(a)}>
                {a}
                {a === "Erros" && res ? <em className={nErros ? "ruim" : "bom"}>{nErros}</em> : null}
              </button>
            ))}
          </nav>
          <div className="conteudo">
            {!res ? (
              <p className="vazio">Clique em “Compilar” para ver o resultado.</p>
            ) : (
              <>
                {aba === "Tokens" && <Tokens tokens={res.tokens} />}
                {aba === "AST" && <Arvore raiz={res.ast} />}
                {aba === "Erros" && <Erros erros={res.erros} aoClicar={(e) => setFoco({ ...e, n: Date.now() })} />}
                {aba === "C++" && (res.cpp ? (
                  <div className="cpp">
                    <div className="barra">
                      <button onClick={copiar}>{copiado ? "Copiado ✓" : "Copiar"}</button>
                      <button onClick={baixar}>Baixar .ino</button>
                    </div>
                    <Editor modo="cpp" valor={res.cpp} />
                  </div>
                ) : <p className="vazio">Sem C++: corrija os erros primeiro.</p>)}
                {aba === "Métricas" && <Metricas m={res.metricas} />}
              </>
            )}
          </div>
        </section>
      </main>
      <footer>Compilador Tupã · só gera o .ino — compile e grave com a Arduino CLI.</footer>
    </div>
  );
}

function Tokens({ tokens }) {
  if (!tokens.length) return <p className="vazio">Nenhum token (erro léxico).</p>;
  return (
    <div className="tabela-wrap">
      <table>
        <thead><tr><th>#</th><th>Tipo</th><th>Lexema</th><th>Linha</th><th>Coluna</th></tr></thead>
        <tbody>
          {tokens.map((t, i) => (
            <tr key={i}>
              <td>{i + 1}</td>
              <td className="tk">{t.tipo}</td>
              <td><code>{t.lexema === "" ? "∅" : t.lexema}</code></td>
              <td>{t.linha}</td>
              <td>{t.coluna}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Erros({ erros, aoClicar }) {
  if (!erros.length) return <p className="ok">✓ Nenhum erro.</p>;
  return (
    <div>
      {erros.map((e, i) => (
        <button key={i} className="erro" onClick={() => aoClicar(e)} title="Ir para a linha no editor">
          <pre>{e.texto}</pre>
        </button>
      ))}
      <p className="dica">Clique no erro para ir à linha no editor.</p>
    </div>
  );
}

function Metricas({ m }) {
  if (!m) return <p className="vazio">Métricas aparecem quando a compilação tem sucesso.</p>;
  const maior = Math.max(m.cpp_codigo, m.tupa_codigo);
  return (
    <div className="metricas">
      <div className="cartoes">
        <div className="cartao"><b className="laranja">{m.tupa_codigo}</b><span>linhas de código Tupã</span><small>{m.tupa_total} no arquivo</small></div>
        <div className="cartao"><b className="verde">{m.cpp_codigo}</b><span>linhas de código C++</span><small>{m.cpp_total} no .ino</small></div>
        <div className="cartao destaque"><b>{m.razao_codigo}×</b><span>mais código em C++</span><small>{m.razao_total}× contando todas as linhas</small></div>
      </div>
      <div className="barras">
        <div><label>Tupã</label><i style={{ width: `${(m.tupa_codigo / maior) * 100}%`, background: "var(--laranja)" }} /><span>{m.tupa_codigo}</span></div>
        <div><label>C++</label><i style={{ width: `${(m.cpp_codigo / maior) * 100}%`, background: "var(--verde)" }} /><span>{m.cpp_codigo}</span></div>
      </div>
      <p className="dica">Linhas de código = não vazias e sem comentário puro. Valores reais deste programa, medidos na compilação.</p>
    </div>
  );
}
