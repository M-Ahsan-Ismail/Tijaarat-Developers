from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime

class Accounting_overall(models.Model):
    _inherit = 'account.move'

