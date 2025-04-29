import csv
import xmlrpc.client
from confImp import url, db, username, password

# 🔧 Mostrar configuración
print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}")
print()

# ✅ Confirmación
confirm = input("¿Deseás continuar con la importación de categorías? (s/n): ").strip().lower()
if confirm != 's':
    print("🚫 Operación cancelada por el usuario.")
    exit()

# 🔌 Conexión a Odoo
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
if not uid:
    print("❌ Error de autenticación.")
    exit()

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
print(f"🔐 Conectado exitosamente. UID: {uid}")

# 🔄 Obtener IDs actuales de ir.model.data
def get_existing_external_ids(model_name):
    records = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read',
                                [[['model', '=', model_name]]],
                                {'fields': ['name', 'module', 'res_id']}
                                )
    return {
        f"{r['module']}.{r['name']}": r['res_id'] for r in records
    }

# 📄 Leer CSV
with open('categorias.csv', newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = list(reader)

# 🧭 Mapeos
external_id_to_odoo_id = get_existing_external_ids('product.category')
name_to_id = {}

# 1️⃣ Crear categorías sin padre
for row in data:
    name = row['Name']
    external_id = row['External ID']
    parent_external_id = row['Parent Category/External ID']

    if parent_external_id:
        continue  # Esperar a padres

    if external_id and external_id in external_id_to_odoo_id:
        print(f"🟡 Categoría ya existente (External ID): {external_id}")
        name_to_id[name] = external_id_to_odoo_id[external_id]
        continue

    # Verificar si ya existe por nombre
    existing = models.execute_kw(db, uid, password, 'product.category', 'search', [[['name', '=', name]]])
    if existing:
        cat_id = existing[0]
        print(f"🟡 Categoría ya existente (por nombre): {name} → ID {cat_id}")
    else:
        cat_id = models.execute_kw(db, uid, password, 'product.category', 'create', [{'name': name}])
        print(f"✅ Creada categoría: {name} → ID {cat_id}")

    if external_id:
        module, name_ext = external_id.split('.')
        models.execute_kw(db, uid, password, 'ir.model.data', 'create', [{
            'name': name_ext,
            'model': 'product.category',
            'module': module,
            'res_id': cat_id
        }])
        external_id_to_odoo_id[external_id] = cat_id

    name_to_id[name] = cat_id

# 2️⃣ Crear subcategorías (con padre)
for row in data:
    name = row['Name']
    external_id = row['External ID']
    parent_external_id = row['Parent Category/External ID']

    if not parent_external_id:
        continue

    if external_id and external_id in external_id_to_odoo_id:
        print(f"🟡 Subcategoría ya existente (External ID): {external_id}")
        continue

    parent_id = external_id_to_odoo_id.get(parent_external_id)
    if not parent_id:
        print(f"⚠️ No se encontró el padre '{parent_external_id}' para '{name}'")
        continue

    # Verificar si ya existe por nombre y padre
    existing = models.execute_kw(db, uid, password, 'product.category', 'search', [[
        ['name', '=', name],
        ['parent_id', '=', parent_id]
    ]])
    if existing:
        cat_id = existing[0]
        print(f"🟡 Subcategoría ya existente: {name} → ID {cat_id}")
    else:
        cat_id = models.execute_kw(db, uid, password, 'product.category', 'create', [{
            'name': name,
            'parent_id': parent_id
        }])
        print(f"✅ Creada subcategoría: {name} → ID {cat_id}")

    if external_id:
        module, name_ext = external_id.split('.')
        models.execute_kw(db, uid, password, 'ir.model.data', 'create', [{
            'name': name_ext,
            'model': 'product.category',
            'module': module,
            'res_id': cat_id
        }])
        external_id_to_odoo_id[external_id] = cat_id

print("✅ Importación terminada correctamente.")
