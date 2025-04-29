import csv
import xmlrpc.client
from confImp import url, db, username, password  # Importación de configuración

# 🔧 Mostrar configuración de conexión
print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}")
print()

# Confirmación antes de continuar
confirm = input("¿Deseás continuar con la importación de productos desde el CSV? (s/n): ").strip().lower()
if confirm != 's':
    print("🚫 Operación cancelada por el usuario.")
    exit()

# Establecer conexión
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 🔍 Buscar ID de categoría a partir del nombre
def get_category_id_by_name(category_name):
    try:
        ids = models.execute_kw(db, uid, password, 'product.category', 'search', [[('name', '=', category_name)]], {'limit': 1})
        return ids[0] if ids else None
    except Exception as e:
        print(f"⚠️ Error al buscar categoría '{category_name}': {e}")
        return None

# 🔍 Buscar ID de unidad de medida a partir del nombre
def get_uom_id_by_name(uom_name):
    try:
        ids = models.execute_kw(db, uid, password, 'uom.uom', 'search', [[('name', '=', uom_name)]], {'limit': 1})
        return ids[0] if ids else None
    except Exception as e:
        print(f"⚠️ Error al buscar unidad de medida '{uom_name}': {e}")
        return None

# 📥 Procesar archivo CSV
def process_products_from_csv(csv_file_path):
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Nombre"].strip()
                default_code = row["Referencia interna"].strip()
                list_price = float(row["Precio de venta"])
                cost = float(row["Coste"])
                uom_name = row["Unidad de medida"].strip()
                categ_name = row["Categoría de producto"].strip()

                uom_id = get_uom_id_by_name(uom_name)
                categ_id = get_category_id_by_name(categ_name)

                if not name or not list_price or not uom_id:
                    print(f"⚠️ Producto '{name}' no se pudo importar por datos incompletos.")
                    continue

                product_vals = {
                    'name': name,
                    'default_code': default_code or False,
                    'list_price': list_price,
                    'standard_price': cost,
                    'uom_id': uom_id,
                    'uom_po_id': uom_id,
                    'categ_id': categ_id,
                    'type': 'consu',  # o 'product' o 'service' si lo querés más dinámico
                }

                try:
                    product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_vals])
                    print(f"✅ Producto '{name}' creado con ID {product_id}.")
                except Exception as e:
                    print(f"❌ Error al crear producto '{name}': {e}")
    except Exception as e:
        print(f"❌ Error al procesar el archivo CSV: {e}")

# 🛠️ Ejecutar importación
csv_file_path = 'productos-reducido.csv'
process_products_from_csv(csv_file_path)
