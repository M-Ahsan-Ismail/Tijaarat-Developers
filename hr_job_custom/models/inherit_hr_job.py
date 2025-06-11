from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class inheritHrJob(models.Model):
    _inherit='hr.job'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Status",
        default='draft') 
    request_ids=fields.One2many('approval.request', 'job_ids', string='Request')
    
    employment_type=fields.Selection([
        ('3_month_internshio','3 Months Internship'),
        ('permanent_employee','Permanent Employee'),
        ('consultant','Consultant / Freelancer(Part Time)'),
        ('emp_with_probabtion','Employee with Probation (3 Months)')], required=True)

    def submit_for_approval(self):
        approval_id=self.env['approval.category'].search([('name','=','Job Position Approvals')],limit=1)
        ceo=self.env['res.users'].search([('groups_id', 'in', self.env.ref('hr_job_custom.group_ceo').id)], limit=1)
        approvers=[(0,0,{'user_id':ceo.id})]
        
        if not approval_id:
            approval_id=self.env['approval.category'].create({
                'name':'Job Position Approvals',
                'manager_approval':'approver',
                'description':'Approval for Job requests',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':self.name,
            'request_owner_id':self.env.uid,
            'category_id':approval_id.id,
            'job_ids':self.id,
            'request_type':'JobPosition'
            
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state="submit_for_approval"
        
            
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('job_ids','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.state='draft' 
        # self.request_ids.action_cancel()
        # self.state='draft' 
        
    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('job_ids','=',self.id)]
        }
        
    @api.onchange('department_id','address_id','alias_name','contract_type_id','no_of_recruitment','is_published','user_id','interviewer_ids','tag_ids','job_details')
    def ristrict_at_submitted(self):
        if self.state =='submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")
        
    @api.onchange('is_published')
    def ristrict_on_published(self):
        if self.state !="approved" and self.is_published==True:
            raise UserError("Request is not approved cannot change published status")

    @api.onchange('employment_type')
    def onchange_employment_type(self):
        if self.employment_type=='permanent_employee':
            type = self.env['hr.contract.type'].search([('name','=','Permanent')])
            self.contract_type_id = type.id

        elif self.employment_type=='3_month_internshio':
            type = self.env['hr.contract.type'].search([('name','=','3 Months Internship')])
            self.contract_type_id = type.id

        elif self.employment_type=='emp_with_probabtion':
            type = self.env['hr.contract.type'].search([('name','=','3 Months Probation')])
            self.contract_type_id = type.id
        elif self.employment_type=='consultant':
            type = self.env['hr.contract.type'].search([('name','=','BSS Freelancer Contract')])
            self.contract_type_id = type.id
        else:
            self.contract_type_id = False