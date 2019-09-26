# -*- coding: utf-8 -*-

{
    'name': 'Tracasa Module',
    'version': '12.0.2.0.0',
    'author': 'CYSFuturo.org',
    'license': 'AGPL-3',
    'website': 'https://github.com/cysfuturo',
    'category': 'Account',
    'description':
        '''
        Modulo para Tracasa
        ''',
    'depends': [
        'base',
        'account'],
    'data': [
        'security/tracasa_security.xml',
        'views/account_invoice_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
