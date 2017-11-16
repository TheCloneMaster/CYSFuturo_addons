# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

class ReportSaleDetails(models.AbstractModel):

    _name = 'report.pos_sales_summary_qweb.report_salesummary'


    @api.model
    def get_sale_summary(self, date_start=False, date_stop=False, configs=False):
        """ Serialise the orders of the day information

        params: date_start, date_stop string representing the datetime of order
        """
        if not configs:
            configs = self.env['pos.config'].search([])

        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
        today = today.astimezone(pytz.timezone('UTC'))
        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_stop),
            ('state', 'in', ['paid','invoiced','done']),
            ('config_id', 'in', configs.ids)])

        user_currency = self.env.user.company_id.currency_id

        total = 0.0
        products_sold = {}
        taxes = {}
        pos_orders = []

        for order in orders:
            if pos.state in ['paid', 'done']:
                order_subtotal = order.amount_subtotal
                order_tax = order.amount_tax
                order_total = order.amount_total
            else:
                order_subtotal = order_tax = order_total = 0

            pos_orders.append( {
                'pos_name': order.name + (order.invoice_id and "-"+order.invoice_id.number or ""),
                'date_order': order.date_order,
                'customer_name': order.partner_id.name,
                'subtotal': order_subtotal,
                'tax': order_tax,
                'total': order_total,
                'state': order.state,
                'lines': order.lines,
            })

            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id.compute(order_total, user_currency)
                subtotal += order.pricelist_id.currency_id.compute(order_subtotal, user_currency)
                tax += order.pricelist_id.currency_id.compute(order_tax, user_currency)
            else:
                total += order_total
                subtotal += order_subtotal
                tax += order_tax
                
            currency = order.session_id.currency_id

            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'total':0.0})
                        taxes[tax['id']]['total'] += tax['amount']

        st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
        if st_line_ids:
            self.env.cr.execute("""
                SELECT aj.name, sum(amount) total
                FROM account_bank_statement_line AS absl,
                     account_bank_statement AS abs,
                     account_journal AS aj 
                WHERE absl.statement_id = abs.id
                    AND abs.journal_id = aj.id 
                    AND absl.id IN %s 
                GROUP BY aj.name
            """, (tuple(st_line_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return {
            'subtotal': user_currency.round(subtotal),
            'tax': tax,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.user.company_id.name,
            'taxes': taxes.values(),
            'orders': pos_orders,
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }

    @api.multi
    def render_html(self, docids, data=None):
        data = dict(data or {})
        configs = self.env['pos.config'].browse(data['config_ids'])
        data.update(self.get_sale_summary(data['date_start'], data['date_stop'], configs))
        return self.env['report'].render('pos_sales_summary_qweb.report_salesummary', data)
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
