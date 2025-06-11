# from typing_extensions import ReadOnly
from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import datetime

class inheritHrContract(models.Model):
    _inherit = 'hr.contract'
    
    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True) 
    request_ids=fields.One2many('approval.request', 'contract_id', string='Request')
    joining_date=fields.Date(string="Joining Date")
    probation_end_date = fields.Date(string="Probation End Date")
    internship_end_date = fields.Date(string="Internship End Date")
    
    probation_remarks = fields.Text(string="Probation Remarks")
    internship_remarks = fields.Text(string="Internship Remarks")

    extend_internship_probation = fields.Boolean(string='Extend Internship/Probation')
    reason = fields.Char(string='Reason')

    related_employee_type = fields.Selection(related='employee_id.employee_type', string="Employee Type")
    extend_till = fields.Date(string="Extend Till")
    is_probation_end = fields.Boolean(string="Is Probation End", default=False, compute="_compute_period_end",store=True)
    is_internship_end = fields.Boolean(string="Is Internship End", default=False, compute="_compute_period_end",store=True)
    
    # @api.onchange('date_end')
    # def onchange_internship_probation_end(self):
    #     # raise UserError(self.date_end)
    #     # if self.date_start:
    #     #     self.probation_end_date = self.date_start + datetime.datetime.timedelta(days=90)
    #     #     self.internship_end_date = (datetime.datetime.strptime(str(self.date_start), '%Y-%m-%d') + datetime.timedelta(days=90)).strftime('%Y-%m-%d')
    #     if self.date_end:
    #         # raise UserError(self.related_employee_type)
    #         if self.related_employee_type in ['emp_with_probabtion']:
    #             # result = self.write({
    #             #     'probation_end_date': self.date_end
    #             # })
    #             # raise UserError(str(self.probation_end_date))
    #             self.probation_end_date = self.date_end

    #         if self.related_employee_type in ['3_month_internshio']:
    #             self.write({
    #                 'internship_end_date': self.date_end,
    #             })

    @api.model_create_multi
    def create(self, vals_list):
        res = super(inheritHrContract,self).create(vals_list)
        
        if res.date_end:
            if res.related_employee_type == '3_month_internshio':
                res.internship_end_date = res.date_end

            if res.related_employee_type == 'emp_with_probabtion':
                res.probation_end_date = res.date_end
        
        return res
        
    def write(self,vals_list):
        result = super(inheritHrContract,self).write(vals_list)
        # if 'hr_contract.hr_contract_view_form' in self.env.context:
        if result:
            for rec in self:
                if rec.related_employee_type == 'emp_with_probabtion':
                    if 'date_end' in vals_list.keys():
                        rec.probation_end_date = vals_list['date_end']

                    elif 'extend_till' in vals_list.keys():
                        rec.date_end = vals_list['extend_till']
                        rec.probation_end_date = rec.date_end
                        # raise UserError(str([rec.read()]))

                    
                if rec.related_employee_type == '3_month_internshio' and 'date_end' in vals_list.keys():
                    rec.internship_end_date = vals_list['date_end']


    @api.depends('probation_end_date', 'internship_end_date')
    def _compute_period_end(self):
        for rec in self:
            rec.is_probation_end = False
            rec.is_internship_end = False
            if rec.employee_id.employee_type == 'emp_with_probabtion' and rec.probation_end_date:
                if datetime.datetime.today().date() >= rec.probation_end_date:
                    rec.is_probation_end = True
            if rec.employee_id.employee_type == '3_month_internshio' and rec.internship_end_date:
                if datetime.datetime.today().date() >= rec.internship_end_date:
                    rec.is_internship_end = True

        # self.probation_end_date = self.probation_end_date
    @api.depends('extend_till')
    def _update_contract_end_date(self):
        self.date_end = self.extend_till

    def submit_for_contract_approval(self):
        approval_id=self.env['approval.category'].search([('name','=','Contract Approvals')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_id:
            approval_id=self.env['approval.category'].create({
                'name':'Contract Approvals',
                'manager_approval':'approver',
                'description':'Contract Approval requests',
                'approver_ids':approvers,
            })
        # raise UserError(str(qpproval_id.read()))
        request=self.env['approval.request'].create({
            'name':self.employee_id.name,
            'request_owner_id':self.env.uid,
            'category_id':approval_id.id,
            'contract_id':self.id,
            'request_type':'ContractApproval'
            
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.approval_state="submit_for_approval"
        
            
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('contract_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.approval_state='draft'
        request_id.request_status = 'cancel'
        

    def open_related_contract_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Contract Approvals')],limit=1)
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('contract_id','=',self.id),('category_id','=',approval_category_id.id)]
        }
        
        
    # @api.onchange('employee_id','date_start','date_end','structure_type_id','resource_calender_id',
    #               'work_entry_source','department_id','job_id','contract_type_id','hr_responsible_id',
    #               'bonus','wage_type','wage','basic_wage','house_rent','conveyance','utilities',
    #               'mobile_allowance','hardship_allowance','graduality','other','request_fuel_allowance',
    #               'opd_allowance','time_credit','notes','state','resource_calendar_id')
    #
    # def ristrict_at_submitted(self):
    #     if self.approval_state =='submit_for_approval':
    #         raise UserError("Request is submitted for approval cannot change until approved")
        
    