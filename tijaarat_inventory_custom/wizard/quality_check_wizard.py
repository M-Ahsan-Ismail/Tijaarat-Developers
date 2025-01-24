from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class QualityCheckWizard(models.TransientModel):
    _name = 'quality.check.wizard'

    remarks = fields.Char(string='Remarks')


    def button_pass(self):
        active_id = self.env.context.get('active_id')
        obj = self.env['stock.picking'].browse(active_id)
        obj.is_quality_check = True
        obj.note = self.remarks

    def button_fail(self):
        for x in self:
            pass
