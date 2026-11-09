"""Screenshot headless de cada slide + checagem de estouro e contagem de palavras. Uso: python apresentacao/shots.py"""
import pathlib
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).parent
JS_CHECK = """()=>{
  const s=document.querySelector('.slide.on'), b=s.getBoundingClientRect(), ruim=[];
  const rod=s.querySelector('.rodape'); const topoRod = rod ? rod.getBoundingClientRect().top : b.bottom;
  s.querySelectorAll('*').forEach(e=>{
    if(e.classList.contains('cx')||e.closest('.rodape')||e.closest('template')||e.tagName==='path'||e.tagName==='g'||e.tagName==='defs'||e.tagName==='marker') return;
    const r=e.getBoundingClientRect(); if(!r.width) return;
    if(r.right>b.right-40||r.left<b.left||r.bottom>topoRod-2) ruim.push(e.tagName+'.'+(e.className.baseVal??e.className)+' r='+Math.round(r.right)+' b='+Math.round(r.bottom));
    if(e.scrollWidth>e.clientWidth+2 && ['hidden','auto','scroll'].includes(getComputedStyle(e).overflowX)) ruim.push('scroll '+e.tagName);
  });
  // sobreposição entre filhos diretos de grids/flex: caixas irmãs que se cruzam
  const cx=[...s.querySelectorAll('.painel,.card,.term,img')].map(e=>[e,e.getBoundingClientRect()]);
  for(let i=0;i<cx.length;i++)for(let j=i+1;j<cx.length;j++){
    const [a,ra]=cx[i],[c,rc]=cx[j]; if(a.contains(c)||c.contains(a)) continue;
    if(ra.left<rc.right-1&&rc.left<ra.right-1&&ra.top<rc.bottom-1&&rc.top<ra.bottom-1) ruim.push('sobrepoe '+a.className+' x '+c.className);
  }
  const clone=s.cloneNode(true); clone.querySelectorAll('pre,svg,table,template,.rodape,.num,.term,.painel,.kicker').forEach(x=>x.remove());
  const palavras=(clone.innerText||'').split(/\\s+/).filter(w=>/[A-Za-zÀ-ú0-9]/.test(w)).length;
  return {ruim:ruim.slice(0,6), palavras, ultimo: Math.round(Math.max(...[...s.querySelectorAll('*')].filter(e=>!e.classList.contains('cx')&&!e.closest('.rodape')&&!e.closest('template')&&e.tagName!=='path').map(e=>e.getBoundingClientRect().bottom)))};
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto((A / "index.html").as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1500)
    (A / "_shots").mkdir(exist_ok=True)
    total = pg.evaluate("document.querySelectorAll('.slide').length")
    for i in range(1, total + 1):
        pg.keyboard.press("Home")
        for _ in range(i - 1):
            pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(120)
        r = pg.evaluate(JS_CHECK)
        print(f"{i:02d} palavras={r['palavras']:3d} base={r['ultimo']} {r['ruim']}")
        pg.screenshot(path=str(A / f"_shots/s{i:02}.png"))
    b.close()
