import xmlrpc.client
from confImp import url, db, username, password

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

# 🔌 Conectar a Odoo
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
if not uid:
    print("❌ Error de autenticación.")
    exit()
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
print(f"🔐 Conectado exitosamente. UID: {uid}")

# 📥 Obtener External IDs para productos
external_ids = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read', [[
    ['model', '=', 'product.template']
]], {'fields': ['model', 'res_id', 'name']})

# Diagnóstico: Imprimir los resultados de external_ids
print("🔍 Resultados de la consulta de External IDs para productos:")
print(external_ids)

# Asegurarse de que todos los campos estén presentes antes de usarlos
external_id_map = {}
for e in external_ids:
    try:
        # Mostrar los campos de cada registro para asegurarnos de que tienen los datos esperados
        print(f"📊 Procesando External ID: {e}")

        # Solo agregamos al mapa si todos los campos necesarios están presentes
        if 'model' in e and 'res_id' in e and 'name' in e:
            external_id_map[f"__export__.{e['model']}_{e['res_id']}_{e['name']}"] = e['res_id']
        else:
            print(f"⚠️ Faltaron campos en el External ID: {e}")
    except KeyError as e:
        print(f"⚠️ Error al procesar el External ID, KeyError: {e}")
        continue

# Verificar que external_id_map no esté vacío
if not external_id_map:
    print("❌ No se encontraron datos válidos para importar.")
    exit()

# 📥 Obtener productos usando los external_ids
product_ids = list(external_id_map.values())
productos = models.execute_kw(db, uid, password, 'product.template', 'read', [product_ids], {
    'fields': ['id', 'name', 'default_code', 'type', 'list_price', 'uom_id', 'categ_id']
})

# Mostrar los productos obtenidos
print("🔍 Productos a importar:")
for p in productos:
    print(p)

# Aquí puedes agregar la lógica de importación de los productos
# Procesar los productos y crear o actualizar en Odoo según lo necesites

print("✅ Importación completada con éxito.")
