# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        ''' Store the initial pricelists A B and C'''
        # TDE FIXME: context brol
        template = super(ProductTemplate, self).create(vals)

        # This is needed to set given values to first variant after creation
        related_vals = {}
        PriceListItem = self.env["product.pricelist.item"]
        for pricelist_id in [4,5,6]:
            new_pricelist = PriceListItem.create({
                'pricelist_id': pricelist_id,
                'compute_price': 'fixed',
                'fixed_price': 0.0,
                'min_quantity': 1.0,
                'applied_on': '1_product',
                'product_tmpl_id': template.id,
            })
            if pricelist_id==4:  # List A
               related_vals['lst_price2_id'] = new_pricelist.id
            elif pricelist_id==5: # List B
               related_vals['lst_price3_id'] = new_pricelist.id
            else: #List C
               related_vals['lst_price4_id'] = new_pricelist.id

        if related_vals:
            template.write(related_vals)
        return template

    @api.depends('lst_price2_percent', 'seller_ids.price')
    def _compute_sale_price_A(self):
        for product in self:
            new_price = (product.lst_price2_percent and product.seller_ids and product.seller_ids[0].price / product.lst_price2_percent) or 0
            product.lst_price2 = new_price
            if product.lst_price2_id:
                product.lst_price2_id.fixed_price = new_price
            
    @api.depends('lst_price3_percent','seller_ids.price')
    def _compute_sale_price_B(self):
        for product in self:
            new_price = (product.lst_price3_percent and product.seller_ids and product.seller_ids[0].price / product.lst_price3_percent) or 0
            product.lst_price3 = new_price
            if product.lst_price3_id:
                product.lst_price3_id.fixed_price = new_price

    @api.depends('lst_price4_percent', 'seller_ids.price')
    def _compute_sale_price_C(self):
        for product in self:
            new_price = (product.lst_price4_percent and product.seller_ids and product.seller_ids[0].price / product.lst_price4_percent) or 0
            product.lst_price4 = new_price
            if product.lst_price4_id:
                product.lst_price4_id.fixed_price = new_price

    cost_price2 = fields.Float('Costo base USD', digits_compute=dp.get_precision('Product Price'))
    lst_price2 = fields.Float('Sale Price 2', compute='_compute_sale_price_A', store=True, digits=dp.get_precision('Product Price'))
    lst_price3 = fields.Float('Sale Price 3', compute='_compute_sale_price_B', store=True, digits=dp.get_precision('Product Price'))
    lst_price4 = fields.Float('Sale Price 4', compute='_compute_sale_price_C', store=True, digits=dp.get_precision('Product Price'))
    lst_price2_percent = fields.Float('Sale Price 2 %', digits=dp.get_precision('Product Price'))
    lst_price3_percent = fields.Float('Sale Price 3 %', digits=dp.get_precision('Product Price'))
    lst_price4_percent = fields.Float('Sale Price 4 %', digits=dp.get_precision('Product Price'))
    lst_price2_id = fields.Many2one('product.pricelist.item', 'Lista A')
    lst_price3_id = fields.Many2one('product.pricelist.item', 'Lista B')
    lst_price4_id = fields.Many2one('product.pricelist.item', 'Lista C')

