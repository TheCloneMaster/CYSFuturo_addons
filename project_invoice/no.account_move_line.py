# -*- coding: utf-8 -*-
# © 2011 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields


class AccountVoucher(osv.Model):

    _inherit = 'account.voucher'

    _columns = {
        'commission': fields.boolean('Commission'),
    }
