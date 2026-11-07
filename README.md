# narizmagica.es

Web del **Festival La Nariz Mágica** (clown y magia para toda la familia). Titular: Dislate Producciones S.L.

Web estática servida como Cloudflare Worker con archivos estáticos (`wrangler.jsonc`). Cada `push` a `main` se publica solo (Workers Builds).

## Cómo se edita

1. Cambia los datos o textos en `scripts/generar.py` (fechas, artistas, correo…).
2. Ejecuta `python3 scripts/generar.py` para regenerar los `.html`. No edites los `.html` a mano.
3. Sube los cambios a `main`.

## Imágenes

Se trajeron de la antigua web de Wix con la acción **Traer imágenes de Wix** (`scripts/imagenes.py`), que las convierte a WebP y crea los iconos y la imagen para redes.

## Otros archivos

- `_headers`: cabeceras de seguridad (CSP) y caché.
- `_redirects`: redirige las direcciones antiguas de Wix.
- `.assetsignore`: lo que no se publica (scripts, README…).
