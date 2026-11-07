#!/usr/bin/env python3
"""Descarga las imágenes de la antigua web de Wix y las guarda en WebP optimizado dentro de img/.
Lo ejecuta la acción de GitHub «Traer imágenes de Wix».

    pip install pillow && python3 scripts/imagenes.py
"""
import io
import pathlib
import urllib.request

from PIL import Image, ImageOps

RAIZ = pathlib.Path(__file__).resolve().parent.parent
W = "https://static.wixstatic.com/media/0171ea_{}"

ARTISTAS = {
    "anibal-mago": "a69982d6f3274252b34d0047697099c2~mv2.jpg",
    "el-gran-chispita": "37207fa06c4e4e50b0c578bbd40b37e1~mv2.jpg",
    "payaso-kikiriki": "2a7ee1834eed406483557d3111b9d4a6~mv2.jpg",
    "chepedro": "6021c7e03208448bad589114d25eec3e~mv2.jpg",
    "giuseppe-salchichone": "34630d34a3ee48b9938d94139bd5bb19~mv2.jpg",
    "rafaelillo": "0030f15fc44744fdb2a4667ed34b874e~mv2.jpg",
    "miriam-santana": "f469c0f3d1b44e10ad02f4f10d0e3342~mv2.jpg",
    "jessica-guloomal": "5a9ddef9268c4185a743eb371082992d~mv2.jpeg",
}

# destino (sin sufijo), URL, anchos
FOTOS = [("img/artistas/" + k, W.format(v), [400, 800]) for k, v in ARTISTAS.items()] + [
    ("img/payaso", W.format("224076828ed04349be21bc51fb68eebb~mv2.jpg"), [600, 1000]),
]


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "narizmagica-web"})
    with urllib.request.urlopen(req, timeout=90) as r:
        im = Image.open(io.BytesIO(r.read()))
        im.load()
    return ImageOps.exif_transpose(im)


def guardar(im, destino, calidad=80):
    p = RAIZ / destino
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p, "WEBP", quality=calidad, method=6)
    print(f"  {destino}  {im.size[0]}x{im.size[1]}  {p.stat().st_size // 1024} KB")


def main():
    payaso = None
    for destino, url, anchos in FOTOS:
        print(destino)
        try:
            im = bajar(url).convert("RGB")
        except Exception as e:  # una imagen que falle no para las demás
            print("  ERROR", e)
            continue
        if destino == "img/payaso":
            payaso = im
        for w in anchos:
            c = im.copy()
            if c.width > w:
                c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
            guardar(c, f"{destino}-{w}.webp")
    if payaso is not None:
        # Color del papel (esquina superior izquierda) para que el fondo de la portada empaste con la ilustración
        r, g, b = payaso.resize((40, 40)).getpixel((1, 1))
        fondo = RAIZ / "img/payaso-fondo.txt"
        if not fondo.exists():  # si ya existe se respeta (se puede ajustar a mano)
            fondo.write_text(f"#{r:02x}{g:02x}{b:02x}\n")
        print("  fondo", f"#{r:02x}{g:02x}{b:02x}")
        # Imagen para compartir en redes (1200x630) e iconos
        lienzo = Image.new("RGB", (1200, 630), (r, g, b))
        p = payaso.copy()
        p.thumbnail((630, 630), Image.LANCZOS)
        lienzo.paste(p, (1200 - p.width - 40, 0))
        lienzo.save(RAIZ / "img/og-nariz-magica.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        cara = ImageOps.fit(payaso, (512, 512), Image.LANCZOS, centering=(0.5, 0.42))
        for nombre, lado in (("icon-512.png", 512), ("icon-192.png", 192), ("apple-touch-icon.png", 180), ("favicon.png", 48)):
            cara.resize((lado, lado), Image.LANCZOS).save(RAIZ / nombre, "PNG", optimize=True)
        cara.resize((48, 48), Image.LANCZOS).save(RAIZ / "favicon.ico", sizes=[(48, 48), (32, 32), (16, 16)])
        print("  og e iconos")


if __name__ == "__main__":
    main()
