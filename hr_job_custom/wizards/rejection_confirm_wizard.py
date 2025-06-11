from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RejectionConfirmWizard(models.TransientModel):
    _name = "rejection.confirm.reason.wizard"
    _description = "Rejection Confirmation"
    
    reason = fields.Char(string="Reason", required=True)

    refused_by = fields.Selection([
        ('candidate', 'Candidate'),
        ('company', 'Company')
    ],string="Refused by")

    def confirm_refuse(self):
        context=self.env.context
        requestId=context.get('request')
        request=self.env['approval.request'].browse(requestId)
        
        request.action_refused_confirm(self.reason)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request', 
            'view_mode': 'form',
            'view_id': self.env.ref('hr_job_custom.inherit_approval_request_view_form').id,  # Replace with actual view ID
            'res_id': self.env.context.get('active_id'),
            'target': 'main',}
#Karimdad
    def extend_budget_redirect(self):
        context=self.env.context
        requestId=context.get('request')
        request=self.env['crossovered.budget'].browse(requestId)
        
        return request.extend_budget(self.reason)
#Karimdad
#Maaz  
    def stage_job_refuse(self):
        context=self.env.context
        requestId=context.get('request')
        request=self.env['hr.applicant'].browse(requestId)
        
        request.stage_refused_confirm(self.reason, self.refused_by)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant', 
            'view_mode': 'form',
            'view_id': self.env.ref('hr_recruitment.hr_applicant_view_form').id,  # Replace with actual view ID
            'res_id': self.env.context.get('active_id'),
            'target': 'main',}
        
#Maaz  
    
    