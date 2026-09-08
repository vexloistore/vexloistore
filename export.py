import pandas as pd
import json
import re
import html

# 1. Cargar el archivo Excel
df = pd.read_excel('SmartScout.xlsx')

def assign_category(title, brand):
    text = f"{title} {brand}".lower()
    if any(k in text for k in ['wheel', 'tire', 'rim', 'rubber', 'brake dust']):
        return 'wheel-and-tire'
    elif any(k in text for k in ['ceramic', 'graphene', 'sealant', 'coating', 'wax', 'hybrid ceramic']):
        return 'ceramics'
    elif any(k in text for k in ['interior', 'leather', 'dashboard', 'upholstery', 'carpet', 'fabric', 'odor', 'scent', 'seat', 'vinyl']):
        return 'interior'
    elif any(k in text for k in ['spot remover', 'scratch', 'polish', 'compound', 'clay', 'paint', 'glass', 'iron remover', 'detailer', 'decontaminat']):
        return 'paint-and-exterior-care'
    elif any(k in text for k in ['wash', 'soap', 'shampoo', 'foam', 'snow foam', 'cleaner', 'waterless', 'suds', 'bucket']):
        return 'car-wash'
    else:
        return 'paint-and-exterior-care'

products = []
brands_set = set()

for idx, row in df.iterrows():
    img_filename = str(row['Product Image']).strip() if pd.notna(row['Product Image']) else ""
    img_url = f"https://m.media-amazon.com/images/I/{img_filename}" if img_filename else ""
    
    title = str(row['Title']).strip() if pd.notna(row['Title']) else ""
    brand = str(row['Brand']).strip() if pd.notna(row['Brand']) else ""
    
    if brand:
        brands_set.add(brand)
        
    if pd.notna(row['Part Number']) and str(row['Part Number']).strip():
        sku = str(row['Part Number']).strip()
    elif pd.notna(row['Model']) and str(row['Model']).strip():
        sku = str(row['Model']).strip()
    else:
        sku = f"SKU-{idx+1:04d}"
        
    price = float(row['Buy Box Price']) if pd.notna(row['Buy Box Price']) else 0.0
    rating = float(row['Rating']) if pd.notna(row['Rating']) else 0.0
    
    if ":" in title:
        parts = title.split(":", 1)
        name_val = parts[0].strip()
        desc_val = parts[1].strip()
    else:
        name_val = title
        desc_val = title

    product = {
        "id": f"ss-{idx+1:02d}",
        "sku": sku,
        "brand": brand,
        "name": name_val,
        "price": price,
        "category": assign_category(title, brand),
        "rating": rating,
        "image": img_url,
        "desc": desc_val
    }
    products.append(product)

# 2. Generar products.js
raw_json = json.dumps(products, indent=2, ensure_ascii=False)
js_objects = re.sub(r'^\s*"([a-zA-Z_][a-zA-Z0-9_]*)":', r'    \1:', raw_json, flags=re.MULTILINE)
js_content = f"// products.js\nconst productsData = {js_objects};\n"

with open('products.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ Archivo 'products.js' creado correctamente.\n")

# 3. Generar HTML para Marcas (Coincidencia exacta con products.js)
sorted_brands = sorted(list(brands_set))
brand_options = ['            <option value="all">All Brands</option>']
for b in sorted_brands:
    # html.escape asegura que comillas como en Meguiar's no rompan el atributo HTML
    safe_val = html.escape(b, quote=True)
    brand_options.append(f'            <option value="{safe_val}">{b}</option>')

brand_select_html = f"""<!-- Brand Filter -->
<div>
  <label class="block text-xs font-bold uppercase text-gray-600 mb-1">Filter by Brand</label>
  <select id="brand-select" onchange="applyFilters()" class="w-full border border-gray-300 rounded-lg p-2 text-xs font-semibold focus:ring-2 focus:ring-brand-red focus:outline-none">
{chr(10).join(brand_options)}
  </select>
</div>"""

print("================ HTML GENERADO CON VALORES EXACTOS ================\n")
print(brand_select_html)