import pandas as pd
import json
import re

# 1. Cargar el archivo Excel
df = pd.read_excel('SmartScout.xlsx')

# 2. Función para clasificar y asignar ID a las categorías
def get_category_info(title, brand):
    text = f"{title} {brand}".lower()
    if any(k in text for k in ['wheel', 'tire', 'rim', 'rubber', 'brake dust']):
        return 1, "wheel-and-tire", "Wheel & Tire Care"
    elif any(k in text for k in ['ceramic', 'graphene', 'sealant', 'coating', 'wax', 'hybrid ceramic']):
        return 2, "ceramics", "Waxes & Ceramics"
    elif any(k in text for k in ['interior', 'leather', 'dashboard', 'upholstery', 'carpet', 'fabric', 'odor', 'scent', 'seat', 'vinyl']):
        return 3, "interior", "Interior Care"
    elif any(k in text for k in ['spot remover', 'scratch', 'polish', 'compound', 'clay', 'paint', 'glass', 'iron remover', 'detailer', 'decontaminat']):
        return 4, "paint-and-exterior-care", "Paint & Exterior Care"
    elif any(k in text for k in ['wash', 'soap', 'shampoo', 'foam', 'snow foam', 'cleaner', 'waterless', 'suds', 'bucket']):
        return 5, "car-wash", "Car Wash & Soap"
    elif any(k in text for k in ['oil', 'chemical', 'fluid', 'solvent', 'cleaner', 'lubricant']):
        return 6, "chemicals-and-oils", "Chemicals & Oils"
    else:
        return 4, "paint-and-exterior-care", "Paint & Exterior Care"

# 3. Crear Diccionario Global de Categorías
categories_dict = {
    1: {"slug": "wheel-and-tire", "name": "Wheel & Tire Care"},
    2: {"slug": "ceramics", "name": "Waxes & Ceramics"},
    3: {"slug": "interior", "name": "Interior Care"},
    4: {"slug": "paint-and-exterior-care", "name": "Paint & Exterior Care"},
    5: {"slug": "car-wash", "name": "Car Wash & Soap"},
    6: {"slug": "chemicals-and-oils", "name": "Chemicals & Oils"}
}

# 4. Crear Diccionario de Marcas (ID entero -> Nombre exacto)
unique_brands = sorted(list(df['Brand'].dropna().astype(str).str.strip().unique()))
brands_dict = {i + 1: brand_name for i, brand_name in enumerate(unique_brands)}
brand_name_to_id = {brand_name: i + 1 for i, brand_name in enumerate(unique_brands)}

# 5. Mapear Productos
products = []

for idx, row in df.iterrows():
    img_filename = str(row['Product Image']).strip() if pd.notna(row['Product Image']) else ""
    img_url = f"https://m.media-amazon.com/images/I/{img_filename}" if img_filename else ""
    
    title = str(row['Title']).strip() if pd.notna(row['Title']) else ""
    brand_name = str(row['Brand']).strip() if pd.notna(row['Brand']) else ""
    
    brand_id = brand_name_to_id.get(brand_name, 0)
    cat_id, cat_slug, cat_name = get_category_info(title, brand_name)
    
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
        "brandId": brand_id,         # ID entero para el filtro
        "brand": brand_name,         # Texto legible para mostrar en pantalla
        "categoryId": cat_id,        # ID entero de categoría
        "category": cat_slug,        # Slug/texto legible
        "name": name_val,
        "price": price,
        "rating": rating,
        "image": img_url,
        "desc": desc_val
    }
    products.append(product)

# 6. Escribir productos.js con los diccionarios integrados
raw_products_json = json.dumps(products, indent=2, ensure_ascii=False)
js_products = re.sub(r'^\s*"([a-zA-Z_][a-zA-Z0-9_]*)":', r'    \1:', raw_products_json, flags=re.MULTILINE)

js_content = f"""// products.js
const brandsDict = {json.dumps(brands_dict, indent=2, ensure_ascii=False)};

const categoriesDict = {json.dumps(categories_dict, indent=2, ensure_ascii=False)};

const productsData = {js_products};
"""

with open('products.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ 'products.js' generado exitosamente con IDs de Marca y Categoría.\n")

# 7. Generar HTML para el Select de Marcas basado en los IDs
brand_options = ['            <option value="all">All Brands</option>']
for b_id, b_name in brands_dict.items():
    brand_options.append(f'            <option value="{b_id}">{b_name}</option>')

brand_select_html = f"""<!-- Brand Filter Select -->
<div>
  <label class="block text-xs font-bold uppercase text-gray-600 mb-1">Filter by Brand</label>
  <select id="brand-select" onchange="applyFilters()" class="w-full border border-gray-300 rounded-lg p-2 text-xs font-semibold focus:ring-2 focus:ring-brand-red focus:outline-none">
{chr(10).join(brand_options)}
  </select>
</div>"""

print("================ HTML DEL SELECT DE MARCAS (CON IDs) ================\n")
print(brand_select_html)