from odoo import fields, models

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    is_subcontractor = fields.Boolean(string='Is Subcontractor')
