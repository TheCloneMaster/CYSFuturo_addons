# -*- coding: utf-8 -*-

import datetime
import json
import logging
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class AccountInvoiceElectronic(models.Model):
    _inherit = "account.invoice"

    plate_number = fields.Char(string="Placa", required=False, copy=False, index=True)
    hour_service = fields.Char(string="Hora del Servicio", required=False, copy=False, index=True)
    schedule = fields.Char(string="Horario", required=False, copy=False, index=True)
    inf_send = fields.Char(string="Envia", required=False, copy=False, index=True)
    inf_for = fields.Char(string="Para", required=False, copy=False, index=True)
    inf_dni = fields.Char(string="Cédula", required=False, copy=False, index=True)
    invoice_code = fields.Char(string="Código Factura", required=False, copy=False, index=True)
    period_to = fields.Char(string="Del Periodo Del", required=False, copy=False, index=True)
    share_days = fields.Char(string="Días Compartidos", required=False, copy=False, index=True)
    invoice_details = fields.Char(string="Detalle Factura", required=False, copy=False, index=True)
    departure_hour = fields.Char(string="Hora de Salida", required=False, copy=False, index=True)
    amount_buses = fields.Char(string="Cantidad de Buses", required=False, copy=False, index=True)
    amount_passengers = fields.Char(string="Cantidad de Pasajeros", required=False, copy=False, index=True)
    departure_date = fields.Char(string="Fecha de Salida", required=False, copy=False, index=True)
    contract_date = fields.Char(string="Fecha de Contrato", required=False, copy=False, index=True)
    sign_place = fields.Char(string="Lugar Firma", required=False, copy=False, index=True)
    balance_money = fields.Char(string="Saldo", required=False, copy=False, index=True)
    advance_money = fields.Char(string="Adelanto", required=False, copy=False, index=True)
    return_hour = fields.Char(string="Hora de retorno", required=False, copy=False, index=True)
    destination_service = fields.Char(string="Destino", required=False, copy=False, index=True)
    contact_phone = fields.Char(string="Telefono Contacto", required=False, copy=False, index=True)
    departure_place = fields.Char(string="Lugar de Salida", required=False, copy=False, index=True)

    @api.model
    def _default_partner_id(self):
        if self.env.user.partner_id.company_type_tracasa == 'cashier':
            return self.env.user.partner_id

    partner_id = fields.Many2one(default=_default_partner_id)











