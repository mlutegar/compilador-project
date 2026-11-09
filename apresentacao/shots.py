import sys
from playwright.sync_api import sync_playwright
import pathlib
A = pathlib.Path(__file__).parent
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width":1280,"height":720})
    pg.goto((A/"index.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1500)
    (A/"_shots").mkdir(exist_ok=True)
    for i in range(1,13):
        pg.keyboard.press("Home")
        for _ in range(i-1): pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(150)
        # overflow check: any element extending beyond slide box
        r = pg.evaluate("""()=>{const s=document.querySelector('.slide.on');const b=s.getBoundingClientRect();const bad=[];
          s.querySelectorAll('*').forEach(e=>{const r=e.getBoundingClientRect();if(r.width&&(r.right>b.right+1||r.bottom>b.bottom-30&&!e.closest('.rodape')&&e.tagName!=='path'&&e.tagName!=='text'&&e.tagName!=='g'||e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflow==='hidden'))bad.push(e.tagName+'.'+e.className+' '+Math.round(r.right)+','+Math.round(r.bottom))});return bad.slice(0,5)}""")
        print(i, r)
        pg.screenshot(path=str(A/f"_shots/s{i:02}.png"))
    b.close()
