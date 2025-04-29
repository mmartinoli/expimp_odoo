import xmlrpc.client
import csv
import os
from confExp import url, db, username, password

print("📦 Configuración de conexión:")
print(f"🖥️  URL:      {url}")
print(f"🗄️  Base de datos: {db}")
print(f"👤 Usuario:  {username}\n")

# Confirmación
if input("¿Deseás continuar con la exportación de productos? (s/n): ").lower() != 's':
    print("Exportación cancelada.")
    exit()

# Conexión a Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Obtener almacenes
almacenes = models.execute_kw(db, uid, password,
                              'stock.warehouse', 'search_read',
                              [[]], {'fields': ['id', 'name']}
                              )

# Obtener productos
productos = models.execute_kw(db, uid, password,
                              'product.product', 'search_read',
                              [[['type', '=', 'product']]],  # Solo productos físicos
                              {
                                  'fields': [
                                      'id', 'name', 'default_code', 'lst_price', 'standard_price',
                                      'categ_id'
                                  ],
                                  'limit': 10000
                              }
                              )

# Obtener XML IDs
xml_ids = models.execute_kw(db, uid, password,
                            'ir.model.data', 'search_read',
                            [[['model', '=', 'product.product']]],
                            {'fields': ['res_id', 'module', 'name']}
                            )
map_xml_id = {item['res_id']: f"{item['module']}.{item['name']}" for item in xml_ids}

# Crear header del CSV
headers = [
              "ID Externo", "Nombre", "Referencia Interna", "Categoría",
              "Precio de Venta", "Coste"
          ] + [f"Stock {alm['name']}" for alm in almacenes]

def get_categoria_completa(categ_id):
    if not categ_id:
        return ''
    categoria_path = []
    current_id = categ_id[0]

    while current_id:
        categ = models.execute_kw(
            db, uid, password,
            'product.category', 'read',
            [[current_id]],
            {'fields': ['name', 'parent_id']}
        )
        if not categ:
            break
        categoria_path.insert(0, categ[0]['name'])  # Agrega al inicio
        current_id = categ[0]['parent_id'][0] if categ[0]['parent_id'] else None

    return " / ".join(categoria_path)


# Obtener stock por almacén
def stock_por_almacen(product_id, warehouse_id):
    quants = models.execute_kw(db, uid, password,
                               'stock.quant', 'search_read',
                               [[['product_id', '=', product_id], ['warehouse_id', '=', warehouse_id]]],
                               {'fields': ['quantity']}
                               )
    return round(sum(q['quantity'] for q in quants), 2)

# Escribir CSV
with open("productos_exportados.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    for prod in productos:
        # Ajustar ID Externo: xml_id > default_code (≠ "0") > PROD_<id>
        default_code = prod['default_code']
        if default_code and default_code != "0":
            id_externo = default_code
        elif prod['id'] in map_xml_id:
            id_externo = map_xml_id[prod['id']]
        else:
            id_externo = f"PROD_{prod['id']}"

        row = [
            id_externo,
            prod['name'],
            default_code if default_code and default_code != "0" else "",
            get_categoria_completa(prod['categ_id']),
            prod['lst_price'],
            prod['standard_price']
        ]

        for almacén in almacenes:
            stock = stock_por_almacen(prod['id'], almacén['id'])
            row.append(stock)

        writer.writerow(row)

print("✅ Exportación finalizada con éxito. Archivo: productos_exportados.csv")

