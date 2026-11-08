"""Monta os carrosseis da Decor da Lulu (layout padrao da Luiza, 08/11).
Uso: python3 montar_decor.py manifesto.json pasta_fotos pasta_saida
Sai: postX-i.jpg (TikTok 768x1376) e igX-i.jpg (Instagram 1080x1350, recorte a partir de 10,5% da altura).
Fonte Patrick Hand; tamanhos em % da largura, posicoes em % da altura.
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PH = os.path.join(HERE, "fonts", "PatrickHand-Regular.ttf")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
PRETO = (17, 17, 17)

def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or o in (0xFE0F, 0x200D)

def split_runs(text):
    runs, cur, emo = [], "", None
    for ch in text:
        e = is_emoji(ch)
        if emo is None or e == emo:
            cur += ch
        else:
            runs.append((cur, emo)); cur = ch
        emo = e
    if cur:
        runs.append((cur, emo))
    return runs

_ecache = {}
def emoji_img(s, px):
    key = (s, px)
    if key not in _ecache:
        f = ImageFont.truetype(EMOJI, 109)
        tmp = Image.new("RGBA", (300 * len(s), 160), (0, 0, 0, 0))
        d = ImageDraw.Draw(tmp)
        d.text((0, 0), s.replace("️", ""), font=f, embedded_color=True)
        bb = tmp.getbbox() or (0, 0, 1, 1)
        im = tmp.crop(bb)
        h = px
        _ecache[key] = im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
    return _ecache[key]

def measure(d, text, f):
    w = 0
    for s, emo in split_runs(text):
        if emo:
            if s.strip("️‍"):
                w += emoji_img(s, int(f.size * 0.9)).width
        else:
            w += d.textlength(s, font=f)
    return w

def draw_text(img, d, x, y, text, f, fill):
    """y = topo da linha (caixa da fonte)."""
    asc, desc = f.getmetrics()
    for s, emo in split_runs(text):
        if emo:
            if not s.strip("️‍"):
                continue
            e = emoji_img(s, int(f.size * 0.9))
            ey = int(y + (asc - e.height) * 0.75)
            img.paste(e, (int(x), ey), e)
            x += e.width
        else:
            d.text((x, y), s, font=f, fill=fill)
            x += d.textlength(s, font=f)

def caixa(img, W, H, topo_pct, texto):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(PH, round(W * 0.047))
    pad = W * 0.026
    tw = measure(d, texto, f)
    bw = tw + 2 * pad
    if bw > W * 0.96:
        raise SystemExit(f"Chamada longa demais para 1 linha: {texto!r}")
    bh = H * 0.076
    x0 = (W - bw) / 2; y0 = H * topo_pct
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=W * 0.016, fill=(255, 255, 255))
    asc, desc = f.getmetrics()
    ty = y0 + (bh - (asc + desc)) / 2
    draw_text(img, d, x0 + pad, ty, texto, f, PRETO)


def quebra(d, texto, f, maxw):
    """1 linha se couber; senao 2 linhas equilibradas."""
    if measure(d, texto, f) <= maxw:
        return [texto]
    w = texto.split()
    best = None
    for i in range(1, len(w)):
        a, b = " ".join(w[:i]), " ".join(w[i:])
        m = max(measure(d, a, f), measure(d, b, f))
        if best is None or m < best[0]:
            best = (m, [a, b])
    return best[1] if best and best[0] <= maxw else None

def ocupacao(img):
    from PIL import ImageFilter, ImageStat
    g = img.convert("L").filter(ImageFilter.FIND_EDGES)
    return g

def capa_auto(img, W, H, texto, ig, topo_fixo=None):
    """Chamada grande e chamativa: caixa branca arredondada, texto preto Patrick Hand,
    ate 2 linhas, colocada na area mais limpa da foto (fora das zonas da interface)."""
    from PIL import ImageStat
    d = ImageDraw.Draw(img)
    pad = W * 0.032
    for pct in (0.065, 0.06, 0.055, 0.05, 0.047):
        f = ImageFont.truetype(PH, round(W * pct))
        linhas = quebra(d, texto, f, W * 0.86 - 2 * pad)
        if linhas:
            break
    asc, desc = f.getmetrics(); lh = (asc + desc) * 1.05
    bw = max(measure(d, l, f) for l in linhas) + 2 * pad
    bh = lh * len(linhas) + 2 * pad * 0.7
    # zonas permitidas: TikTok 14%-64% (fora das abas do topo e da legenda/botoes);
    # Instagram 8%-88%
    lo, hi = (0.08, 0.88) if ig else (0.20, 0.64)
    edges = ocupacao(img)
    x0 = (W - bw) / 2
    if topo_fixo is not None:
        y0 = H * topo_fixo
    else:
        best = None
        y = H * lo
        while y + bh <= H * hi:
            st = ImageStat.Stat(edges.crop((int(x0), int(y), int(x0 + bw), int(y + bh))))
            score = st.mean[0] + 0.5 * st.stddev[0]
            if best is None or score < best[0]:
                best = (score, y)
            y += H * 0.01
        y0 = best[1]
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=W * 0.025, fill=(255, 255, 255))
    ty = y0 + (bh - lh * len(linhas)) / 2
    for l in linhas:
        tw = measure(d, l, f)
        draw_text(img, d, (W - tw) / 2, ty, l, f, PRETO)
        ty += lh
    return y0 / H

def codigo(img, W, H, cod, ig):
    if not cod:
        return
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(PH, round(W * (0.05 if ig else 0.042)))
    tw = d.textlength(cod, font=f)
    x = W - W * 0.042 - tw
    y = H * (0.045 if ig else 0.15)
    d.text((x, y), cod, font=f, fill=PRETO)

def slide_final(img, W, H, linha, ig=False):
    """Bloco compacto: caixas arredondadas centralizadas, no maximo 74% da largura,
    entre ~20% e ~40% da altura no TikTok (longe das abas do topo e da coluna de icones da direita)."""
    d = ImageDraw.Draw(img)
    itens = [("Grupo de ofertas GRATUITO", 0.058, (17, 17, 17), (255, 255, 255)),
             ("com ofertas diárias e cupons de desconto!", 0.038, (255, 255, 255), PRETO),
             (linha, 0.042, (255, 255, 255), PRETO)]
    maxw = W * 0.74; padx = W * 0.035; gap = H * 0.012
    caixas = []
    for txt, pct, bg, fg in itens:
        f = ImageFont.truetype(PH, round(W * pct))
        while measure(d, txt, f) > maxw - 2 * padx and f.size > 12:
            f = ImageFont.truetype(PH, f.size - 1)
        asc, desc = f.getmetrics()
        caixas.append((txt, f, bg, fg, measure(d, txt, f) + 2 * padx, asc + desc + W * 0.03))
    total = sum(c[5] for c in caixas) + gap * (len(caixas) - 1)
    y = H * (0.30 if ig else 0.21)
    for txt, f, bg, fg, bw, bh in caixas:
        x0 = (W - bw) / 2
        d.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=W * 0.02, fill=bg)
        draw_text(img, d, x0 + padx, y + W * 0.015, txt, f, fg)
        y += bh + gap
    return total

def formatos(src):
    tk = src.convert("RGB").resize((768, 1376), Image.LANCZOS)
    top = round(1376 * 0.105); ch = round(768 * 1350 / 1080)
    ig = tk.crop((0, top, 768, top + ch)).resize((1080, 1350), Image.LANCZOS)
    return tk, ig

def fmt(c):
    c = (c or "").replace("-", "").upper()
    return f"{c[:3]}-{c[3:6]}-{c[6:9]}" if len(c) == 9 else c

def main(man, src, out):
    m = json.load(open(man)); os.makedirs(out, exist_ok=True)
    for p in m["posts"]:
        n = p["post"]
        tk_g, ig_g = formatos(Image.open(os.path.join(src, p["geral"])))
        fotos = []
        # capa
        for im, ig in ((tk_g.copy(), False), (ig_g.copy(), True)):
            W, H = im.size
            pos = capa_auto(im, W, H, p["capa"], ig, p.get("capa_topo_ig" if ig else "capa_topo"))
            print(f"post{n} capa {'ig' if ig else 'tiktok'}: topo {pos:.0%}")
            fotos.append((1, ig, im))
        # produtos
        for i, pr in enumerate(p["produtos"], 2):
            tk, ig_im = formatos(Image.open(os.path.join(src, pr["arquivo"])))
            for im, ig in ((tk, False), (ig_im, True)):
                W, H = im.size
                if pr.get("cta2"):
                    caixa(im, W, H, 0.72 if ig else 0.66, pr["cta2"])
                codigo(im, W, H, fmt(pr.get("codigo")), ig)
                fotos.append((i, ig, im))
        # slide final do grupo
        k = len(p["produtos"]) + 2
        for im, ig, linha in ((tk_g.copy(), False, p["final_tiktok"]), (ig_g.copy(), True, p["final_ig"])):
            W, H = im.size
            slide_final(im, W, H, linha, ig)
            fotos.append((k, ig, im))
        for i, ig, im in fotos:
            im.save(os.path.join(out, f"{'ig' if ig else 'post'}{n}-{i}.jpg"), quality=93)

if __name__ == "__main__":
    main(*sys.argv[1:4])
