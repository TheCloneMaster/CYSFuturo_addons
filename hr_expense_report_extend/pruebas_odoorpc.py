#from datetime import datetime, timedelta
import odoorpc
import sys

# Prepare the connection to the server
#oerpOrig = oerplib.OERP('192.168.1.5', protocol='xmlrpc', port=8071)
odoo = odoorpc.ODOO('174.138.86.107', port=8082)  #agrofadaca


# Login (the object returned is a browsable record)
#userO = oerpOrig.login('admin', 'Amecsa..04..adm', 'produccion')
#userO = oerpOrig.login('admin', 'amecsa.03.adm', 'training2')
#odoo.login('prod_agrofadaca', 'admin', 'af.03.adm')
odoo.login('pruebas_liquidaciones', 'admin', 'af.03.adm')


aml = odoo.env['account.move.line']

account_id = 110 #viaticos empleados
partner_id = 808 # Mario 368 # Alberth

moves = aml.get_move_lines_for_manual_reconciliation( account_id, partner_id )

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


