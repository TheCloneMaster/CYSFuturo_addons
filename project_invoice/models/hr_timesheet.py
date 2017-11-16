# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    #product_id = fields.Many2one(
    #    comodel_name='product.product', string='Product')
    unit_cost = fields.Float(string='unit cost')
    total_cost = fields.Float(string='Total')
    billable = fields.Boolean("Billable", default=True)
    invoiced = fields.Boolean("Invoiced", default=False, readonly=True)

