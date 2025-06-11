from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import datetime

class inheritWFHRequest(models.Model):
    _inherit='wfh_request'
    request_ids=fields.One2many('approval.request', 'wfh_request_id', string='Request')
    
    state = fields.Selection([
        ('draft', 'New'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default="draft")
    
    
    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','WFH Request Approvals')],limit=1)
        admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_system').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'WFH Request Approvals',
                'manager_approval':'approver',
                'description':'WFH Request Approvals',
                'approver_ids':approvers,  
            })
        
        request=self.env['approval.request'].create({
            'name':self.employee_name.name,
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'wfh_request_id':self.id,
            'request_type':'WFHRequest'
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state="submit_for_approval"
        
        #   self.state="draft"
            
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('wfh_request_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.state='draft' 
        # for request in self.request_ids:
        #     request.action_cancel()
        # self.state='draft' 
        
    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('wfh_request_id','=',self.id)]
        }

    def create_wfh_attendance(self):
        morning_time_from = datetime.time(4,0,0)
        morning_time_to = datetime.time(13,0,0)
        
        evening_time_from = datetime.time(8,0,0)
        evening_time_to = datetime.time(17,0,0)

        new_entry = {
            'employee_id': self.employee_name.id,
            'check_in': False,
            'check_out': False,
            'is_wfh': True,
            'wfh_reason': self.reason
            }
        
        wfh_start_date = self.from_date.date()
        wfh_end_date = self.to_date.date()
        if 'Morning' in self.employee_name.resource_calendar_id.name:
            iter = wfh_start_date
            
            while iter <= wfh_end_date:
                morning_leave_date_from = datetime.datetime.combine(iter, morning_time_from)
                morning_leave_date_to = datetime.datetime.combine(iter, morning_time_to)
                new_entry['check_in'] = morning_leave_date_from
                new_entry['check_out'] = morning_leave_date_to
                # raise UserError(str(new_entry))
                
                self.env['hr.attendance'].create(new_entry)
                iter += datetime.timedelta(days=1)

        elif 'Evening' in self.employee_name.resource_calendar_id.name:
            iter = wfh_start_date
            while iter <= wfh_end_date:
                evening_leave_date_from = datetime.datetime.combine(iter, evening_time_from)
                evening_leave_date_to = datetime.datetime.combine(iter, evening_time_to)

                new_entry['check_in'] = evening_leave_date_from
                new_entry['check_out'] = evening_leave_date_to
                
                self.env['hr.attendance'].create(new_entry)
                iter += datetime.timedelta(days=1)

    
    
    @api.onchange('employee_name','from_date','duration','to_date','reason','description')
    def ristrict_at_submitted(self):
        if self.state =='submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")
            
    

# class TestAttendance(models.Model):
#     _inherit='hr.attendance'

#     @api.model_create_multi
#     def create(self, vals_list):
#         res = super().create(vals_list)
#         raise UserError(str(vals_list))
#         res._update_overtime()
#         return res

