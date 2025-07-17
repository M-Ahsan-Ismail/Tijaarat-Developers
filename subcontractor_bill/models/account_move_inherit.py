from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    sub_contractor_id = fields.Many2one('subcontractor.bill', string='Subcontractor')

    count_sub_contractor_id = fields.Integer('Sub Contractor', compute='_compute_subcontractor')

    @api.depends('sub_contractor_id')
    def _compute_subcontractor(self):
        for x in self:
            relevant_counts = self.env['subcontractor.bill'].search_count([('id', '=', self.sub_contractor_id.id)])
            x.count_sub_contractor_id = relevant_counts

    def action_view_related_sub_contractor(self):
        return {
            'name': 'Related Sub Contractors',
            'res_model': 'subcontractor.bill',
            'view_mode': 'list,form',
            'domain': [('id', '=', self.sub_contractor_id.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
