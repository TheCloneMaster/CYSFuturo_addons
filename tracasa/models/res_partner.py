# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class PartnerElectronic(models.Model):
    _inherit = "res.partner"

    company_type_tracasa = fields.Char(required=False, copy=False, index=True)

    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Compañía'), ('bus', 'Buses'),
                                               ('cashier', 'Cajero'), ('driver', 'Chofer'),
                                               ('external', 'Cliente Externo'),('departament', 'Departamento'),
                                               ('vehicle', 'Vehículo')])

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else self.company_type_tracasa


    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.company_type_tracasa = self.company_type
        self.is_company = (self.company_type == 'company')





