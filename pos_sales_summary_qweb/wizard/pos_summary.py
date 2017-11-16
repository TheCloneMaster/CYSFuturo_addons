# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError

import time
from datetime import datetime

class PosSummary(models.TransientModel):
    _name = 'pos.summary.wizard'
    _description = 'Open Sale Summary Report'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(start_at) as start,
            config_id
            FROM pos_session
            WHERE config_id = ANY(%s)
            AND start_at > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Date(required=True, default=_default_start_date)
    end_date = fields.Date(required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2many('pos.config', 'pos_detail_configs',
        default=lambda s: s.env['pos.config'].search([]))
    show_details = fields.Boolean('Show Details?', help="Check this box if you want to print details on invoices.")

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_report(self):
        # get timedelta between user timezone and UTC
        utc_time = datetime.now()
        user_time = fields.datetime.context_timestamp(cr, uid, utc_time).replace(tzinfo=None)
        user_timedelta = utc_time - user_time
        start_date2 = (datetime.strptime(self.start_date+' 00:00:00',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        end_date2 = (datetime.strptime(self.end_date+' 23:59:59',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        data = {'date_start': start_date2, 'date_stop': end_date2, 'config_ids': self.pos_config_ids.ids, 'show_details': self.show_details}
        return self.env['report'].get_action(
            [], 'pos_sales_summary.report_salesummary', data=data)


##############################################################################


"""
from datetime import datetime
import time
from openerp.osv import osv, fields
from openerp import tools

import logging
_logger = logging.getLogger(__name__)


class pos_summary(osv.osv_memory):
    _name = 'pos.summary'
    _description = 'Sales summary'

    _columns = {
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
        'user_ids': fields.many2many('res.users', 'pos_summary_report_user_rel', 'user_id', 'wizard_id', 'Salespeople'),
        'location_ids': fields.many2many('stock.location', 'pos_summary_report_location_rel', 'location_id', 'wizard_id', 'Locations', domain=[('usage', '=', 'internal')]),
        'show_details': fields.boolean('Show Details?', help="Check this box if you want to print details on invoices."),
}
    _defaults = {
        'date_start': fields.date.context_today,
        'date_end': fields.date.context_today,
        'show_details': True,
    }

    def print_report(self, cr, uid, ids, context=None):
        ""
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        ""
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date_start', 'date_end', 'location_ids','show_details'], context=context)
        res = res and res[0] or {}

        # get timedelta between user timezone and UTC
        utc_time = datetime.now()
        user_time = fields.datetime.context_timestamp(cr, uid, utc_time).replace(tzinfo=None)
        user_timedelta = utc_time - user_time
        date_start2 = (datetime.strptime(res['date_start']+' 00:00:00',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        date_end2 = (datetime.strptime(res['date_end']+' 23:59:59',tools.DEFAULT_SERVER_DATETIME_FORMAT) + user_timedelta).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'pos_sales_summary.report_summaryofsales', data=datas, context=context)
"""
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
