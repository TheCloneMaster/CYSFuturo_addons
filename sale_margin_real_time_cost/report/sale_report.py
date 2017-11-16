# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"
    invoice_id = fields.Many2one('account.invoice', string='Factura', readonly=True)

    def _select(self):
        select_str=super(AccountInvoiceReport, self)._select()  #.replace("COALESCE(cr.rate, 1.0)", "cr.rate/ccr.rate")
        return  select_str+ """
            , sub.invoice_id
        """

    def _sub_select(self):
        select_str=super(AccountInvoiceReport, self)._sub_select()  #.replace("COALESCE(cr.rate, 1.0)", "cr.rate/ccr.rate")
        return  select_str+ """
            , ai.id as invoice_id
        """


class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin = fields.Float('Margin')
    cost = fields.Float('Total Cost')

    margin_pct = fields.Float('Margin %')
    unit_cost = fields.Float('Unit Cost')

    zona = fields.Many2one('res.country.state', 'Zona', readonly=True)

    def _select(self):
        select_str=super(SaleReport, self)._select()  #.replace("COALESCE(cr.rate, 1.0)", "cr.rate/ccr.rate")
        return  select_str+ """
            , SUM(l.margin / COALESCE(cr.rate, 1.0)) AS margin
            , SUM(l.margin)/sum(case l.purchase_price when 0 then 1 else l.purchase_price*l.qty_delivered end)*100 AS margin_pct
            , SUM(l.purchase_price / COALESCE(cr.rate, 1.0)) AS unit_cost
            , SUM(l.purchase_price*l.qty_delivered / COALESCE(cr.rate, 1.0)) AS cost
            , partner.state_id as zona
        """

    def _from(self):
        return super(SaleReport, self)._from() + """
            left join res_company c on (c.id = s.company_id)
            left join currency_rate ccr on (ccr.currency_id = c.currency_id and
                ccr.company_id = c.id and
                ccr.date_start <= coalesce(s.date_order, now()) and
                (ccr.date_end is null or ccr.date_end > coalesce(s.date_order, now())))
        """

    def _group_by(self):
        return """where s.state in ('sale', 'done') """ + super(SaleReport, self)._group_by() + """,partner.state_id"""
            

"""
class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.team_id as team_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ai.team_id as team_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.team_id"
"""
    

