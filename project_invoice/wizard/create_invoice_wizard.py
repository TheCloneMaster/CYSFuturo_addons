# -*- coding: utf-8 -*-
# © 2017 CYSFuturo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, _
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)

class CreateInvoiceWizard(models.TransientModel):
    _name = 'create.invoice.wizard'

    def do_invoicing(self):   #, cr, uid, ids, context=None):
        #inv_obj = self.env['account.invoice']
        _logger.error('MAB - ### 1')
        so_obj = self.env['sale.order']
        so_line_obj = self.env['sale.order.line']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        sale_orders = invoices = {}
        references = {}

        #journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        #if not journal_id:
        #    raise UserError(_('Please define an accounting sale journal for this company.'))

        _logger.error('MAB - ### 2')
        tasks = self.env['project.task'].search([('timesheet_ids.invoiced', '=', False),('timesheet_ids.date', '<=', self.date)])
        _logger.error('MAB - ### 3')
        for task in tasks:
            _logger.error('MAB - ### 4.1')
            task_cost = task_expense = 0
            group_key = (task.partner_id.id, task.pricelist_id.id)
            _logger.error('MAB - ### 4.2')
            for line in task.timesheet_ids:
                if line.product_id.type == 'service':
                    _logger.error('MAB - ### 5.1')
                    task_cost += line.total_cost
                else:
                    _logger.error('MAB - ### 5.2')
                    task_expense += line.total_cost
            if float_is_zero(task_cost + task_expense, precision_digits=precision):   #nothing to invoice
                _logger.error('MAB - ### 6')
                continue

            if group_key not in sale_orders:
                _logger.error('MAB - ### 7')
                so_vals = {
                    'validity_date': fields.Date.context_today(self),
                    'partner_id': task.partner_id.id,
                    #'currency_id': task.currency_id.id,
                    'pricelist_id': task.pricelist_id.id,
                    #'note': task.description,
                    'origin': task.name,
                    #'payment_term_id': task.payment_term_id.id,
                    'fiscal_position_id': task.partner_id.property_account_position_id.id,
                    #'company_id': self.company_id.id,
                    #'user_id': self.user_id and self.user_id.id,
                }
                _logger.error('MAB - ### 8 SO VALS = %s', so_vals)
                so = so_obj.create(so_vals)
                _logger.error('MAB - ### 9')
                #references[invoice] = order
                sale_orders[group_key] = so

            else:
                _logger.error('MAB - ### 10')
                sale_orders[group_key].write({
                    #'note'   : ', '.join(sale_orders[group_key].note,task.description),
                    'origin' : ', '.join((sale_orders[group_key].origin,task.name))
                })
                _logger.error('MAB - ### 11')

            so_line_vals = {
                'order_id': sale_orders[group_key].id,
                'product_id': 6,  #Honorarios
                'name': task.name,
                'price_unit': task_cost,
                'product_uom_qty': 1,
                #'product_uom': self.product_uom.id,
            }
            _logger.error('MAB - ### 12')
            so_line = so_line_obj.create(so_line_vals) 
            _logger.error('MAB - ### 13')

            so_line_vals = {
                'order_id': sale_orders[group_key].id,
                'product_id': 1,  #Gastos
                'name': task.name,
                'price_unit': task_expense,
                'product_uom_qty': 1,
                #'product_uom': self.product_uom.id,
            }
            _logger.error('MAB - ### 14')
            so_line = so_line_obj.create(so_line_vals)
            _logger.error('MAB - ### 15')

        _logger.error('MAB - ### 16')
        so_ids = [so.id for so in sale_orders.values()]

        _logger.error('MAB - ### 17')
        return {
            'name': _('Estados de Cuenta'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', so_ids)],
            'context': self.env.context,
            'res_id': self.id,
        }

    date=fields.Date('Fecha Final')

