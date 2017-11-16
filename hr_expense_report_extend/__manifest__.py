# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Expense Report Extend',
    'version': '1.0',
    'category': 'Human Resources',
    'sequence': 95,
    'summary': 'Expenses Validation, Invoicing',
    'description': """
Expense Report Extend
=====================

This module overwrites expense report, to add open payments in draft and realized paymend in done states
    """,
    'website': 'https://www.odoo.com/page/expenses',
    'depends': ['hr_expense'],
    'data': [
        'report/report_expense_sheet.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
