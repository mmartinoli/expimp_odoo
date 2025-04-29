import csv
import xmlrpc.client
from confImp import url, db, username, password

# Configuración
# 🔧 Mostrar configuración
print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}")
print()

confirm = input("¿Deseás continuar con la importación de productos? (s/n): ").strip().lower()
if confirm != 's':
    print("🚫 Operación cancelada por el usuario.")
    exit()

# Conexión
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Mapear almacenes a ubicaciones internas
warehouse_mapping = {
    'Stock Rotonda': 'Stock Rotonda',
    'Stock Revestimientos Vitoria (Canning)': 'Stock Vitoria',
    'Stock Canning': 'Stock Canning',
    'Stock Ruta': 'Stock Ruta',
}

# Obtener ID de ubicación interna
def get_location_id(name):
    domain = [('name', '=', name), ('usage', '=', 'internal')]
    location_ids = models.execute_kw(db, uid, password,
                                     'stock.location', 'search', [domain], {'limit': 1})
    if location_ids:
        return location_ids[0]
    return None

# Obtener o crear categoría
def get_or_create_category(name):
    cat_id = models.execute_kw(db, uid, password,
                               'product.category', 'search', [[('name', '=', name)]], {'limit': 1})
    if cat_id:
        return cat_id[0]
    return models.execute_kw(db, uid, password, 'product.category', 'create', [{'name': name}])

# Crear o actualizar producto
def create_or_update_product(row):
    external_id = row['ID Externo']
    name = row['Nombre']
    default_code = row['Referencia Interna']
    category = get_or_create_category(row['Categoría'])
    list_price = float(row['Precio de Venta'] or 0)
    standard_price = float(row['Coste'] or 0)

    domain = [('default_code', '=', default_code)]
    product_ids = models.execute_kw(db, uid, password, 'product.product', 'search', [domain], {'limit': 1})

    vals = {
        'name': name,
        'default_code': default_code,
        'categ_id': category,
        'list_price': list_price,
        'standard_price': standard_price,
    }

    if product_ids:
        product_id = product_ids[0]
        models.execute_kw(db, uid, password, 'product.product', 'write', [[product_id], vals])
    else:
        product_id = models.execute_kw(db, uid, password, 'product.product', 'create', [vals])

    # Stock por almacén
    for col, location_name in warehouse_mapping.items():
        stock_qty = float(row[col] or 0)
        if stock_qty > 0:
            location_id = get_location_id(location_name)
            if location_id:
                models.execute_kw(db, uid, password,
                                  'stock.quant', 'create', [{
                        'product_id': product_id,
                        'location_id': location_id,
                        'inventory_quantity': stock_qty,
                    }])

# Leer CSV
with open('productos_con_stock.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        create_or_update_product(row)