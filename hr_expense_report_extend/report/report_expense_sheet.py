#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

import logging
_logger = logging.getLogger(__name__)


class ExpenseSheetReport(models.AbstractModel):
    _name = 'report.hr_expense_report_extend.report_expense_sheet_extended'

    def get_related_payments(self, expenses):
        _logger.error('MAB - Expenses %s', expenses)

        account_id = 110 #viaticos empleados
        aml = self.env['account.move.line']
        #partner_id = 368 # Alberth
        
        result = {}
        
        for expense in expenses:
            result[expense.id] = [x for x in aml.get_move_lines_for_manual_reconciliation( account_id, expense.employee_id.address_id.id ) if x['debit'] >0]
            
        _logger.error('MAB - Open Payments %s', result)
        return result
    
    def get_name(self, object):
        return 'Hola amigos'
        result = {}
        self.env.cr.execute("""
            SELECT pl.id from hr_payslip_line as pl
            LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id)
            WHERE (hp.date_from >= %s) AND (hp.date_to <= %s)
            AND pl.register_id in %s
            AND hp.state = 'done'
            ORDER BY pl.slip_id, pl.sequence""",
            (date_from, date_to, tuple(register_ids)))
        line_ids = [x[0] for x in self.env.cr.fetchall()]
        for line in self.env['hr.payslip.line'].browse(line_ids):
            result.setdefault(line.register_id.id, self.env['hr.payslip.line'])
            result[line.register_id.id] += line
        return result

    #def get_details_by_rule_category(self, payslip_lines):
    #    PayslipLine = self.env['hr.payslip.line']
    #    RuleCateg = self.env['hr.salary.rule.category']

    #    res = {}
    #    result = {}

    #    if payslip_lines:
    #        self.env.cr.execute("""
    #    return res

    #def get_lines_by_contribution_register(self, payslip_lines):
    #    result = {}
    #    res = {}
    #    for line in payslip_lines.filtered('register_id'):
    #        result.setdefault(line.slip_id.id, {})
    #        result[line.slip_id.id].setdefault(line.register_id, line)
    #        result[line.slip_id.id][line.register_id] |= line
    #    for payslip_id, lines_dict in result.iteritems():
    #        res.setdefault(payslip_id, [])
    #        for register, lines in lines_dict.iteritems():
    #            res[payslip_id].append({

    @api.model
    def render_html(self, docids, data=None):
        _logger.error('MAB - Render start')
        expense_sheets = self.env['hr.expense.sheet'].browse(docids)
        open_payments = self.get_related_payments(expense_sheets)
        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.expense.sheet',
            'docs': expense_sheets,
            'data': data,
            'get_name': self.get_name(expense_sheets),
            'related_payments': open_payments,
            #'get_details_by_rule_category': self.get_details_by_rule_category(payslips.mapped('details_by_salary_rule_category').filtered(lambda r: r.appears_on_payslip)),
            #'get_lines_by_contribution_register': self.get_lines_by_contribution_register(payslips.mapped('line_ids').filtered(lambda r: r.appears_on_payslip)),
        }
        #return self.env['report'].render('hr_payroll.report_payslipdetails', docargs)
        return self.env['report'].render('hr_expense_report_extend.report_expense_sheet_extended', docargs)
