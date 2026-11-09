"""TikTok 7:10 (1080x1543): alarga a foto 9:16 com seam carving (modelo protegida) e redesenha a arte.
No app, a área da foto no feed é ~0,70 (largura/altura): 9:16 é cortada (some cabeça/pés) e 3:4 fica com bordas. 7:10 preenche sem borda e sem corte.
Uso: python3 montar_tt34.py pasta_do_dia [saida]  -> ttN-i.jpg
"""
import json, os, subprocess, sys
import numpy as np, cv2
from PIL import Image
T = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, T)
import arte, alarga
dia = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else dia
m = json.load(open(os.path.join(dia, "manifesto.json"))); os.makedirs(out, exist_ok=True)
O = os.path.join(dia, "originais"); C = os.path.join(dia, "originais710"); os.makedirs(C, exist_ok=True)
def base34(nome):
    dst = os.path.join(C, nome)
    if not os.path.exists(dst):
        img = cv2.imread(os.path.join(O, nome)); H, W = img.shape[:2]
        pm = np.zeros((H, W), bool); pm[:, int(W*0.20):int(W*0.80)] = True
        r = alarga.alarga(img, round(H*0.70), pm)
        cv2.imwrite(dst, cv2.resize(r, (1080, 1543), interpolation=cv2.INTER_LANCZOS4), [cv2.IMWRITE_JPEG_QUALITY, 95])
    return dst
for p in m["posts"]:
    for i, f in enumerate(p["fotos"], 1):
        nome = f"tt{p['post']}-{i}.jpg"
        if f.get("slide"):
            subprocess.run(["python3", f"{T}/slide_texto.py", base34(f["fundo"]), os.path.join(out, nome), "--num", f["num"],
                            "--titulo", f["titulo"], "--texto", f["texto"], "--w", "1080", "--h", "1543"], check=True); continue
        im = Image.open(base34(f["arquivo"])).convert("RGBA")
        if i == 1: arte.desenha_cta(im, p["cta"], 0.70)
        if f.get("num"): arte.desenha_num(im, f["num"])
        if f.get("cta2"): arte.desenha_cta(im, f["cta2"], 0.70)
        if f.get("codigo"): arte.desenha_codigo(im, f["codigo"])
        im.convert("RGB").save(os.path.join(out, nome), quality=92)
print("ok")
