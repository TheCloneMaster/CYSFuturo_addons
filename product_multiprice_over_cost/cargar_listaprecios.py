#Factura
#    ->  Proveedor
#        ->  name, ref, street, phone, mobile, email, customer, supplier, property_account_receivable, property_account_payable
#        invoice_line
#        ->  product_id, name, account_id, quantity, price_unit, 
#        user_id
#        origin, reference, date_invoice, date_due, comment

#from datetime import datetime, timedelta
import odoorpc
import sys

# Prepare the connection to the server
#oerpOrig = oerplib.OERP('192.168.1.5', protocol='xmlrpc', port=8071)
odoo = odoorpc.ODOO('174.138.86.107', port=8082)  #agrofadaca


# Login (the object returned is a browsable record)
#userO = oerpOrig.login('admin', 'Amecsa..04..adm', 'produccion')
#userO = oerpOrig.login('admin', 'amecsa.03.adm', 'training2')
odoo.login('prod_agrofadaca', 'admin', 'af.03.adm')

if 'product.pricelist' in odoo.env:
    List = odoo.env['product.pricelist']
    list_ids = List.search([])
    for list in List.browse(list_ids):
        print(list.name)
        for product in list.item_ids:
            print("     ",product.name)
            if list.name == 'Lista A':
                product.product_tmpl_id.lst_price2_id = product
            elif list.name == 'Lista B':
                product.product_tmpl_id.lst_price3_id = product
            elif list.name == 'Lista C':
                product.product_tmpl_id.lst_price4_id = product


