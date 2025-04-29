import csv
import xmlrpc.client

# Configuración de Odoo (nueva base)
url = 'http://34.70.34.0:8069/'
db = 'prueba'
username = 'mmartinoli@gmail.com'
password = '123Telecom'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def import_from_csv(model, filename, fields, id_field='id'):
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {}
            for field in fields:
                val = row.get(field)
                if val in ['', 'False', 'None']:
                    val = False
                elif field.endswith('_id') or field in ['product_tmpl_id', 'product_id', 'order_id', 'location_id', 'picking_type_id', 'partner_id', 'department_id', 'job_id']:
                    try:
                        val = int(val)
                    except ValueError:
                        val = False
                elif field in ['quantity', 'amount_total', 'price_unit', 'product_uom_qty', 'list_price']:
                    try:
                        val = float(val)
                    except ValueError:
                        val = 0.0

            record['id'] = int(row[id_field])
            # Se crea con el ID original usando context `force_create` si está habilitado en tu módulo
            try:
                models.execute_kw(db, uid, password, model, 'create', [record])
                print(f"✔ Insertado {model} ID {record['id']}")
            except Exception as e:
                print(f"✖ Error en {model} ID {record['id']}: {e}")

# Importar en orden para respetar dependencias

# Categorías
import_from_csv('product.category', 'categorias.csv', ['id', 'name', 'parent_id'])

# Productos
import_from_csv('product.template', 'productos.csv', ['id', 'name', 'default_code', 'type', 'categ_id', 'list_price'])

# Variantes
#import_from_csv('product.product', 'productos_variantes.csv', ['id', 'product_tmpl_id', 'default_code', 'barcode'])

# Empleados
#import_from_csv('hr.employee', 'empleados.csv', ['id', 'name', 'work_email', 'job_id', 'department_id'])

# Ventas
#import_from_csv('sale.order', 'ventas.csv', ['id', 'name', 'date_order', 'partner_id', 'amount_total', 'state'])

# Líneas de venta
#import_from_csv('sale.order.line', 'ventas_lineas.csv', ['id', 'order_id', 'product_id', 'product_uom_qty', 'price_unit'])

# Stock
#import_from_csv('stock.quant', 'stock.csv', ['id', 'product_id', 'location_id', 'quantity'])

# Paquetes / movimientos
#import_from_csv('stock.picking', 'paquetes.csv', ['id', 'name', 'picking_type_id', 'origin', 'state'])