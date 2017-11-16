# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re

from odoo import fields, models, _


class HrExpense(models.Model):

    _inherit = "hr.expense"
    provider_id = fields.Many2one('res.partner', string="Proveedor", 
        #states={'draft': [('readonly', False)], 'refused': [('readonly', False)]}, 
    )
    odometer = fields.Integer(string='Kilometraje')

class ResPartner(models.Model):

    _inherit = "res.partner"
    odometer = fields.Integer(string='Kilometraje')

