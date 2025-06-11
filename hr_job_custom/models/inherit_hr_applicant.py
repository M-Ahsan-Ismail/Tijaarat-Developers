from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

import datetime, pytz
class inheritHrJob(models.Model):
    _inherit='hr.applicant'
    
    #Maaz
    reason_for_rejection= fields.Char(string='Reason for rejection')
    #Maaz
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default="draft")
    
    show_submit_Button=fields.Boolean(compute="_check_ShowSubmit")
    request_ids=fields.One2many('approval.request', 'job_application_id', string='Request')
    job_status = fields.Selection(string = 'Job Status', related='job_id.state')

    #Karimdad Start
    applicant_interviewer_ids = fields.One2many('hr.applicant.interviewer','applicant_id', string="Interviewers")
    refused_by = fields.Selection([
        ('candidate', 'Candidate'),
        ('company', 'Company')
    ],string="Refused by")
    #Karimdad End


    #flag fields
    isFirstReason=fields.Boolean(default=True)


    
    def check_is_first_reason(self):
        if self.isFirstReason== True and self.reason_for_rejection and self.refused_by:
            self.isFirstReason = False
            self.reason_for_rejection = self.reason_for_rejection

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('user_id'):
                vals['date_open'] = fields.Datetime.now()
            if vals.get('email_from'):
                vals['email_from'] = vals['email_from'].strip()
            
        
        # raise UserError(self)
        # raise UserError(str([self.job_id.state, self.job_id.website_published]))
        
        applicants = super().create(vals_list)
        applicants.sudo().interviewer_ids._create_recruitment_interviewers()
        # Record creation through calendar, creates the calendar event directly, it will also create the activity.
        if 'default_activity_date_deadline' in self.env.context:
            deadline = fields.Datetime.to_datetime(self.env.context.get('default_activity_date_deadline'))
            category = self.env.ref('hr_recruitment.categ_meet_interview')
            for applicant in applicants:
                partners = applicant.partner_id | applicant.user_id.partner_id | applicant.department_id.manager_id.user_id.partner_id
                self.env['calendar.event'].sudo().with_context(default_applicant_id=applicant.id).create({
                    'applicant_id': applicant.id,
                    'partner_ids': [(6, 0, partners.ids)],
                    'user_id': self.env.uid,
                    'name': applicant.name,
                    'categ_ids': [category.id],
                    'start': deadline,
                    'stop': deadline + relativedelta(minutes=30),
                })
            
        if applicants.job_id.state and applicants.job_id.website_published:
            if applicants.job_id.state == 'approved' and applicants.job_id.website_published == True:
                return applicants
        else:
            raise UserError(str("\nCan't accept applications. Job Position is either not approved or published."))
        

    @api.onchange('create_date')
    def _check_job_status(self):
        if self.job_status != 'approved':
            raise UserError("Can't accept applications. Job Position is not yet approved.")
    
    
    @api.onchange('stage_id')
    def _check_ShowSubmit(self):
        for record in self:
            if record.stage_id.sequence == 3:
                self.show_submit_Button=True
            else:
                self.show_submit_Button=False
    
    
    @api.onchange('stage_id')
    def validateChangeInStage(self):
        if self.state == 'draft' and self.stage_id.name == "Contract Signed":
            raise UserError(str("Can't hire candidates without an approved request!"))
        if self.state == "submit_for_approval":
            raise UserError(str("Can't change the stage. The application has been sent for approval"))
        if self.state == "rejected":
            raise UserError(str("Can't change the stage. The application has been rejected"))
    
    #Maaz    
    @api.onchange('stage_id')
    def approvedChangeStage(self):
        if self.state == "approved" and (self.stage_id.name).lower() in ('initial qualification', 'first interview', 'second interview') :
            raise UserError(str("Stage can't move backward once it is approved."))
        

    def stage_refused_confirm(self,reason,refused_by):
        self.reason_for_rejection = reason
        self.refused_by = refused_by
        self.check_is_first_reason()
        refuse_stage_id= self.env['hr.recruitment.stage'].search([('name','ilike','Candidate Refused')])
        self.stage_id=refuse_stage_id.id
   
    def action_refuse_job_application(self):
    #Maaz 
        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Job Application'),
            'res_model': 'rejection.confirm.reason.wizard',
            'target': 'new',
            'view_id': self.env.ref('hr_job_custom.refuse_stage_reason_view').id,
            'view_mode': 'form',
            'context': {
                "request": self.id,
            }
        } 
    #Maaz           
        
    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Job Applications Approvals')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)

        approvers=[(0,0,{'user_id':admin.id})]
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Job Applications Approvals',
                'manager_approval':'approver',
                'description':'Approval for Job Applications ',
                'approver_ids':approvers,  
            })
        
        request=self.env['approval.request'].create({
            'name':f"{self.name}  ({self.partner_name})",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'job_application_id':self.id,
            'request_type':'JobApplication'
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state="submit_for_approval"

    #this is a deafault function inside the default addons hr.applicant
    def create_employee_from_applicant(self):
        """ Create an employee from applicant """
        self.ensure_one()
        self._check_interviewer_access()
        employee_type = ''
        contact_name = False
        if self.partner_id:
            address_id = self.partner_id.address_get(['contact'])['contact']
            contact_name = self.partner_id.display_name
        else:
            if not self.partner_name:
                raise UserError(_('You must define a Contact Name for this applicant.'))
            new_partner_id = self.env['res.partner'].create({
                'is_company': False,
                'type': 'private',
                'name': self.partner_name,
                'email': self.email_from,
                'phone': self.partner_phone,
                'mobile': self.partner_mobile
            })
            self.partner_id = new_partner_id
            address_id = new_partner_id.address_get(['contact'])['contact']
        
        if self.job_id.employment_type == '3_month_internshio':
            employee_type = 'student'
        elif self.job_id.employment_type == 'permanent_employee':
            employee_type = 'employee'
        elif self.job_id.employment_type in ['emp_with_probabtion', 'consultant']:
            employee_type = 'trainee'

        timezone = pytz.timezone('Asia/Karachi') 

        employee_data = {
            'default_name': self.partner_name or contact_name,
            'default_job_id': self.job_id.id,
            'default_job_title': self.job_id.name,
            'default_address_home_id': address_id,
            'default_department_id': [(6,0,self.department_id.id)],
            'default_address_id': self.company_id.partner_id.id,
            'default_work_email': self.department_id.company_id.email or self.email_from, # To have a valid email address by default
            'default_work_phone': self.department_id.company_id.phone,
            # 'default_employee_type': 'emp_with_probabtion',
            'default_employee_type': employee_type,
            'default_position_type': self.job_id.employment_type,
            'form_view_initial_mode': 'edit',
            'default_applicant_id': self.ids,
            'default_joining_date': datetime.datetime.now(timezone)
        }

        
        
        # raise UserError(str(employee_data))
        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window
        
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('job_application_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.state='draft' 
        
    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('job_application_id','=',self.id)]
        }
        
    @api.onchange('name','partner_name','email_cc','email_from','source_id','partner_phone',
                  'partner_mobile','linkedin_profile','type_id',
                  'interviewer_ids','user_id','priority','medium_id',
                  'categ_ids','job_id','department_id','salary_expected',
                  'salary_proposed','availability','extract_remote_id',
                  'description')
    def ristrict_at_submitted(self):
        if self.state =='submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")
    
    @api.onchange('stage_id')
    def restrict_at_candidate_refused(self):
        refused_stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Candidate Refused')])
        signed_stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Contract Signed')])
        # # raise UserError(str([self.stage_id.id,stage.id]))
        # if self._origin.stage_id.id == refused_stage.id:
        #     raise UserError("This application is now locked as the candidate has refused the offer.")
        #
        # if self._origin.stage_id.id == signed_stage.id:
        #     raise UserError("This application is now locked as the candidate has signed the contract.")



class HrApplicantInterviewer(models.Model):
    _name = 'hr.applicant.interviewer'
    _description = 'HR Applicant Interviewer'

    interviewer_id = fields.Many2one('res.users', string="Interviewer Name", required=True)
    feedback = fields.Text(string="Feedback")
    decision = fields.Selection([
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending')
    ], string="Decision", default='pending', required=True)
    applicant_id = fields.Many2one('hr.applicant', string="Applicant", ondelete='cascade')
