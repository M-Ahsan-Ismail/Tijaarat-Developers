from odoo import models, fields, api
from odoo.exceptions import UserError


class MaintenanceApprovalWizard(models.TransientModel):
    _name = "maintenance.approval.wizard"
    _description = "Add Revision Reason"

    remark = fields.Char(string='Remarks')
    state = fields.Char('')

    def update_maintenance_request(self):
        active_id = self.env['maintenance.request'].browse(self._context.get('active_id'))
        active_id.reject_remarks = self.remark
        active_id.stage_id = self.env.ref('tijaarat_maintenance_custom.stage_5').id or 6
