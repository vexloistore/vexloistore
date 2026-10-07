"""Genera products.js para el sitio Vexloi LLC (tecnología).

Toma las 355 marcas de 'Marcas agrupadas para distribuidores.xlsx' y, de los archivos de
SmartScout en Downloads/productros (grupo1..6 + pulsar), deja SOLO los 10 productos más
vendidos de cada marca (por Est. Monthly Revenue). Solo esos productos van al sitio.

Ejecutar desde esta carpeta:  python build_catalog.py
"""
import json
import re
from pathlib import Path

import pandas as pd

DL = Path.home() / 'Downloads'
OUT = Path(__file__).with_name('products.js')
TOP_N = 10

# Los 20 grupos -> categoría del sitio (en inglés, como el sitio original)
GROUPS = {
    1: ('car-audio-12v', 'Car Audio & 12V', 'car', 'Head units, amplifiers, speakers, subwoofers and 12V power.'),
    2: ('marine-radios', 'Marine Electronics & Radios', 'anchor', 'Fish finders, VHF radios, marine lighting and two-way comms.'),
    3: ('home-audio-hifi', 'Home Audio & Hi-Fi', 'headphones', 'Turntables, DACs, IEMs, headphones and hi-fi components.'),
    4: ('tv-streaming-projectors', 'TV, Streaming & Projectors', 'tv', 'Projectors, screens, antennas, streaming devices and displays.'),
    5: ('pro-av-broadcast', 'Pro AV & Broadcast', 'video', 'Converters, monitors, recorders, PTZ and signal distribution.'),
    6: ('networking-communications', 'Networking & Communications', 'wifi', 'Routers, switches, cellular gateways, VoIP and cabling.'),
    7: ('pc-components-storage', 'PC Components & Storage', 'hard-drive', 'SSDs, NVMe drives, encrypted storage, NAS and PC hardware.'),
    8: ('security-access-control', 'Security & Access Control', 'lock', 'Access control, intercoms, locks, alarms and surveillance.'),
    9: ('photo-video', 'Photo & Video', 'camera', 'Cameras, lenses, light meters, tripods and imaging accessories.'),
    10: ('sport-optics-outdoor', 'Sport Optics & Outdoor', 'binoculars', 'Binoculars, rifle scopes, rangefinders and outdoor optics.'),
    11: ('musical-instruments', 'Musical Instruments', 'guitar', 'Guitars, keyboards, effects pedals, amps and tuners.'),
    12: ('pro-audio-studio-dj', 'Pro Audio, Studio & DJ', 'mic', 'Microphones, interfaces, mixers, DJ gear and studio cables.'),
    13: ('lab-test-measurement', 'Lab, Test & Measurement', 'microscope', 'Oscilloscopes, meters, scales, moisture and medical devices.'),
    14: ('industrial-safety-mro', 'Industrial Safety & MRO', 'hard-hat', 'Safety gear, labeling, lubricants and maintenance supplies.'),
    15: ('tools-construction', 'Tools & Construction', 'hammer', 'Power tools, hand tools, sharpening systems and building supplies.'),
    16: ('hvac-electrical', 'HVAC & Electrical', 'zap', 'HVAC instruments, electrical connectors, testers and controls.'),
    17: ('plumbing-pumps-water', 'Plumbing, Pumps & Water', 'droplets', 'Pumps, metering, water filtration and plumbing systems.'),
    18: ('foodservice-appliances', 'Foodservice & Appliances', 'refrigerator', 'Commercial filtration, refrigeration and kitchen appliances.'),
    19: ('janitorial-facilities', 'Janitorial & Facilities', 'spray-can', 'Hand dryers, washroom accessories and facility equipment.'),
    20: ('office-printing-pos', 'Office, Printing & POS', 'printer', 'Receipt printers, MICR toner, POS hardware and office supplies.'),
}

# Categorías de Amazon que no corresponden a estas marcas (homónimos: velas, CDs, ropa, etc.)
EXCLUDED_CATS = {
    'Health & Household', 'Beauty & Personal Care', 'Grocery & Gourmet Food', 'Books', 'CDs & Vinyl',
    'Movies & TV', 'Clothing, Shoes & Jewelry', 'Toys & Games', 'Pet Supplies', 'Baby Products',
    'Kitchen & Dining', 'Home & Kitchen', 'Arts, Crafts & Sewing', 'Patio, Lawn & Garden', 'Handmade Products',
    'Kindle Store', 'Digital Music', 'Collectibles & Fine Art', 'Everything Else',
}
# Marcas con muchos homónimos: solo se aceptan productos en las categorías de su grupo
STRICT_BRANDS = {'king'}

PRODUCT_COLS = ['Product Image', 'ASIN', 'Title', 'Brand', 'Est. Monthly Revenue', 'Main Category Name',
                'Primary Subcategory Name', 'Buy Box Price', 'Rating', 'Listing Review Count', 'Parent ASIN', 'UPC']


def short_name(title, limit=110):
    title = re.sub(r'\s+', ' ', title).strip()
    if len(title) <= limit:
        return title
    cut = title[:limit].rsplit(' ', 1)[0]
    return cut.rstrip(' ,-|:;') + '…'


def main():
    agr = DL / 'Marcas agrupadas para distribuidores.xlsx'
    resumen = pd.read_excel(agr, sheet_name='Resumen')
    group_num = dict(zip(resumen['Grupo'], resumen['Hoja']))
    group_cats = {row['Hoja']: {c.strip() for c in row['Categorías SmartScout'].split(',')} for _, row in resumen.iterrows()}

    brands = pd.read_excel(agr, sheet_name='Todas las marcas')
    brands['gid'] = brands['Grupo'].map(group_num)
    brands['key'] = brands['Brand Name'].astype(str).str.strip().str.lower()

    homon = pd.read_excel(DL / 'TODAS - Top 3 por Marca.xlsx', sheet_name='Revisión homónimos')
    bad_asins = set(homon.loc[homon['Acción'] == 'Reemplazado', 'ASIN'])

    files = sorted((DL / 'productros').glob('grupo*.xlsx')) + [DL / 'productros' / 'pulsar.xlsx']
    print(f'Leyendo {len(files)} archivos de SmartScout (solo para elegir el top {TOP_N})...')
    df = pd.concat([pd.read_excel(f, usecols=PRODUCT_COLS) for f in files], ignore_index=True)

    df['key'] = df['Brand'].astype(str).str.strip().str.lower()
    df = df[df['key'].isin(set(brands['key']))]
    df = df[df['Buy Box Price'].notna() & df['Product Image'].notna() & df['Title'].notna()]
    df = df[~df['ASIN'].isin(bad_asins) & ~df['Main Category Name'].isin(EXCLUDED_CATS)]
    df = df.sort_values('Est. Monthly Revenue', ascending=False)
    # Una sola variación por producto padre (evita 10 colores del mismo artículo)
    df['parent'] = df['Parent ASIN'].fillna(df['ASIN'])
    df = df.drop_duplicates('ASIN').drop_duplicates(['key', 'parent'])

    brands = brands.sort_values('Brand Name', key=lambda s: s.str.lower()).reset_index(drop=True)
    brands_dict, products, missing, short = {}, [], [], []
    for _, b in brands.iterrows():
        sub = df[df['key'] == b['key']]
        if b['key'] in STRICT_BRANDS:
            sub = sub[sub['Main Category Name'].isin(group_cats[b['gid']])]
        top = sub.head(TOP_N)
        if top.empty:
            missing.append(b['Brand Name'])
            continue
        if len(top) < TOP_N:
            short.append(f"{b['Brand Name']} ({len(top)})")
        bid = len(brands_dict) + 1
        slug, cat_name, _, _ = GROUPS[b['gid']]
        brands_dict[bid] = {'name': str(b['Brand Name']).strip(), 'categoryId': int(b['gid'])}
        for rank, (_, p) in enumerate(top.iterrows(), start=1):
            upc = '' if pd.isna(p['UPC']) else str(p['UPC']).split('.')[0].split(',')[0].strip()
            products.append({
                'id': p['ASIN'],
                'sku': p['ASIN'],
                'upc': upc,
                'brandId': bid,
                'brand': brands_dict[bid]['name'],
                'categoryId': int(b['gid']),
                'category': slug,
                'subcategory': '' if pd.isna(p['Primary Subcategory Name']) else str(p['Primary Subcategory Name']),
                'rank': rank,
                'pop': 0,
                'name': short_name(str(p['Title'])),
                'desc': re.sub(r'\s+', ' ', str(p['Title'])).strip(),
                'price': round(float(p['Buy Box Price']), 2),
                'rating': 0 if pd.isna(p['Rating']) else round(float(p['Rating']), 1),
                'reviews': 0 if pd.isna(p['Listing Review Count']) else int(p['Listing Review Count']),
                'image': f"https://m.media-amazon.com/images/I/{str(p['Product Image']).strip()}",
            })

    # Popularidad global (1 = el más vendido del catálogo), sin exponer cifras de venta
    rev = {a: i for i, a in enumerate(df['ASIN'])}
    for i, p in enumerate(sorted(products, key=lambda x: rev[x['id']]), start=1):
        p['pop'] = i

    categories = {gid: {'slug': s, 'name': n, 'icon': i, 'desc': d} for gid, (s, n, i, d) in GROUPS.items()}
    js = ('// products.js — generado por build_catalog.py (top 10 por marca, fuente SmartScout)\n'
          f'const categoriesDict = {json.dumps(categories, indent=2, ensure_ascii=False)};\n\n'
          f'const brandsDict = {json.dumps(brands_dict, ensure_ascii=False)};\n\n'
          f'const productsData = [\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in products) + '\n];\n')
    OUT.write_text(js, encoding='utf-8')

    print(f'OK: {len(products)} productos de {len(brands_dict)} marcas -> {OUT.name}')
    print(f'Marcas sin productos en los archivos: {missing}')
    print(f'Marcas con menos de {TOP_N} productos válidos ({len(short)}): {", ".join(short)}')


if __name__ == '__main__':
    main()
