from odoo import _,api, fields, models
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import simplejson

class InheritHrPayslip(models.Model):
    _inherit='hr.payslip'

    payslip_state = fields.Selection([
        ('none','None'),
        ('draft','Draft'),
        ('submit_for_approval', 'Submit for approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default="draft",string="Request Status",readonly=True )

    request_ids=fields.One2many('approval.request', 'payslip_id', string='Request')
    print_request_ids=fields.One2many('approval.request', 'print_payslip_id', string='Request')
    # COMMENTING THIS FIELD FOR NOW
    # status_request_slip isn't used anywhere in the views or in any of the functions defined in here.
    status_request_slip = fields.Selection([('Waiting for request','Waiting for request'),('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],default='Waiting for request', string="Portal payslip request status")

    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Payslip Approval')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Payslip Approval',
                'manager_approval':'approver',
                'description':'Payslip Approval',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':f"Payslip Approval {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'payslip_id':self.id,
            'request_type':'payslip_approval', 
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.payslip_state = "submit_for_approval"

    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('payslip_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        request_id.request_status = 'cancel'
        self.payslip_state='draft' 


    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('payslip_id','=',self.id)]
        }
    

    @api.onchange('date_from','contract_id','payslip_run_id','struct_id','status_request_slip','worked_days_line_ids','input_line_ids','line_ids','name','has_negative_net_to_report','date','journal_id','move_id')        
    def restrict_at_submitted(self):
        if self.payslip_state =='submit_for_approval':
            raise UserError("Cannot change status until request is approved!")