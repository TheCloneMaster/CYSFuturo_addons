# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Pos Sales Summary',
    'version': '1.0.1',
    'category': 'Point Of Sale',
    'sequence': 6,
    'summary': 'POS sales summary',
    'description': """
POS Sales summary
===========================
    """,
    'author': 'CYSFuturo',
    'images': [
    ],
    'depends': ['point_of_sale'],
    'data': [
        #'wizard/pos_summary.xml',
        #'point_of_sale_report.xml',
        #'product_view.xml',
        #'report/so_pos_order_report_view.xml',
        #'views/report_summaryofsales.xml',
        'views/report_salesummary.xml',
     ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.cysfuturo.com',
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
