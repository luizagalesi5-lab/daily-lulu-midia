"""Aplica a arte da Daily da Lulu nas fotos do carrossel.

Uso:
  python3 arte.py capa  entrada.jpg saida.jpg --cta "Top vestidos de festa da Shopee 💚" [--codigo ABCDEFGHI]
  python3 arte.py foto  entrada.jpg saida.jpg [--codigo ABCDEFGHI]
  python3 arte.py pin   entrada.jpg saida.jpg          (foto limpa)

Padrão aprovado em 29/10/2026: fonte Patrick Hand, CTA em caixa branca
arredondada com letra preta a ~2/3 da altura, código só com as 9 letras
(XXX-XXX-XXX) em preto no canto superior direito.
"""
import argparse, os, re, shutil
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "PatrickHand-Regular.ttf")
EMOJI_DIR = os.path.join(AQUI, "emoji")  # PNGs Twemoji 64px, nome = codepoints em hex

H_TOPO = 0.15  # código a 15% da altura (fora da área da barra de pesquisa do TikTok)

EMOJI_RE =re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")


def fmt_codigo(c):
    c = re.sub(r"[^A-Za-z]", "", c or "").upper()
    if len(c) != 9:
        raise SystemExit(f"Código precisa ter 9 letras, recebi {len(c)}: {c!r}")
    return f"{c[:3]}-{c[3:6]}-{c[6:]}"


def emoji_png(seq):
    cps = [f"{ord(ch):x}" for ch in seq]
    for nome in ("-".join(cps), "-".join(c for c in cps if c != "fe0f")):
        p = os.path.join(EMOJI_DIR, nome + ".png")
        if os.path.exists(p):
            return Image.open(p).convert("RGBA")
    return None


def desenha_codigo(img, codigo):
    d = ImageDraw.Draw(img)
    W = img.width
    f = ImageFont.truetype(FONTE, round(W * 0.042))
    txt = fmt_codigo(codigo)
    # Abaixo da barra superior do TikTok (lupa/pesquisa fica no topo direito).
    d.text((W - round(W * 0.042), round(H_TOPO * img.height)), txt, font=f, fill=(17, 17, 17), anchor="ra")


def desenha_cta(img, cta):
    W, H = img.size
    f = ImageFont.truetype(FONTE, round(W * 0.047))
    partes = [(m.start(), m.end()) for m in EMOJI_RE.finditer(cta)]
    pedacos, pos = [], 0
    for a, b in partes:
        if a > pos:
            pedacos.append(("t", cta[pos:a]))
        pedacos.append(("e", cta[a:b]))
        pos = b
    if pos < len(cta):
        pedacos.append(("t", cta[pos:]))
    tam_emoji = round(f.size * 1.0)
    larg = 0
    for tipo, s in pedacos:
        larg += f.getlength(s) if tipo == "t" else tam_emoji
    pad_x, alt = round(W * 0.026), round(W * 0.076)
    bx0 = (W - larg) / 2 - pad_x
    by0 = round(H * 0.66)
    caixa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(caixa)
    dc.rounded_rectangle([bx0, by0, bx0 + larg + 2 * pad_x, by0 + alt], radius=round(W * 0.016), fill=(255, 255, 255, 255))
    img.alpha_composite(caixa)
    d = ImageDraw.Draw(img)
    x, ymid = bx0 + pad_x, by0 + alt / 2
    for tipo, s in pedacos:
        if tipo == "t":
            d.text((x, ymid + 2), s, font=f, fill=(17, 17, 17), anchor="lm")
            x += f.getlength(s)
        else:
            png = emoji_png(s)
            if png:
                png = png.resize((tam_emoji, tam_emoji), Image.LANCZOS)
                img.alpha_composite(png, (round(x), round(ymid - tam_emoji / 2)))
            x += tam_emoji


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["capa", "foto", "pin"])
    ap.add_argument("entrada")
    ap.add_argument("saida")
    ap.add_argument("--cta")
    ap.add_argument("--codigo")
    a = ap.parse_args()
    img = Image.open(a.entrada).convert("RGBA")
    if a.modo == "capa":
        if not a.cta:
            raise SystemExit("A capa precisa de --cta")
        desenha_cta(img, a.cta)
    if a.modo in ("capa", "foto") and a.codigo:
        desenha_codigo(img, a.codigo)
    img.convert("RGB").save(a.saida, "JPEG", quality=92)


if __name__ == "__main__":
    main()
