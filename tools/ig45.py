"""Versão 4:5 do Instagram enquadrada (sem laterais desfocadas).

Corta a foto original 9:16 numa janela 4:5 na largura total, mantendo a cabeça
e cortando os pés. Peças longas (vestido longo, calça, macacão) descem a janela
um pouco (corta o alto do cabelo/testa) para mostrar mais da peça.
Depois aplica a arte (CTA na capa e código em todas).

Uso: python3 ig45.py manifesto.json pasta_originais pasta_saida tipos.json
tipos.json: {"post-foto": "curta"|"midi"|"longa"}  ex.: {"2-1": "longa"}
"""
import json, os, subprocess, sys, tempfile
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
TOPO = {"curta": 0.10, "midi": 0.13, "longa": 0.165}  # início da janela (fração da altura)


def main():
    man, orig, saida, tipos = sys.argv[1:5]
    m = json.load(open(man)); t = json.load(open(tipos))
    os.makedirs(saida, exist_ok=True)
    for p in m["posts"]:
        for i, f in enumerate(p["fotos"], 1):
            k = f"{p['post']}-{i}"
            if k not in t:
                continue
            im = Image.open(os.path.join(orig, f["arquivo"])).convert("RGB")
            W, H = im.size
            h = round(W * 5 / 4)
            y0 = min(round(TOPO[t[k]] * H), H - h)
            im = im.crop((0, y0, W, y0 + h)).resize((1080, 1350), Image.LANCZOS)
            tmp = tempfile.mktemp(suffix=".jpg"); im.save(tmp, quality=95)
            cmd = ["python3", os.path.join(AQUI, "arte.py"), "capa" if i == 1 else "foto", tmp,
                   os.path.join(saida, f"igq{k}.jpg"), "--codigo", f["codigo"]]
            if i == 1:
                cmd += ["--cta", p["cta"]]
            subprocess.run(cmd, check=True); os.remove(tmp)


if __name__ == "__main__":
    main()
