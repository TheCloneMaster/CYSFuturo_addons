# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin = fields.Float(compute='_product_margin', digits=dp.get_precision('Product Price'), store=True)
    purchase_price = fields.Float(compute='_product_margin', string='Cost', digits=dp.get_precision('Product Price'), store=True)

    def _compute_margin(self, order_id, product_id, product_uom_id):
        price = 0
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        if self.product_uom_qty == self.qty_delivered and self.qty_delivered != 0:
            for move in self.procurement_ids.mapped('move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    price += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)*move.price_unit
                elif move.location_dest_id.usage == "internal" and move.to_refund_so:
                    price -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)*move.price_unit
            ctx = self.env.context.copy()
            ctx['date'] = order_id.date_order
            price = frm_cur.with_context(ctx).compute(price/self.product_uom_qty, to_cur, round=False)
        return price
        #####
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        ctx = self.env.context.copy()
        ctx['date'] = order_id.date_order
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return price
        ####


    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        price = 0
        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist_id.currency_id
        if self.product_uom_qty == self.qty_delivered:
            for move in self.procurement_ids.mapped('move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    price += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)*move.price_unit
                elif move.location_dest_id.usage == "internal" and move.to_refund_so:
                    price -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)*move.price_unit
            ctx = self.env.context.copy()
            ctx['date'] = order_id.date_order
            price = frm_cur.with_context(ctx).compute(price, to_cur, round=False)
        return price
        #######
        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist.currency_id
        purchase_price = product.standard_price
        if product_uom != product.uom_id:
            purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        ctx = self.env.context.copy()
        ctx['date'] = date
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return {'purchase_price': price}

    """
    @api.onchange('product_id', 'product_uom')
    def product_id_change_margin(self):
        if not self.order_id.pricelist_id or not self.product_id or not self.product_uom:
            return
        self.purchase_price = self._compute_margin(self.order_id, self.product_id, self.product_uom)

        @api.model
        def create(self, vals):
            # Calculation of the margin for programmatic creation of a SO line. It is therefore not
            # necessary to call product_id_change_margin manually
            if 'purchase_price' not in vals:
                order_id = self.env['sale.order'].browse(vals['order_id'])
                product_id = self.env['product.product'].browse(vals['product_id'])
                product_uom_id = self.env['product.uom'].browse(vals['product_uom'])

                vals['purchase_price'] = self._compute_margin(order_id, product_id, product_uom_id)

            return super(SaleOrderLine, self).create(vals)
    """

    @api.depends('product_id', 'product_uom_qty', 'price_unit', 'qty_delivered')
    def _product_margin(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            line.purchase_price = line._compute_margin(line.order_id, line.product_id, line.product_uom)
            line.margin = (line.purchase_price and currency.round(line.price_subtotal - (line.purchase_price * line.product_uom_qty))) or 0.0


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Monetary(compute='_product_margin', help="It gives profitability by calculating the difference between the Unit Price and the cost.", currency_field='currency_id', digits=dp.get_precision('Product Price'), store=True)

    @api.depends('order_line.margin')
    def _product_margin(self):
        for order in self:
            order.margin = sum(order.order_line.filtered(lambda r: r.state != 'cancel').mapped('margin'))
