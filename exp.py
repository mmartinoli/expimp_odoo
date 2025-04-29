import csv
import xmlrpc.client

# Configuración de Odoo
url = 'https://rv.ops.net.ar'
db = 'rv-prod'
username = 'martin.it@revestimientosvitoria.com'
password = '123Telecom'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def export_to_csv(model, fields, filename, domain=None):
    domain = domain or []
    records = models.execute_kw(db, uid, password, model, 'search_read', [domain], {'fields': fields})
    if not records:
        print(f"No se encontraron datos en {model}")
        return

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            writer.writerow({field: rec.get(field, '') for field in fields})

    print(f"Exportado {model} → {filename}")


# Exportar categorías de producto
export_to_csv('product.category', ['id', 'name', 'parent_id'], 'categorias.csv')

# Exportar ccontactos
export_to_csv('res.partner', ['id', 'name', 'is_company','company_id'], 'contactos.csv')


# Exportar productos
export_to_csv('product.template', ['id', 'name', 'default_code', 'type', 'categ_id', 'list_price'], 'productos.csv')

# Exportar variantes (por si hay productos con atributos)
export_to_csv('product.product', ['id', 'product_tmpl_id', 'default_code', 'barcode'], 'productos_variantes.csv')

# Exportar stock (cantidad disponible por almacén)
export_to_csv('stock.quant', ['id', 'product_id', 'location_id', 'quantity'], 'stock.csv')

# Exportar empleados
export_to_csv('hr.employee', ['id', 'name', 'work_email', 'job_id', 'department_id'], 'empleados.csv')

# Exportar ventas
export_to_csv('sale.order', ['id', 'name', 'date_order', 'partner_id', 'amount_total', 'state'], 'ventas.csv')

# Exportar líneas de venta (detalle de productos por orden)
export_to_csv('sale.order.line', ['id', 'order_id', 'product_id', 'product_uom_qty', 'price_unit'], 'ventas_lineas.csv')

# Exportar paquetes (si usás el módulo de inventario avanzado)
export_to_csv('stock.picking', ['id', 'name', 'picking_type_id', 'origin', 'state'], 'paquetes.csv')
