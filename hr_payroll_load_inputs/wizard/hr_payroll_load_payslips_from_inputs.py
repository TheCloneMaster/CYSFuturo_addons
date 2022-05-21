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

import logging
import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _


from xlrd import open_workbook, XL_CELL_EMPTY, XL_CELL_BLANK, XL_CELL_TEXT

import base64
from cStringIO import StringIO
import re
from calendar import monthrange

_logger = logging.getLogger(__name__)

class hr_payslip_load_inputs(osv.osv_memory):

    _name ='hr.payslip.load.inputs'
    _description = 'Generate payslips from a inputs file'
    _columns = {
        'input_file': fields.binary('Test Importing File', required=False),
        'previous_payroll_date' : fields.date('Last Payroll Date'),
        'from_column': fields.integer('From Column'),
        'to_column': fields.integer('To Column'),
        'run_days': fields.integer('Run Days'),
        'append_inputs': fields.boolean('Append Inputs', help="If it is checked, no payslip will be generated and inputs will be added to existing ones."),
        'off_cycle_new_hires': fields.boolean('Off Cycle New Hires ?', help="If it is checked, will only load base salary for new hires starting from Last Payroll Date"),
        'overwrite_payslip_run_id': fields.many2one('hr.payslip.run', 'Overwrite previous Payslip Batches'),
    }
    _defaults = {
        'from_column':6,
        'to_column':31,
        'run_days':15,
    }


    def sheet_to_dict(self, cr, uid, ids, sheet, from_column, to_column, context={}):
        headers = []
        result = {}
        _logger.error('Colums: %s  Rows: %s', sheet.ncols, sheet.nrows)
        
        for col in range(sheet.ncols):
            headers.append(sheet.cell(1,col).value)

        for row in range(2,sheet.nrows):
            line = []
            emp_id = sheet.cell(row,0).value
            for col in range(from_column,to_column+1):
                if sheet.cell(row,col).ctype in (XL_CELL_BLANK, XL_CELL_EMPTY):
                    continue
                elif sheet.cell(row,col).ctype == XL_CELL_TEXT :
                    line.append((headers[col], re.sub('[a-zA-Z, \xa2]','', sheet.cell(row,col).value)))
                else :
                    line.append((headers[col], sheet.cell(row,col).value))
            result[emp_id]=line
            _logger.error('Employee: %s Line : %s ', emp_id, line)
               
        return result
    
    def create_payslips(self, cr, uid, ids, payroll_dict, previous_payroll_date, off_cycle_new_hires, run_days, previous_payslip_run_id, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        slip_line_pool = self.pool.get('hr.payslip.line')
        run_pool = self.pool.get('hr.payslip.run')
        contract_obj = self.pool.get('hr.contract')

        run_data = {}
        active_id = context.get('active_id', False)
        if context and active_id:
            run_data = run_pool.read(cr, uid, active_id, ['name', 'date_start', 'date_end', 'credit_note', 'journal_id'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        journal_id = run_data.get('journal_id', False)[0]

        slip_ids = []
        
        search_criteria = ['|',('date_end', '=', False),('date_end', '>=', from_date)]
        if off_cycle_new_hires:
            search_criteria =  ['&',('date_start', '>', previous_payroll_date)] + search_criteria
            
        contract_ids = contract_obj.search(cr, uid, search_criteria )
        contract_datas = contract_obj.browse(cr, uid, contract_ids)

        for contract_data in contract_datas :
            if contract_data.date_end:
                # The employee was terminated, so we need to check for real days worked
                base_days = run_days - min(30,int(to_date[8:])) + min(int(contract_data.date_end[8:]),30)
            else:
                base_days = run_days
                
            if previous_payroll_date<contract_data.date_start:
                payroll_start_date = datetime.strptime(from_date, '%Y-%m-%d')
                contract_start_date = datetime.strptime(contract_data.date_start, '%Y-%m-%d')
                payroll_month = payroll_start_date.month
                contract_start_month = contract_start_date.month

                delta_days = relativedelta.relativedelta(payroll_start_date, contract_start_date)
                month_adjustment = 0
                if payroll_month > contract_start_month:
                    if contract_start_month in (1,3,5,7,8,10,12):
                        month_adjustment = -1
                    elif contract_start_month == 2:
                        month_adjustment = 2
                base_days+= delta_days.days + month_adjustment
            base_hours = base_days * contract_data.hourly_wage

            emp_inputs = [{
                          'name': "CREHB01",
                          'code': "CREHB01",
                          'amount': base_hours,
                          'contract_id': contract_data.id,
            }]
            
            if previous_payslip_run_id:
                previous_gross = 0
                previous_maternity = 0
                
                ### Get previous Maternity help, to adjust salary taxes
                previous_maternity_ids = slip_line_pool.search( cr, uid, 
                                                            [('slip_id.payslip_run_id', '=', previous_payslip_run_id),
                                                             ('contract_id', '=', contract_data.id),
                                                             ('sequence','=',118)])   ## Maternity line sequence
                previous_maternity_vals = slip_line_pool.read(cr, uid, previous_maternity_ids, ['amount'])
                if isinstance(previous_maternity_vals, list):
                    if len(previous_maternity_vals):
                        previous_maternity = previous_maternity_vals[0]['amount']

                ### Get previous Gross salary, to adjust salary taxes
                previous_gross_ids = slip_line_pool.search( cr, uid, 
                                                            [('slip_id.payslip_run_id', '=', previous_payslip_run_id),
                                                             ('contract_id', '=', contract_data.id),
                                                             ('sequence','=',150)])   ## Gross slip line sequence
                previous_gross_vals = slip_line_pool.read(cr, uid, previous_gross_ids, ['amount'])
                if isinstance(previous_gross_vals, list):
                    if len(previous_gross_vals):
                        previous_gross = previous_gross_vals[0]['amount'] - previous_maternity

                        ## Now get previous tax amount, to deduct from current amount
                        previous_tax_ids = slip_line_pool.search( cr, uid, 
                                                                    [('slip_id.payslip_run_id', '=', previous_payslip_run_id),
                                                                     ('contract_id', '=', contract_data.id),
                                                                     ('sequence','=',180)]) ## Tax slip line sequence
                        previous_tax = slip_line_pool.read(cr, uid, previous_tax_ids, ['amount'])
                        if isinstance(previous_tax, list):
                            if len(previous_tax):
                                previous_tax = previous_tax[0]['amount']
                                emp_inputs.append({
                                              'name': "PREVIOUS_TAX",
                                              'code': "PREVIOUS_TAX",
                                              'amount': previous_tax,
                                              'contract_id': contract_data.id
                                })
                # always create previous gross code for second run...
                emp_inputs.append({
                              'name': "PREVIOUS_GROSS",
                              'code': "PREVIOUS_GROSS",
                              'amount': previous_gross,
                              'contract_id': contract_data.id
                })

            if not off_cycle_new_hires:
                inputs = payroll_dict.get(contract_data.employee_id.identification_id, [])
                for input_code, input_value in inputs:
                    input_rec = {
                              'name': input_code,
                              'code': input_code,
                              'amount': input_value,
                              'contract_id': contract_data.id,
                    }
                    emp_inputs.append(input_rec)
    
            slip_data = {
                'employee_id': contract_data.employee_id.id,
                'name': contract_data.employee_id.identification_id + ' payslip details for '+contract_data.employee_id.name+
                        ' ' + contract_data.employee_id.last_name ,
                'struct_id': contract_data.struct_id.id,
                'contract_id': contract_data.id or False,
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in emp_inputs],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
                'journal_id': journal_id,
            }
            slip_ids.append(slip_pool.create(cr, uid, slip_data, context=context))

        
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return slip_ids


    def add_inputs(self, cr, uid, ids, payroll_dict, overwrite_payslip_run_id, context=None):
        slip_pool = self.pool.get('hr.payslip')
        slip_input_pool = self.pool.get('hr.payslip.input')
        slip_line_pool = self.pool.get('hr.payslip.line')
        emp_pool = self.pool.get('hr.employee')

        active_id = context.get('active_id', False)

        slip_ids = []
        for emp_code, inputs in payroll_dict.iteritems():
            if not inputs:
                continue
            
            
            emp_id = emp_pool.search(cr, uid, [('identification_id', '=', emp_code)])
            slip_id = slip_pool.search(cr, uid, [('payslip_run_id', '=', overwrite_payslip_run_id or active_id),('employee_id', '=', emp_id)])
            if slip_id:
                if isinstance(slip_id, list):
                    if len(slip_id):
                        slip_id = slip_id[0]
                    else:
                        continue  # should raise error
            else:
                run_pool = self.pool.get('hr.payslip.run')
                run_data = {}
                if context and active_id:
                    run_data = run_pool.read(cr, uid, active_id, ['name', 'date_start', 'date_end', 'credit_note', 'journal_id'])
                from_date =  run_data.get('date_start', False)
                to_date = run_data.get('date_end', False)
                credit_note = run_data.get('credit_note', False)
                journal_id = run_data.get('journal_id', False)[0]
                contract_obj = self.pool.get('hr.contract')
                contract_ids = contract_obj.search(cr, uid, [('name', '=', emp_code)] )
                _logger.error('MAB *** Emp Code = %s', emp_code)
                contract_data = contract_obj.browse(cr, uid, contract_ids)[0]

                slip_data = {
                    'employee_id': contract_data.employee_id.id,
                    'name': contract_data.employee_id.identification_id + ' payslip details for '+contract_data.employee_id.name+
                            ' ' + contract_data.employee_id.last_name ,
                    'struct_id': contract_data.struct_id.id,
                    'contract_id': contract_data.id or False,
                    'payslip_run_id': active_id,
                    'date_from': from_date,
                    'date_to': to_date,
                    'credit_note': credit_note,
                    'journal_id': journal_id,
                }
                slip_id = slip_pool.create(cr, uid, slip_data, context=context)


                
            slip_obj = slip_pool.browse(cr, uid, slip_id, context=context)
            slip_contract_id = slip_obj.contract_id.id
            
            if overwrite_payslip_run_id:
                slip_pool.write(cr, uid, slip_id, {'payslip_run_id': active_id}, context=context)
            
            for input_code, input_value in inputs:
                current_input = slip_input_pool.search(cr, uid, [('payslip_id', '=', slip_id),('code', '=', input_code)])
                if isinstance(current_input, list):
                    if len(current_input):
                        current_input = current_input[0]
                    else:
                        current_input = False
                        
                if current_input:
                    input_obj = slip_input_pool.browse(cr, uid, current_input, context=context)
                    slip_input_pool.write(cr, uid, current_input, {'amount': input_obj.amount+float(input_value)}, context=context)
                else:
                    input_rec = {
                              'name': input_code,
                              'code': input_code,
                              'amount': input_value,
                              'contract_id': slip_contract_id,
                              'payslip_id':slip_id,
                    }
                    slip_input_pool.create(cr, uid, input_rec, context=context)
                slip_ids.append(slip_id)
            # need to implement automatic get old value to get difference...
            #current_slip_net_id = slip_line_pool.search(cr, uid, [('payslip_id', '=', slip_id),('code', '=', 'NETCR')])
            #current_slip_net = 
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return slip_ids

    def load_inputs(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        input_file = data['input_file']
        from_column = data['from_column']
        to_column = data['to_column']
        run_days = data['run_days']
        append_inputs = data['append_inputs']
        off_cycle_new_hires = data['off_cycle_new_hires']
        overwrite_payslip_run_id = data['overwrite_payslip_run_id'] and data['overwrite_payslip_run_id'][0]
        previous_payroll_date = data['previous_payroll_date']
        if not off_cycle_new_hires:
            if not input_file:
                raise osv.except_osv(_("Warning !"), _("You must select a file to generate payslip(s)."))
                
            base64content=base64.b64decode(input_file)
            workbook = open_workbook(file_contents=base64content)
            sheet=workbook.sheets()[0]
            
            payroll_dict = self.sheet_to_dict(cr, uid, ids, sheet, from_column, to_column, context=context)

            if not payroll_dict:
                raise osv.except_osv(_("Warning !"), _("No data loaded, please check file name and content"))
        else:
            payroll_dict={}
            
        if not append_inputs:
            slip_ids = self.create_payslips(cr, uid, ids, payroll_dict, previous_payroll_date, off_cycle_new_hires, run_days, overwrite_payslip_run_id, context)
        else:
            slip_ids = self.add_inputs(cr, uid, ids, payroll_dict, overwrite_payslip_run_id, context)
            
        return {'type': 'ir.actions.act_window_close'}


hr_payslip_load_inputs()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
