# Sitio multicategoría de Vexloi LLC

Sitio estático para mostrarles a los distribuidores en qué categorías vendemos y hacia cuál queremos crecer. No modifica `vexloi_tech_ecommerce`: solo lee su `products.js`.

## Dashboard (lo más fácil)
Doble clic en `abrir_dashboard.bat` (o `python dashboard.py`). Se abre en el navegador en http://127.0.0.1:8770/ y solo funciona en tu PC.
- **Marcas**: enciende o apaga marcas y tipos de producto.
- **Categorías**: agrega categorías del catálogo de vexloi.com (por ejemplo Tools & Construction).
- **Perfiles para proveedores**: crea la página para cada tipo de proveedor (aceites, jardín...) y elige cuál sale en la portada.
- **Textos del sitio**: portada, correo, formulario.
- **Guardar y generar sitio** y luego **Vista previa** para revisar. **Publicar** sube a GitHub cuando la carpeta esté conectada.

Para cerrarlo, cierra la ventana negra.

## Cómo cambiar lo que se muestra (a mano)
1. Abre `config.json`.
   - `brands`: pon `true` o `false` en cada marca.
   - `categories`: categorías visibles (`enabled`).
   - `profiles`: perfiles de expansión (por ejemplo `lubricants`). `activeProfile` es el que sale en la portada.
   - `site`: textos de la portada, correo y ubicación.
2. Ejecuta en esta carpeta:  `python build_site.py`
3. Abre `index.html` en el navegador para revisar.

El script regenera `data.js` y una página por perfil en `partners/<perfil>/` (el link que va en los correos, por ejemplo `https://<tu-dominio>/partners/lubricants/`).

Productos propios adicionales: agrégalos en `source/extra_products.json` con el mismo formato de `products.js`.

