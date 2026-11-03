"""Monta TikTok 9:16 (postN-i.jpg), Instagram 4:5 (igrN-i.jpg) e pins (postN-i-pin.jpg).
Aceita slides de texto e uma 2a chamada (cta2) numa foto. Código só se preenchido.
Uso: python3 montar_dia.py pasta_do_dia [saida]
"""
import json, os, subprocess, sys, tempfile
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arte
T = os.path.dirname(os.path.abspath(__file__))
dia = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else dia
m = json.load(open(os.path.join(dia, "manifesto.json"))); os.makedirs(out, exist_ok=True)
O = os.path.join(dia, "originais")

def ig_crop(src, dst):
    im = Image.open(src).convert("RGB"); W, H = im.size; h = round(W * 5 / 4)
    y0 = min(round(0.105 * H), H - h)
    im.crop((0, y0, W, y0 + h)).resize((1080, 1350), Image.LANCZOS).save(dst, quality=95)

for p in m["posts"]:
    for i, f in enumerate(p["fotos"], 1):
        b = f"post{p['post']}-{i}"
        if f.get("slide"):
            for (w, h, nome) in [(768, 1376, b), (1080, 1350, f"igr{p['post']}-{i}")]:
                subprocess.run(["python3", f"{T}/slide_texto.py", os.path.join(O, f["fundo"]), os.path.join(out, nome + ".jpg"),
                                "--num", f["num"], "--titulo", f["titulo"], "--texto", f["texto"], "--w", str(w), "--h", str(h)], check=True)
            continue
        src = os.path.join(O, f["arquivo"])
        if f.get("zoom"):
            # "puxada": recorte do detalhe da peça, número e código em destaque
            cx, cy, cw = f["zoom"]
            for (w, h, nome) in [(1080, 1920, b), (1080, 1350, f"igr{p['post']}-{i}")]:
                im = Image.open(src).convert("RGB"); W, H = im.size
                bw = round(W * cw); bh = round(bw * h / w)
                if bh > H: bh = H; bw = round(bh * w / h)
                x0 = min(max(0, round(W * cx - bw / 2)), W - bw); y0 = min(max(0, round(H * cy - bh / 2)), H - bh)
                im = im.crop((x0, y0, x0 + bw, y0 + bh)).resize((w, h), Image.LANCZOS).convert("RGBA")
                if f.get("num"): arte.desenha_num(im, f["num"])
                if i == 1: arte.desenha_cta(im, p["cta"], 0.66)
                if f.get("codigo"): arte.desenha_codigo_grande(im, f["codigo"], 0.80 if h > 1500 else 0.82)
                im.convert("RGB").save(os.path.join(out, nome + ".jpg"), quality=92)
            continue
        for modo, base, ig in [("tt", src, False), ("ig", None, True)]:
            if ig:
                tmp = tempfile.mktemp(suffix=".jpg"); ig_crop(src, tmp); base = tmp
            im = Image.open(base).convert("RGBA")
            if i == 1: arte.desenha_cta(im, p["cta"], 0.72 if ig else 0.66)
            if f.get("num"): arte.desenha_num(im, f["num"])
            if f.get("cta2"): arte.desenha_cta(im, f["cta2"], 0.72 if ig else 0.66)
            if f.get("codigo"):
                arte.desenha_codigo(im, f["codigo"], 0.045, 0.05) if ig else arte.desenha_codigo(im, f["codigo"])
            nome = f"igr{p['post']}-{i}" if ig else b
            im.convert("RGB").save(os.path.join(out, nome + ".jpg"), quality=92)
        Image.open(src).convert("RGB").save(os.path.join(out, b + "-pin.jpg"), quality=92)
print("ok")
