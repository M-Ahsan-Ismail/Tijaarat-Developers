# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InheritResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_approval_amount = fields.Float(string="Minimum Approval Amount",help="The minimum amount for which this approval will be triggered",config_parameter='hr_job_custom.minimum_approval_amount')
    