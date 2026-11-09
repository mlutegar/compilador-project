"""apresentacao.pdf: 1 slide por página (1280x720), via playwright headless. Uso: python apresentacao/pdf.py"""
import pathlib
from playwright.sync_api import sync_playwright

A = pathlib.Path(__file__).parent
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.goto((A / "index.html").as_uri())
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1500)
    pg.emulate_media(media="print")
    pg.pdf(path=str(A / "apresentacao.pdf"), width="1280px", height="720px", print_background=True,
           prefer_css_page_size=True)
    b.close()
print("apresentacao.pdf")
