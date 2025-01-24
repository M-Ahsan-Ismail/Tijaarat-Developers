from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project', string='Project')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    is_quality_check = fields.Boolean('Is Quality Check')

    def action_quality_check(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quality Check',
            'res_model': 'quality.check.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_active_id': self.id}
        }

    def button_validate(self):
        if not self.is_quality_check:
            raise UserError('Please click on "Quality Check" button first...!')
        return super().button_validate()
