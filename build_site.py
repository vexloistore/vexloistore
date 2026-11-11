"""Genera data.js y las páginas de perfil del sitio multicategoría de Vexloi LLC.

Lee config.json (qué categorías, marcas y perfiles se muestran) y las fuentes de
productos (por defecto el products.js del sitio vexloi_tech_ecommerce, sin modificarlo).

Ejecutar desde esta carpeta:   python build_site.py
Solo usa la librería estándar de Python.
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG = HERE / 'config.json'
OUT = HERE / 'data.js'


def load_js_catalog(path):
    """Lee un products.js (categoriesDict, brandsDict, productsData) y devuelve productos con el slug de su categoría."""
    text = path.read_text(encoding='utf-8')
    cats = json.loads(re.search(r'const categoriesDict = (\{.*?\n\});', text, re.S).group(1))
    prods = json.loads(re.search(r'const productsData = (\[.*\]);', text, re.S).group(1))
    for p in prods:
        p.setdefault('category', cats.get(str(p.get('categoryId')), {}).get('slug', ''))
    return prods


def load_source(path):
    if not path.exists():
        print(f'  (aviso) no existe la fuente {path}')
        return []
    if path.suffix == '.js':
        return load_js_catalog(path)
    return json.loads(path.read_text(encoding='utf-8'))


def load_products(cfg, log=print):
    products = []
    for src in cfg['sources']:
        found = load_source((HERE / src).resolve())
        log(f'Fuente {src}: {len(found)} productos')
        products.extend(found)
    return products


def source_inventory(cfg):
    """Para el dashboard: por categoría de origen, nombre, marcas y subcategorías con su conteo."""
    inv = {}
    for p in load_products(cfg, log=lambda *_: None):
        c = inv.setdefault(p.get('category', ''), {'brands': {}, 'subcategories': {}})
        c['brands'][p['brand']] = c['brands'].get(p['brand'], 0) + 1
        sub = p.get('subcategory', '')
        c['subcategories'][sub] = c['subcategories'].get(sub, 0) + 1
    return inv


def source_category_names(cfg):
    names = {}
    for src in cfg['sources']:
        path = (HERE / src).resolve()
        if path.suffix == '.js' and path.exists():
            text = path.read_text(encoding='utf-8')
            for c in json.loads(re.search(r'const categoriesDict = (\{.*?\n\});', text, re.S).group(1)).values():
                names[c['slug']] = {'name': c['name'], 'icon': c.get('icon', 'tag'), 'desc': c.get('desc', '')}
    return names


def build(log=print):
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    products = load_products(cfg, log)

    excluded_subs = set(cfg.get('excludeSubcategories', []))
    brand_flags = cfg.setdefault('brands', {})
    max_per_brand = int(cfg.get('maxPerBrand', 10))
    cats = [c for c in cfg['categories'] if c.get('enabled', True)]

    categories, brands, out, new_brands = {}, {}, [], []
    seen = set()
    for cid, c in enumerate(cats, start=1):
        categories[cid] = {k: c[k] for k in ('slug', 'name', 'icon', 'desc')}
        src_slugs = c.get('fromSourceCategory', c['slug'])
        src_slugs = {src_slugs} if isinstance(src_slugs, str) else set(src_slugs)
        pool = [p for p in products if p.get('category') in src_slugs and p.get('subcategory', '') not in excluded_subs]

        # Las marcas nuevas se agregan al config apagadas, para encenderlas desde el dashboard
        for name in sorted({p['brand'] for p in pool}, key=str.lower):
            if name not in brand_flags:
                brand_flags[name] = False
                new_brands.append(name)

        per_brand = {}
        for p in sorted(pool, key=lambda x: (x['brand'].lower(), x.get('rank', 99))):
            if not brand_flags.get(p['brand']) or p['id'] in seen:
                continue
            if per_brand.get(p['brand'], 0) >= max_per_brand:
                continue
            per_brand[p['brand']] = per_brand.get(p['brand'], 0) + 1
            key = (p['brand'], cid)
            if key not in brands:
                brands[key] = len(brands) + 1
            seen.add(p['id'])
            item = dict(p, categoryId=cid, category=c['slug'], brandId=brands[key], rank=per_brand[p['brand']])
            out.append(item)

    # Orden de popularidad dentro del sitio (1 = más popular en la fuente)
    for i, p in enumerate(sorted(out, key=lambda x: x.get('pop', 10**9)), start=1):
        p['pop'] = i

    brands_dict = {bid: {'name': name, 'categoryId': cid} for (name, cid), bid in brands.items()}
    profiles = [p for p in cfg.get('profiles', []) if p.get('enabled', True)]
    active = cfg.get('activeProfile') if any(p['slug'] == cfg.get('activeProfile') for p in profiles) else None

    js = ('// data.js — generado por build_site.py a partir de config.json. No editar a mano.\n'
          f'const siteConfig = {json.dumps(cfg["site"], ensure_ascii=False, indent=2)};\n\n'
          f'const categoriesDict = {json.dumps(categories, ensure_ascii=False, indent=2)};\n\n'
          f'const brandsDict = {json.dumps(brands_dict, ensure_ascii=False)};\n\n'
          f'const profilesData = {json.dumps(profiles, ensure_ascii=False, indent=2)};\n\n'
          f'const activeProfileSlug = {json.dumps(active)};\n\n'
          'const productsData = [\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in out) + '\n];\n')
    OUT.write_text(js, encoding='utf-8')

    # Una página por perfil: partners/<slug>/index.html (link para pegar en correos)
    template = (HERE / 'partners.html').read_text(encoding='utf-8')
    pdir = HERE / 'partners'
    if pdir.exists():
        shutil.rmtree(pdir)
    for p in profiles:
        d = pdir / p['slug']
        d.mkdir(parents=True, exist_ok=True)
        page = template.replace('<head>', '<head>\n  <base href="../../">', 1).replace('data-profile=""', f'data-profile="{p["slug"]}"', 1)
        (d / 'index.html').write_text(page, encoding='utf-8')

    if new_brands:
        CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        log(f'Marcas nuevas agregadas a config.json (apagadas): {", ".join(new_brands)}')

    log(f'OK: {len(out)} productos, {len(brands_dict)} marcas, {len(categories)} categorías, '
          f'{len(profiles)} perfiles -> data.js')
    for p in profiles:
        log(f'  Perfil: partners/{p["slug"]}/')
    return len(out)


if __name__ == '__main__':
    build()
