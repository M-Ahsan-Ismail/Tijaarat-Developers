from reportlab.lib.pagesizes import elevenSeventeen
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.models import Model


class TijaaratMaintenanceCustom(models.Model):
    _inherit = 'maintenance.request'

    maintenance_cost = fields.Float('Maintenance Cost')
    partner_id = fields.Many2one('res.partner', 'Partner')
    reject_remarks = fields.Char('Rejected Remarks', tracking=True)
    move_id = fields.Many2one('account.move', 'Bill')
    maintenance_count = fields.Integer(string='Number of Bills', compute='_compute_maintenance_count')

    stage_seq = fields.Integer(related='stage_id.sequence')
    def action_submit(self):
        for x in self:
            try:
                x.stage_id = self.env.ref('tijaarat_maintenance_custom.stage_sfa').id
            except Exception as e:
                raise UserError(e)
    def action_ceo_approval(self):
        for x in self:
            try:
                if not x.maintenance_cost:
                    raise UserError('Maintenance cost must be set')
                x.stage_id = self.env.ref('tijaarat_maintenance_custom.stage_approval').id or 5
            except Exception as e:
                raise UserError(e)

    def action_in_progress(self):
        for rec in self:
            rec.stage_id = 2

    def action_repaired(self):
        for rec in self:
            rec.stage_id = 3

    def action_scrap(self):
        for rec in self:
            rec.stage_id = 4

    def create_vendor_bill(self):
        for x in self:
            data = []
            line_data = {
                'name': f'{x.equipment_id.name} {x.equipment_id.serial_no}',
                'quantity': 1,
                'price_unit': x.maintenance_cost
            }
            data.append((0, 0, line_data))

            vals = {
                'invoice_line_ids': data,
                'invoice_date': x.request_date,
                'invoice_date_due': x.close_date,
                'partner_id': x.partner_id.id,
                'move_type': 'in_invoice',
                'maintenance_id': x.id
            }
            bill = self.env['account.move'].create(vals)
            x.move_id = bill.id

    def action_reject(self):
        return {
            'name': 'Rejected',
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.approval.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_state': self.stage_id.id},
            'view_id': self.env.ref("tijaarat_maintenance_custom.view_maintenance_approvals_wizard_form").id,
            'target': 'new',
        }

    @api.depends('equipment_id')
    def _compute_maintenance_count(self):
        for x in self:
            x.maintenance_count = self.env['account.move'].search_count(
                [('maintenance_id', '=', self.id)])

    def action_open_maintenance_history(self):
        return {
            'name': f'Bill',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
                'domain': [('id', '=', self.move_id.id), ('maintenance_id', '=', self.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }



class AccountMove(models.Model):
    _inherit = 'account.move'

    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')