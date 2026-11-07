#!/usr/bin/env python3
"""Genera las páginas HTML de la web del Festival La Nariz Mágica.

Uso:  python3 scripts/generar.py
Los datos (fechas, artistas, contacto) están arriba de este fichero.
No edites los .html a mano: se sobrescriben.
"""
import html
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from iconos import ICO  # noqa: E402
import json  # noqa: E402


def _datos(nombre, defecto):
    f = RAIZ / "data" / nombre
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else defecto


# Datos editables desde el portal (Gestor de webs → La Nariz Mágica): data/edicion.json, data/programa.json, data/artistas.json
ED = (_datos("edicion.json", []) or [{}])[0]
LUGAR, FECHAS = ED.get("lugar") or "Telde", ED.get("fechas") or "Diciembre 2026"
ENTRADA = ED.get("entrada") or "Entrada gratuita"
TEXTO_EDICION = ED.get("texto") or "Toda la programación se publicará aquí muy pronto."
PROGRAMA = sorted(_datos("programa.json", []), key=lambda f: (f.get("fecha", ""), f.get("hora", "")))

DOMINIO = "https://narizmagica.es"
CORREO = "dislateproducciones@gmail.com"
CORREO_DATOS = "protecciondatos@dislateproducciones.com"

ICO["chispa"] = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8z"/></svg>'
ICO["familia"] = ICO["manos"]

# Artistas: data/artistas.json [{id, nombre, disciplina, texto, imagen, edicion}]
ARTISTAS = [(x.get("imagen") or f"img/artistas/{x['id']}", x["nombre"], x.get("disciplina") or "Clown", x.get("texto", ""))
            for x in _datos("artistas.json", []) if x.get("nombre")]
CIFRAS = [("4", "días de festival"), ("10", "funciones"), ("8", "compañías y artistas canarios"), ("2", "disciplinas: clown y magia")]


def esc(t):
    return html.escape(str(t), quote=True)


def img(ruta, alt, anchos, sizes, carga="lazy", prioridad=False, ancho=None, alto=None):
    srcset = ", ".join(f"/{ruta}-{w}.webp {w}w" for w in anchos)
    dim = f' width="{ancho}" height="{alto}"' if ancho else ""
    return (f'<img src="/{ruta}-{anchos[0]}.webp" srcset="{srcset}" sizes="{sizes}" alt="{esc(alt)}"{dim} loading="{carga}" decoding="async"'
            f'{" fetchpriority=" + chr(34) + "high" + chr(34) if prioridad else ""}>')


def papel():
    f = RAIZ / "img/payaso-fondo.txt"
    return f.read_text().strip() if f.exists() else "#dddbd6"


def cabecera():
    items = [("/#festival", "El festival"), ("/#telde", "Telde 2026"), ("/#artistas", "Artistas"), ("/#contacto", "Contacto")]
    lis = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items)
    return f'''<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="nav">
  <div class="contenedor">
    <a class="marca" href="/" aria-label="Festival La Nariz Mágica, ir al inicio"><span class="nariz" aria-hidden="true"></span><span>La Nariz Mágica</span></a>
    <button class="boton-menu" type="button" aria-controls="menu" aria-expanded="false"><span class="visualmente-oculto">Abrir menú</span>{ICO["menu"]}</button>
    <ul class="menu" id="menu">{lis}</ul>
  </div>
</header>'''


def pie():
    return f'''<footer class="pie">
  <div class="contenedor">
    <div class="pie-arriba">
      <div><p class="pie-titulo"><span class="nariz" aria-hidden="true"></span> La Nariz Mágica</p>
        <p>Festival de clown y magia para toda la familia.<br>Próximamente en {esc(LUGAR)} · {esc(FECHAS)}.</p></div>
      <div class="pie-org"><span>Organiza</span><img src="/img/logos/dislate.webp" alt="Dislate Producciones" width="67" height="80"></div>
    </div>
    <div class="pie-base">
      <span>© <span id="anio">2026</span> Dislate Producciones S.L. · Festival La Nariz Mágica</span>
      <span><a href="/aviso-legal.html">Aviso legal</a> · <a href="/privacidad.html">Privacidad</a> · <a href="/cookies.html">Cookies</a></span>
    </div>
  </div>
</footer>
<script src="/js/main.js" defer></script>'''


def pagina(titulo, descripcion, ruta, cuerpo):
    return f'''<!doctype html>
<html lang="es" class="sin-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descripcion)}">
<link rel="canonical" href="{DOMINIO}{ruta}">
<meta name="theme-color" content="{papel()}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Festival La Nariz Mágica">
<meta property="og:locale" content="es_ES">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descripcion)}">
<meta property="og:url" content="{DOMINIO}{ruta}">
<meta property="og:image" content="{DOMINIO}/img/og-nariz-magica.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/fonts/fredoka-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/css/estilos.css">
<style>:root{{--papel:{papel()}}}</style>
</head>
<body>
{cabecera()}
<main id="contenido">
{cuerpo}
</main>
{pie()}
</body>
</html>
'''


def programa_html():
    """Programa de la edición (data/programa.json), agrupado por día. Vacío = no se muestra."""
    if not PROGRAMA:
        return ""
    import datetime
    dias, html_dias = {}, ""
    for f in PROGRAMA:
        dias.setdefault(f.get("fecha", ""), []).append(f)
    nombres = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    for d, fs in dias.items():
        try:
            dt = datetime.date.fromisoformat(d)
            titulo = f"{nombres[dt.weekday()]} {dt.day} de {meses[dt.month - 1]}".capitalize()
        except ValueError:
            titulo = d
        filas = "".join(f'''<li><time>{esc(f.get("hora", ""))}</time><div><strong>{esc(f.get("artista", ""))}</strong>
          {f'<span>{esc(f["espectaculo"])}</span>' if f.get("espectaculo") else ""}<small>{esc(f.get("lugar", ""))}{" · " + esc(f["nota"]) if f.get("nota") else ""}</small></div></li>''' for f in fs)
        html_dias += f'<div class="prog-dia"><h3>{titulo}</h3><ol>{filas}</ol></div>'
    return f'<div class="programa aparece"><h3 class="programa-titulo">Programa</h3>{html_dias}</div>'


def inicio():
    cifras = "".join(f'<li><strong>{n}</strong><span>{t}</span></li>' for n, t in CIFRAS)
    artistas = "".join(f'''<article class="artista aparece">
        {img(s, n, [400, 800], "(min-width: 1100px) 260px, (min-width: 700px) 45vw, 90vw", ancho=400, alto=400)}
        <div><span class="etiqueta etiqueta-{d.lower()}">{esc(d)}</span><h3>{esc(n)}</h3><p>{esc(t)}</p></div>
      </article>''' for s, n, d, t in ARTISTAS)
    datos = "".join(f'<li>{ICO[i]}<div><strong>{a}</strong><span>{b}</span></div></li>' for i, a, b in [
        ("pin", "Dónde", f"{esc(LUGAR)}, Gran Canaria." + ("" if PROGRAMA else " Los espacios se anunciarán muy pronto.")),
        ("cal", "Cuándo", esc(FECHAS) + "."),
        ("ticket", "Entrada", esc(ENTRADA) + "."),
        ("familia", "Para quién", "Familias, peques y mayores con ganas de reír."),
    ])
    ld = ('{"@context":"https://schema.org","@type":"Festival","name":"Festival La Nariz Mágica",'
          '"description":"Festival de clown y magia para toda la familia.","location":{"@type":"Place","name":"Telde",'
          '"address":{"@type":"PostalAddress","addressLocality":"Telde","addressRegion":"Las Palmas","addressCountry":"ES"}},'
          '"isAccessibleForFree":true,"organizer":{"@type":"Organization","name":"Dislate Producciones","url":"https://dislateproducciones.com"},'
          f'"url":"{DOMINIO}/"}}')
    cuerpo = f'''<section class="portada">
  <div class="contenedor portada-grid">
    <div class="portada-texto">
      <p class="antetitulo">Festival de clown y magia para toda la familia</p>
      <h1>La Nariz <span>Mágica</span></h1>
      <p class="proxima">{ICO["chispa"]}<span>Próximamente en <strong>{esc(LUGAR)}</strong><br><em>{esc(FECHAS)}</em></span></p>
      <p class="entrada">{esc(ENTRADA)}</p>
      <div class="botones">
        <a class="boton boton-rojo" href="#telde">Qué sabemos de 2026 {ICO["flecha"]}</a>
        <a class="boton boton-linea" href="#artistas">Artistas de la 1.ª edición</a>
      </div>
    </div>
    <div class="portada-arte">
      {img("img/payaso", "Ilustración del payaso de La Nariz Mágica: sombrero de bombín, ojos cerrados, nariz roja y pajarita", [600, 1000], "(min-width: 900px) 46vw, 92vw", carga="eager", prioridad=True, ancho=600, alto=600)}
      <span class="destello d1" aria-hidden="true">{ICO["chispa"]}</span><span class="destello d2" aria-hidden="true">{ICO["chispa"]}</span>
    </div>
  </div>
</section>

<div class="cinta" aria-hidden="true"><div><span>Clown</span><i></i><span>Magia</span><i></i><span>Navidad</span><i></i><span>Telde</span><i></i><span>Entrada gratuita</span><i></i><span>Clown</span><i></i><span>Magia</span><i></i><span>Navidad</span><i></i><span>Telde</span><i></i><span>Entrada gratuita</span><i></i></div></div>

<section class="seccion" id="festival">
  <div class="contenedor dos-col">
    <div class="aparece">
      <p class="antetitulo">El festival</p>
      <h2>Una nariz roja basta para cambiarlo todo</h2>
      <p class="entradilla">La Nariz Mágica es un festival navideño de clown y magia pensado para disfrutar en familia, con artistas de Canarias y espectáculos para todas las edades.</p>
      <p>Su primera edición llenó de risas y asombro cuatro días de diciembre. Ahora el festival viaja a <strong>Telde</strong> para la Navidad de 2026, con entrada gratuita y la misma idea: reunir a peques y mayores alrededor de un payaso, un truco imposible y una buena carcajada.</p>
    </div>
    <div class="aparece">
      <p class="cifras-titulo">Así fue la primera edición</p>
      <ul class="cifras">{cifras}</ul>
    </div>
  </div>
</section>

<section class="seccion seccion-azul" id="telde">
  <div class="contenedor">
    <div class="cabecera-seccion aparece">
      <p class="antetitulo">{esc(LUGAR)} · {esc(FECHAS)}</p>
      <h2>La segunda edición llega a {esc(LUGAR)}</h2>
      <p class="entradilla">{esc(TEXTO_EDICION)}</p>
    </div>
    <ul class="datos aparece">{datos}</ul>
    {programa_html()}
  </div>
</section>

<section class="seccion" id="artistas">
  <div class="contenedor">
    <div class="cabecera-seccion aparece">
      <p class="antetitulo">Primera edición</p>
      <h2>Quienes hicieron magia en la primera edición</h2>
      <p class="entradilla">Ocho compañías y artistas canarios de clown y magia protagonizaron la primera edición del festival.</p>
    </div>
    <div class="artistas">{artistas}</div>
  </div>
</section>

<section class="seccion contacto" id="contacto">
  <div class="contenedor contacto-caja aparece">
    <span class="nariz nariz-grande" aria-hidden="true"></span>
    <h2>¿Quieren saber más?</h2>
    <p>Para compañías, colaboraciones, prensa o cualquier duda sobre el festival, escríbannos.</p>
    <a class="boton boton-rojo" href="mailto:{CORREO}">{ICO["mail"]} Escríbannos</a>
    <p class="correo"><a href="mailto:{CORREO}">{CORREO}</a></p>
  </div>
</section>
<script type="application/ld+json">{ld}</script>'''
    return pagina(f"Festival La Nariz Mágica · Clown y magia · Próximamente en {LUGAR}, {FECHAS.lower()}",
                  f"Festival de clown y magia para toda la familia. Próximamente en {LUGAR} (Gran Canaria): {FECHAS.lower()}. {ENTRADA}.",
                  "/", cuerpo)


TITULAR = f'''<table>
<tr><th>Titular</th><td>Dislate Producciones S.L.</td></tr>
<tr><th>NIF</th><td>B22534796</td></tr>
<tr><th>Domicilio</th><td>Hoya de Parrado, 4 · 35017 Las Palmas de Gran Canaria</td></tr>
<tr><th>Correo</th><td><a href="mailto:{CORREO}">{CORREO}</a></td></tr>
</table>'''

AVISO = f'''<h2>1. Datos del titular</h2>
<p>En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI-CE), se informa de que esta web, narizmagica.es, es titularidad de:</p>
{TITULAR}
<h2>2. Objeto</h2>
<p>Esta web informa sobre el Festival La Nariz Mágica: sus ediciones, programación, artistas y forma de contacto.</p>
<h2>3. Propiedad intelectual</h2>
<p>Los textos, la ilustración del festival y el diseño de la web pertenecen a Dislate Producciones S.L. o se usan con permiso de sus autores. Las fotografías de artistas y compañías pertenecen a sus titulares. No se permite reproducirlos sin autorización, salvo para informar del festival citando la fuente.</p>
<h2>4. Responsabilidad</h2>
<p>La información sobre fechas, espacios y programación puede cambiar. La programación que se publique en esta web será la de referencia. Los enlaces a webs de terceros se ofrecen solo como información.</p>
<h2>5. Legislación aplicable</h2>
<p>Este aviso se rige por la legislación española.</p>'''

PRIVACIDAD = f'''<p>Esta web no tiene formularios ni pide datos personales. Solo se tratan datos si nos escriben por correo electrónico.</p>
<h2>Responsable</h2>
{TITULAR}
<p>Contacto para protección de datos: <a href="mailto:{CORREO_DATOS}">{CORREO_DATOS}</a>.</p>
<h2>Qué datos y para qué</h2>
<p>Si nos escriben, usaremos su nombre, su correo y lo que nos cuenten solo para responder y, si es el caso, gestionar la relación que se derive (por ejemplo, la participación de una compañía o una colaboración). La base legal es su consentimiento al escribirnos y, en su caso, la aplicación de medidas precontractuales o de un contrato.</p>
<h2>Cuánto tiempo</h2>
<p>Lo necesario para atender la consulta y, después, durante los plazos legales que correspondan.</p>
<h2>Destinatarios</h2>
<p>No se ceden datos a terceros salvo obligación legal. El proveedor de correo y el de alojamiento web (Cloudflare) pueden acceder a ellos solo para prestar su servicio.</p>
<h2>Sus derechos</h2>
<p>Pueden pedir acceso, rectificación, supresión, oposición, limitación y portabilidad escribiendo a <a href="mailto:{CORREO_DATOS}">{CORREO_DATOS}</a>. Si no están conformes con la respuesta, pueden reclamar ante la Agencia Española de Protección de Datos (aepd.es).</p>'''

COOKIES = '''<p>Esta web no utiliza cookies propias ni de terceros con fines de analítica, publicidad o seguimiento, por lo que no muestra aviso de cookies.</p>
<p>Para medir de forma agregada cuántas personas la visitan se puede usar Cloudflare Web Analytics, que no instala cookies ni identifica a quien visita la web.</p>'''


def legal(slug, titulo, desc, contenido):
    return pagina(f"{titulo} · Festival La Nariz Mágica", desc, f"/{slug}.html",
                  f'<section class="seccion legal"><div class="contenedor estrecho"><h1>{titulo}</h1>{contenido}</div></section>')


def no_encontrada():
    return pagina("Página no encontrada · Festival La Nariz Mágica", "Esta página no existe.", "/404.html",
                  f'''<section class="seccion error"><div class="contenedor estrecho"><span class="nariz nariz-grande" aria-hidden="true"></span>
<h1>¡Puf! Esta página ha desaparecido</h1><p>Algún mago se la ha llevado. Volvamos al principio.</p>
<a class="boton boton-rojo" href="/">Ir al inicio {ICO["flecha"]}</a></div></section>''')


def escribir(ruta, texto):
    p = RAIZ / ruta
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")


def main():
    escribir("index.html", inicio())
    escribir("aviso-legal.html", legal("aviso-legal", "Aviso legal", "Aviso legal de la web del Festival La Nariz Mágica.", AVISO))
    escribir("privacidad.html", legal("privacidad", "Política de privacidad", "Cómo trata Dislate Producciones los datos de quien escribe al festival.", PRIVACIDAD))
    escribir("cookies.html", legal("cookies", "Política de cookies", "Uso de cookies en la web del Festival La Nariz Mágica.", COOKIES))
    escribir("404.html", no_encontrada())
    urls = ["/", "/aviso-legal.html", "/privacidad.html", "/cookies.html"]
    escribir("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             + "\n".join(f"  <url><loc>{DOMINIO}{u}</loc></url>" for u in urls) + "\n</urlset>\n")
    escribir("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    escribir("site.webmanifest", '{"name":"Festival La Nariz Mágica","short_name":"Nariz Mágica","icons":[{"src":"/icon-192.png","sizes":"192x192",'
             f'"type":"image/png"}},{{"src":"/icon-512.png","sizes":"512x512","type":"image/png"}}],"theme_color":"{papel()}","background_color":"{papel()}","display":"browser"}}\n')
    print("Generadas 5 páginas")


if __name__ == "__main__":
    main()
