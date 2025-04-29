import csv
import xmlrpc.client
from confExp import url, db, username, password  # <-- tu archivo imp.py debe tener estas 4 variables definidas

# 🔧 MOSTRAR CONFIGURACIÓN
print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}")
print()

# ✅ CONFIRMACIÓN DEL USUARIO
confirm = input("¿Deseás continuar con la exportación de categorías? (s/n): ").strip().lower()
if confirm != 's':
    print("🚫 Operación cancelada por el usuario.")
    exit()

# 🔌 CONEXIÓN A ODOO
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

if not uid:
    print("❌ Error de autenticación. Verifica tus credenciales.")
    exit()

print(f"🔐 Conectado exitosamente. UID: {uid}")
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# 📥 1. Obtener todas las categorías
categoria_ids = models.execute_kw(db, uid, password,
                                  'product.category', 'search', [[]])

# 📤 2. Leer campos
categorias = models.execute_kw(db, uid, password,
                               'product.category', 'read', [categoria_ids],
                               {'fields': ['id', 'name', 'parent_id']})

# 🔎 3. Buscar External IDs
ir_model_data = models.execute_kw(db, uid, password,
                                  'ir.model.data', 'search_read',
                                  [[['model', '=', 'product.category'], ['res_id', 'in', [c['id'] for c in categorias]]]],
                                  {'fields': ['res_id', 'module', 'name']})

# 🧭 Mapear res_id → external_id
external_id_map = {
    r['res_id']: f"{r['module']}.{r['name']}"
    for r in ir_model_data
}

# 💾 4. Exportar a CSV
with open('categorias.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['External ID', 'Name', 'Parent Category/External ID'])

    for cat in categorias:
        external_id = external_id_map.get(cat['id'], '')
        parent_external_id = ''
        if cat['parent_id']:
            parent_id = cat['parent_id'][0]
            parent_external_id = external_id_map.get(parent_id, '')
        writer.writerow([external_id, cat['name'], parent_external_id])

print("✅ Exportación completada: categorias.csv")
