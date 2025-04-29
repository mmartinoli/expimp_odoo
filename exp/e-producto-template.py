import csv
import xmlrpc.client
from confExp import url, db, username, password

print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}\n")

confirm = input("¿Deseás continuar con la exportación de productos? (s/n): ").strip().lower()
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

# 📥 Obtener productos
product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', [[]])
productos = models.execute_kw(db, uid, password, 'product.template', 'read', [product_ids], {
    'fields': ['id', 'name', 'default_code', 'type', 'list_price', 'uom_id', 'categ_id']
})

# 📥 External IDs para productos
product_external_ids = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read', [[
    ['model', '=', 'product.template'],
    ['res_id', 'in', [p['id'] for p in productos]]
]], {'fields': ['model', 'res_id', 'name']})

ext_map_product = {
    r['res_id']: f"__export__.{r['model']}_{r['res_id']}_{r['name']}"
    for r in product_external_ids if all(k in r for k in ('model', 'res_id', 'name'))
}

# 📥 External IDs para categorías
categ_ids = list({p['categ_id'][0] for p in productos if p.get('categ_id')})
cat_external_ids = models.execute_kw(db, uid, password, 'ir.model.data', 'search_read', [[
    ['model', '=', 'product.category'],
    ['res_id', 'in', categ_ids]
]], {'fields': ['res_id', 'module', 'name']})

ext_map_categ = {
    r['res_id']: f"__export__.{r['module']}_{r['res_id']}_{r['name']}"
    for r in cat_external_ids
}

# 📥 Unidades de medida
uom_ids = list({p['uom_id'][0] for p in productos if p.get('uom_id')})
uoms = models.execute_kw(db, uid, password, 'uom.uom', 'read', [uom_ids], {'fields': ['id', 'name']})
uom_map = {u['id']: u['name'] for u in uoms}

# 📤 Escribir CSV
with open('productos.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        'External ID', 'Name', 'Default Code', 'Type', 'List Price',
        'Unit of Measure', 'Category External ID'
    ])
    for p in productos:
        external_id = ext_map_product.get(p['id'], '')
        name = p.get('name', '')
        default_code = p.get('default_code', '')
        ptype = p.get('type', '')
        price = p.get('list_price', 0.0)
        uom_name = uom_map.get(p['uom_id'][0], '') if p.get('uom_id') else ''
        categ_external_id = ext_map_categ.get(p['categ_id'][0], '') if p.get('categ_id') else ''

        writer.writerow([
            external_id,
            name,
            default_code,
            ptype,
            price,
            uom_name,
            categ_external_id
        ])

print("✅ Exportación completada: productos.csv")
