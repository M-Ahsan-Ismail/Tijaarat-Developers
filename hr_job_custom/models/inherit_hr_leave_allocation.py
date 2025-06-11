from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class inherit_hr_leave_allocation(models.Model):
    _inherit = 'hr.leave.allocation'

    request_ids = fields.One2many('approval.request', 'allocation_id' ,string='Request', readonly = True)

    allocation_state = fields.Selection([
        ('none','None'),
        ('draft','Draft'),
        ('submit_for_approval', 'Submit for approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Allocation Status", default='draft')


    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Leaves Allocation Approval')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Leaves Allocation Approval',
                'manager_approval':'approver',
                'description':'Leaves Allocation Approval',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':f"Leave Allocation {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'allocation_id':self.id,
            'request_type':'leave_allocation', 
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.allocation_state = "submit_for_approval"
        self.state = "confirm"
        # raise UserError(self.allocation_state)

    def open_related_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Leaves Allocation Approval')],limit=1)
        # raise UserError(approval_category_id)
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('allocation_id','=',self.id),('category_id','=',approval_category_id.id)]
        }
    
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('allocation_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        request_id.request_status = 'cancel'
        self.allocation_state='draft'
        self.state = "draft" 
    
    def onchange_action_approve(self):
        self.state = 'validate'