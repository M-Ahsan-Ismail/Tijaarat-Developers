# from typing_extensions import ReadOnly
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)
class inheritHrAppraisalGoal(models.Model):
    _inherit='hr.appraisal.goal'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Status",
        default='draft',
        readonly=True) 
    request_ids=fields.One2many('approval.request', 'goal_id', string='Request')
    
    manager_rating=fields.Selection([
        ('1','(1) Partially Achieved'),
        ('2','(2) Development Needs Identified'),
        ('3','(3) Achieved Expectations'),
        ('4','(4) Exceeded Expectations'),
        ('5','(5) Continuously Exceeded Expectations')
    ],string="Manager's Rating", force_save=True)

    employee_rating=fields.Selection([
        ('1','(1) Partially Achieved'),
        ('2','(2) Development Needs Identified'),
        ('3','(3) Achieved Expectations'),
        ('4','(4) Exceeded Expectations'),
        ('5','(5) Continuously Exceeded Expectations')
    ],string="Employee's Rating", force_save=True)
    
    def get_selection_field_name(self,field, value):
        # This method retrieves the human-readable name for a given stored value
        selection_dict = dict(self._fields[field].selection)
        return selection_dict.get(value, 'None')
    
    def get_selection(self,field):
        selection_dict = dict(self._fields[field].selection)
        if selection_dict:
            return selection_dict
        else:
            return {}
            
    
    
    def submit_for_approval(self):
        approval_id=self.env['approval.category'].search([('name','=','Goal Approvals')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_id:
            approval_id=self.env['approval.category'].create({
                'name':'Goal Approvals',
                'manager_approval':'approver',
                'description':'Goal Approval requests',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':self.name,
            'request_owner_id':self.env.uid,
            'category_id':approval_id.id,
            'goal_id':self.id,
            'request_type':'GoalRequest'
            
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state="submit_for_approval"
        
            

    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('goal_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.state='draft'
        
    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('goal_id','=',self.id)]
        }
        
    @api.onchange('name','employee_id','manager_id','start_date','deadline','goal_type','discription')
    def ristrict_at_submitted(self):
        if self.state =='submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")
        
    def action_confirm(self):
        if self.state !="approved":
            raise UserError("Cant Mark Done until approved")
        else:
            super(inheritHrAppraisalGoal, self).action_confirm()
