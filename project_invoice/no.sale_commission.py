# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields
from openerp.tools.translate import _


class CommissionRule(osv.Model):
    """Commission Rule"""

    _name = 'sale.commission.rule'

    _description = __doc__

    def _check_post_expiration_days(self, cr, uid, ids, context=None):
        for rule in self.browse(cr, uid, ids, context=context):
            if rule.post_expiration_days < 0:
                return False
        return True

    _columns = {
        'name': fields.char('Rule Name', size=128, required=True),
        'member_ids': fields.one2many('res.users', 'sale_commission_rule_id',
                                      string='Members'),
        'post_expiration_days': fields.integer(
            string='Post-Expiration Days', required=True,
            help='Quantity of days of tolerance between the '
                 'invoice due date and the payment date.'),
        'line_ids': fields.one2many('sale.commission.rule.line',
                                    'commission_rule_id', 'Rule Lines'),
        'company_id': fields.many2one('res.company', string='Company'),
        'global_base': fields.integer(
            string='Base General', required=True,
            help='Base a aplicar a todas las reglas que se asocien '
                 'a la base global.'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(cr, uid,
                                                'sale.commission.rule',
                                                context=c),
    }

    _constraints = [
        (_check_post_expiration_days, 'Value must be greater or equal than 0.',
         ['post_expiration_days'])]


class CommissionRuleLine(osv.Model):
    """Commission Rule Line"""

    _name = 'sale.commission.rule.line'

    _description = __doc__

    _order = 'sequence asc'

    def _check_sequence(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.sequence < 0:
                return False
        return True

    def _check_percentages(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if (not (0.0 <= line.commission_percentage <= 100.0)) or \
                    (not (0.0 <= line.max_discount <= 100.0)):
                return False
        return True

    def _check_monthly_sales(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.monthly_sales < 0.0:
                return False
        return True

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'sequence': fields.integer('Sequence', required=True,
                                   help='Lower sequence, more priority.'),
        'commission_percentage': fields.float('Commission (%)', digits=(16, 2),
                                              required=True),
        'commission_fix': fields.float('Commission (fija)', digits=(16, 2),
                                              required=True),
        'commission_rule_id': fields.many2one('sale.commission.rule',
                                              string='Commission Rule'),
        'partner_category_id': fields.many2one(
            'res.partner.category', string='Partner Category',
            help='True if empty or the partner belongs to this category.'),
        'pricelist_id': fields.many2one(
            'product.pricelist', string='Pricelist',
            help='True if empty or uses this Pricelist'),
        'payment_term_id': fields.many2one(
            'account.payment.term', string='Payment Term',
            help='True if empty or belongs to the Payment Term'),
        'max_discount': fields.float('Max Discount (%)', digits=(16, 2),
                                     help='True if empty or met'),
        'monthly_sales': fields.float('Monthly Sales', digits=(16, 2),
                                      help='True if empty or met.'),
        #MAB                              
        'product_category_id': fields.many2one(
            'product.category', string='Product Category',
            help='True if empty or the product belongs to this category.'),
        'product_id': fields.many2one(
            'product.product', string='Product',
            help='True if empty or the product matches.'),
        'use_global_base': fields.boolean('Aplica a base global'),
    }

    _constraints = [(_check_sequence, 'Value must be greater or equal than 0.',
                     ['sequence']),
                    (_check_percentages,
                     'Value must be greater or equal than 0 and lower '
                     'or equal than 100.',
                     ['commission_percentage', 'max_discount']),
                    (_check_monthly_sales, 'Sales can not be negative',
                     ['monthly_sales'])]

    _sql_constraints = [
        ('unique_sequence_rule', 'UNIQUE(sequence,commission_rule_id)',
         'Sequence must be unique for every line in a Commission Rule.')]


class Commission(osv.Model):
    """Commission"""

    _name = 'sale.commission.commission'

    _description = __doc__

    _order = 'invoice_id asc, voucher_id asc'

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'},
                          context=context)

    def pay(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    def expired(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'expired'}, context=context)

    def _check_amount(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            if commission.amount < 0.0:
                return False
        return True

    def _check_percentage(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            if commission.invoice_commission_percentage < 0.0 or \
                            commission.invoice_commission_percentage > 100.0:
                return False
        return True

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            res.append((item.id, '%s - %s' % (
                item.user_id.name, item.invoice_id.number)))
        return res

    def unlink(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            commission.voucher_id.write({'commission': False}, context=context)
        return super(Commission, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(
            _('Failed to copy the record'),
            _('Commissions can not be copied in order to '
              'maintain integrity with the payments.'))

    def create(self, cr, uid, values, context=None):
        commission_id = super(Commission, self).create(cr, uid, values,
                                                       context=context)
        commission = self.browse(cr, uid, commission_id, context=context)
        commission.voucher_id.write({'commission': True}, context=context)
        return commission_id

    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        if 'voucher_id' in values:
            # Get the new assigned voucher
            new_voucher = values['voucher_id']
            # Update all vouchers involved and set commission to False
            move_line_obj = self.pool.get('account.move.line')
            for voucher_data in self.read(cr, uid, ids, ['voucher_id'],
                                          context=context):
                move_line_obj.write(cr, uid, voucher_data['voucher_id'][0],
                                    {'commission': False}, context=context)
            # Update the new voucher and set commission to True
            move_line_obj.write(cr, uid, new_voucher, {'commission': True},
                                context=context)
        return super(Commission, self).write(cr, uid, ids, values,
                                             context=context)

    _columns = {
        'invoice_id': fields.many2one('account.invoice', string='Invoice',
                                      required=False),
        'period_id': fields.related(
            'voucher_id', 'period_id', type='many2one', obj='account.period',
            string='Period', readonly=True),
        'currency_id': fields.related(
            'invoice_id', 'currency_id', type='many2one', obj='res.currency',
            string='Currency', readonly=True),
        'voucher_id': fields.many2one('account.voucher', string='Payment',
                                      required=True),
        'state': fields.selection(
            [('new', 'New'), ('paid', 'Paid'), ('expired', 'Expired'),
             ('cancelled', 'Cancelled')], string='State'),
        'user_id': fields.many2one('res.users', string='Salesperson',
                                   required=True),
        'invoice_base': fields.float('Invoice base', digits=(16, 2)),
        'invoice_line_id': fields.many2one('account.invoice.line', string='Invoice Line',
                                      required=False),
        'product_id': fields.many2one('product.product', string='Producto',
                                      required=False),
        'qty': fields.float('Qty', digits=(16, 2)),
        'list_price': fields.float('Line list price', digits=(16, 2)),
        'line_subtotal': fields.float('Line subtotal', digits=(16, 2)),
        'amount_base': fields.float('Base Amount', digits=(16, 2)),
        'amount': fields.float('Amount', digits=(16, 2)),
        'invoice_commission_percentage': fields.float('Commission (%)',
                                                      digits=(16, 2)),
        'company_id': fields.many2one('res.company', string='Company'),


        #MAB
        'invoice_number' : fields.char(string='Invoice Number', index=True,
            readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', string='Cliente',
                                   required=True),
        'date_invoice': fields.related(
            'invoice_id', 'date_invoice', type='date', string='Invoice Date',
            readonly=True),
        'date_paid': fields.related(
            'voucher_id', 'date', type='date', string='Payment Date',
            readonly=True),
        'plazo_pago': fields.selection(
            [('Contado', 'Contado'), ('Credito', 'Credito')], string='Plazo Pago'),
        'rule_summary_id': fields.many2one('sale.commission.rule.summary', 'Resumen Regla Asociado', ondelete='cascade'),
    }

    _constraints = [
        (_check_amount, 'Value must be greater than 0.', ['amount']),
        (_check_percentage, 'Value must be greater than 0 and '
                            'lower or equal than 100',
         ['invoice_commission_percentage'])]

    #_sql_constraints = [('unique_vucher', 'UNIQUE(voucher_id)',
    #                     'Only one commission can be associated '
    #                     'with a specific payment.')]

    _defaults = {
        'state': 'new',
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(cr, uid,
                                                'sale.commission.commission',
                                                context=c),
    }
    
###############
"""
update data to new table structure, only needed to migrate from original version
update sale_commission_summary
set credito_regular=amount_credit,
total_credito=amount_credit,
contado_regular=amount_cash,
total_contado=amount_cash,
receivable_regular=amount_base,
total_receivable=amount_base,
comision_regular=amount,
total_comision=amount
where amount is not null
"""
###############

class CommissionRuleSummary(osv.Model):
    """Commission Rule Summary"""

    _name = 'sale.commission.rule.summary'

    _description = __doc__

    _order = 'sequence asc'


    def unlink(self, cr, uid, ids, context=None):
        commission_obj = self.pool.get('sale.commission.commission')
        for summary in self.browse(cr, uid, ids, context=context):
            commission_obj.unlink(cr, uid, [l.id for l in summary.commission_line_ids], context=context)
        return super(CommissionRuleSummary, self).unlink(cr, uid, ids, context=context)

    _columns = {
        'commission_rule_line_id': fields.many2one('sale.commission.rule.line',
                                              string='Commission Rule Line'),
        'summary_id': fields.many2one('sale.commission.summary', 'Resumen Asociado', ondelete='cascade'),
        'base': fields.related('commission_rule_line_id', 'monthly_sales', type='float', string='Mínimo a Facturar',readonly=True),
        'sequence': fields.related('commission_rule_line_id', 'sequence', type='integer', readonly=True),
        'total_base_percentage': fields.float('% Sobre Base', digits=(16, 2)),

        'rule_receivable': fields.float('Total Comisionable', digits=(16, 2)),
        'commission_percentage': fields.float('Commission (%)',
                                                      digits=(16, 3)),
        'total_comision': fields.float('Total Comision', digits=(16, 2)),
        'commission_line_ids': fields.one2many('sale.commission.commission', 'rule_summary_id', 'Detalles de Comision'),
    }


class CommissionSummary(osv.Model):
    """Commission Summary"""

    _name = 'sale.commission.summary'

    _description = __doc__

    _order = 'period_id asc, user_id asc'

    def cancel(self, cr, uid, ids, context=None):
        rule_obj = self.pool.get('sale.commission.rule.summary')
        for summary in self.browse(cr, uid, ids):
            rule_obj.write(cr, uid, [l.id for l in summary.rule_summary_ids], {'state': 'cancelled'})

        return self.write(cr, uid, ids, {'state': 'cancelled'},
                          context=context)

    def pay(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)


    def name_get(self, cr, uid, ids, context=None):
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            res.append((item.id, '%s - %s' % (
                item.user_id.name, item.period_id.name)))
        return res

    def unlink(self, cr, uid, ids, context=None):
        rule_obj = self.pool.get('sale.commission.rule.summary')
        for summary in self.browse(cr, uid, ids, context=context):
            rule_obj.unlink(cr, uid, [l.id for l in summary.rule_summary_ids], context=context)
        return super(CommissionSummary, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(
            _('Failed to copy the record'),
            _('Commissions can not be copied in order to '
              'maintain integrity with the payments.'))

    _columns = {
        'company_id': fields.many2one('res.company', string='Company'),
        'currency_id': fields.related(
            'company_id', 'currency_id', type='many2one', obj='res.currency',
            string='Currency', readonly=True),
        'period_id': fields.many2one(
            'account.period', string='Period', readonly=True),
        'user_id': fields.many2one('res.users', string='Salesperson',
                                   required=True),
        'global_base': fields.float('Mínimo a Facturar', digits=(16, 2)),

        'total_receivable': fields.float('Total Comisionable', digits=(16, 2)),

        'total_comision': fields.float('Total Comision', digits=(16, 2)),

        'date_calc' : fields.date(string='Calculation Date',
            readonly=True),
        'date_paid' : fields.date(string='Paid Date',
            readonly=True),
        'state': fields.selection(
            [('new', 'New'), ('paid', 'Paid'), ('expired', 'Expired'),
             ('cancelled', 'Cancelled')], string='State'),
        'rule_summary_ids': fields.one2many('sale.commission.rule.summary', 'summary_id', 'Detalles de Comision'),
    }


    _defaults = {
        'state': 'new',
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(cr, uid,
                                                'sale.commission.summary',
                                                context=c),
        'date_calc': fields.date.context_today,
    }    
