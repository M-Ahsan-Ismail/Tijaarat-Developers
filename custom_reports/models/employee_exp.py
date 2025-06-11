
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class GroupAging(models.Model):
    _inherit = 'hr.employee'