"""Monta as imagens finais de um dia a partir de um manifesto JSON.

Uso: python3 montar.py manifesto.json pasta_das_fotos pasta_saida

Manifesto: {"data": "2026-10-30", "posts": [{"post": 1, "cta": "...",
  "fotos": [{"arquivo": "p1a_a.jpg", "produto": "58265635180", "codigo": "AATJKRAUZ"}, ...]}]}
A primeira foto de cada post é a capa (recebe a CTA). Todas recebem o código,
quando houver. Para cada foto também sai a versão limpa do pin.
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    man, fotos, saida = sys.argv[1:4]
    m = json.load(open(man))
    os.makedirs(saida, exist_ok=True)
    faltando = []
    for p in m["posts"]:
        for i, f in enumerate(p["fotos"], 1):
            src = os.path.join(fotos, f["arquivo"])
            base = f"post{p['post']}-{i}"
            cmd = ["python3", os.path.join(AQUI, "arte.py"), "capa" if i == 1 else "foto", src,
                   os.path.join(saida, base + ".jpg")]
            if i == 1:
                cmd += ["--cta", p["cta"]]
            if f.get("codigo"):
                cmd += ["--codigo", f["codigo"]]
            else:
                faltando.append(base)
            subprocess.run(cmd, check=True)
            subprocess.run(["python3", os.path.join(AQUI, "arte.py"), "pin", src,
                            os.path.join(saida, base + "-pin.jpg")], check=True)
    print("sem código:", ", ".join(faltando) or "nenhuma")


if __name__ == "__main__":
    main()
