# -*- coding: utf-8 -*-
# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Task(models.Model):
    _inherit = "project.task"

    material_ids = fields.One2many(
        comodel_name='project.task.material', inverse_name='task_id',
        string='Material used')


class ProjectTaskMaterial(models.Model):
    _name = "project.task.material"
    _description = "Task Material Used"

    task_id = fields.Many2one(
        comodel_name='project.task', string='Task', ondelete='cascade',
        required=True)
    quantity = fields.Float(string='Quantity')

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    _('Quantity of material consumed must be greater than 0.')
                )
                
                
class ProjectProject(models.Model):
    _inherit = 'project.project'

    location_source_id = fields.Many2one(
        comodel_name='stock.location',
        string='Source Location',
        index=True,
        help='Default location from which materials are consumed.',
    )
    location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Destination Location',
        index=True,
        help='Default location to which materials are consumed.',
    )
"""

