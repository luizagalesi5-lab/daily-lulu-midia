"""Slide de texto do formato "Antes de comprar, confere isso" (Daily da Lulu).

Fundo: foto da modelo desfocada e clareada; cartão branco arredondado no centro
com número grande, título e texto (fonte Patrick Hand).
Uso: python3 slide_texto.py fundo.jpg saida.jpg --num 1 --titulo "..." --texto "..." [--w 768 --h 1376]
"""
import argparse, os, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "PatrickHand-Regular.ttf")

def wrap(d, txt, f, maxw):
    linhas = []
    for par in txt.split("\n"):
        pal, cur = par.split(), ""
        for p in pal:
            t = (cur + " " + p).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: linhas.append(cur); cur = p
        linhas.append(cur)
    return linhas

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fundo"); ap.add_argument("saida")
    ap.add_argument("--num"); ap.add_argument("--titulo"); ap.add_argument("--texto")
    ap.add_argument("--w", type=int, default=768); ap.add_argument("--h", type=int, default=1376)
    a = ap.parse_args()
    W, H = a.w, a.h
    im = Image.open(a.fundo).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0, y0 = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(W * 0.03))
    im = ImageEnhance.Brightness(im).enhance(1.08).convert("RGBA")
    d = ImageDraw.Draw(im)
    fn = ImageFont.truetype(FONTE, round(W * 0.16))
    ft = ImageFont.truetype(FONTE, round(W * 0.075))
    fx = ImageFont.truetype(FONTE, round(W * 0.056))
    pad = round(W * 0.07); cw = W - 2 * round(W * 0.08); maxw = cw - 2 * pad
    lt = wrap(d, a.titulo, ft, maxw); lx = wrap(d, a.texto, fx, maxw)
    hn = round(W * 0.17); ht = len(lt) * round(ft.size * 1.15); hx = len(lx) * round(fx.size * 1.3)
    ch = pad + hn + ht + round(W * 0.04) + hx + pad
    cx0 = (W - cw) // 2; cy0 = (H - ch) // 2
    card = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle([cx0, cy0, cx0 + cw, cy0 + ch], radius=round(W * 0.04), fill=(255, 255, 255, 240))
    im.alpha_composite(card); d = ImageDraw.Draw(im)
    y = cy0 + pad
    d.text((W / 2, y), a.num, font=fn, fill=(214, 96, 132), anchor="ma"); y += hn
    for l in lt:
        d.text((W / 2, y), l, font=ft, fill=(17, 17, 17), anchor="ma"); y += round(ft.size * 1.15)
    y += round(W * 0.04)
    for l in lx:
        d.text((W / 2, y), l, font=fx, fill=(60, 60, 60), anchor="ma"); y += round(fx.size * 1.3)
    im.convert("RGB").save(a.saida, "JPEG", quality=92)

if __name__ == "__main__":
    main()
