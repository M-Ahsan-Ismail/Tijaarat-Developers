from odoo import fields, models


class ResConfigInherited(models.TransientModel):
    _inherit = 'res.config.settings'

    ded_adv_account_id = fields.Many2one(
        'account.account',
        string="Deduction/Advance Account",
        help="Default account used for subcontractor deduction or advance entries.",
        config_parameter='subcontractor_bill.ded_adv_account_id',
        readonly=False
    )
