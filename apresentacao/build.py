"""Gera index.html (autocontido) a partir de fonte.html + imagens. Uso: python build.py"""
import base64, io, pathlib
from PIL import Image

AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent

def b64(img: Image.Image, fmt: str, **kw) -> str:
    buf = io.BytesIO(); img.save(buf, fmt, **kw)
    mime = "image/png" if fmt == "PNG" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(buf.getvalue()).decode()

logo = Image.open(RAIZ / "web/app/public/tupa-icone.png").convert("RGB").resize((600, 600), Image.LANCZOS)
proto = Image.open(RAIZ / "artigo/figuras/prototipo.jpg").convert("RGB")
play = Image.open(AQUI / "assets/playground.png").convert("RGB")
qr = (AQUI / "assets/qr.svg").read_text(encoding="utf-8").replace("<svg ", '<svg style="width:100%;height:100%" ', 1)

html = (AQUI / "fonte.html").read_text(encoding="utf-8")
html = (html.replace("{{LOGO}}", b64(logo, "PNG", optimize=True))
            .replace("{{PROTO}}", b64(proto, "JPEG", quality=88))
            .replace("{{PLAY}}", b64(play, "PNG", optimize=True))
            .replace("{{QR}}", qr))
(AQUI / "index.html").write_text(html, encoding="utf-8")
print("index.html", len(html) // 1024, "KB")
