from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class inheritApprovalRequest(models.Model):
    _inherit = 'approval.request'

    job_ids = fields.Many2one('hr.job', string="Request", readonly=True)
    fuel_id = fields.Many2one('hr.contract', string="Request", readonly=True)
    job_application_id = fields.Many2one('hr.applicant', string="Request", readonly=True)
    goal_id = fields.Many2one('hr.appraisal.goal', string="Request", readonly=True)
    employee_position_id = fields.Many2one('hr.employee', string="Request", readonly=True)
    appraisal_id = fields.Many2one('hr.appraisal', string="Request", readonly=True)
    contract_id = fields.Many2one('hr.contract', string="Request", readonly=True)
    purchaseOrder_id = fields.Many2one('purchase.order', string="Request", readonly=True)
    wfh_request_id = fields.Many2one("wfh_request",string="Request", readonly=True)
    expense_id = fields.Many2one("hr.expense",string="Request", readonly=True)
    payslip_id = fields.Many2one("hr.payslip",string="Request", readonly=True)
    print_payslip_id = fields.Many2one("hr.payslip",string="Request", readonly=True)
    budget_id = fields.Many2one("crossovered.budget",string="Request", readonly=True)
    payment_id = fields.Many2one("account.payment",string="Request", readonly=True)
    # payment_id = fields.Many2one("account.payment",string="Request", readonly=True)
    # purchase_request_id = fields.Many2one('purchase.request', string='Request', required=False)
    # purchase_request_line_id = fields.Many2one('purchase.request.line', string='Request', required=False)

    allocation_id = fields.Many2one('hr.leave.allocation', string='Allocation Reference', required=False)
    
    
    reason_for_rejection = fields.Char(string="Reason For Rejection")
    
    fuel_request_for = fields.Many2one('hr.employee',related='fuel_id.employee_id', string="Fuel Approval Requested For")

    request_type = fields.Selection([
        ('none', 'none'),
        ('JobPosition', 'Job Position Approval'),
        ('JobApplication', 'Job Application Approval'),
        ('EmployeePosition', 'Employee Position Approval'),
        ('payslip_approval', 'Payslip Approval'),
        ('fuel_upgrade_approval', 'Fuel Upgrade Approval'),
        ('salary_slip_portal_approval', 'Salary slip portal Approval'),
        ('expense_approval', 'Expense Approval'),
        ('GoalRequest', 'Goal Approval'),
        ('AppraisalRequest','Appraisal Approval'),
        ('purchaseOrderRequest','Purchase Order Request'),
        ('WFHRequest','WFH Request'),
        ('ContractApproval','Contract Approval'),
        ('BudgetApproval','Budget Approval'),
        ('PaymentApproval1','Payment Approval for Amounts less than or equal to 5000'),
        ('PaymentApproval2','Payment Approval for Amounts less than or equal to 50000 and greater than 5000'),
        ('PaymentApproval3','Payment Approval for Amounts less than or equal to 100000 and greater than 50000'),
        ('PaymentApproval4','Payment Approval for Amounts greater than 100000'),
        ('NonCashPaymentApproval','Payment(Non Cash) Approvals'),
        ('leave_allocation','Leave Allocation'),
        ('PurchaseRequestApproval','Purchase Request Approval'),
        ('PurchaseRequestLineMGRApproval','Purchase Request Line Manager Approval'),
        ('PurchaseRequestLineCTOApproval','Purchase Request Line CTO Approval'),
    ], default="none")

    #Maps the states in the 'request_status' field
    #to the states in the respective approval source models.
    def map_request_status_to_state(self):
        match self.request_status:
            case "pending":
                return 'submit_for_approval'
            
            case "approved":
                return 'approved'
            
            case "refused":
                return 'rejected'
            

    def action_approve(self, approver=None):
        result = super(inheritApprovalRequest, self).action_approve(approver)
        approvers=self.approver_ids
        approved=True
        approved_count = 0
        

        #check how many of the approvers have approved
        for approver in approvers:
            if approver.status =='approved':
                approved_count += 1
            
        #condition block to check if the minimum number of approvals have been obtained
        if approved_count >= self.category_id.approval_minimum:
            approved = True
        elif approved_count < self.category_id.approval_minimum:
            approved = False

        
        if self.request_type == "JobPosition" and approved:
            # raise UserError("inside JobPosition")
            self.job_ids.write({
                'state': self.map_request_status_to_state()
            })
        elif self.request_type == "JobApplication" and approved:
            # stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Contract Signed')])
            
            self.job_application_id.write({

                'state': self.map_request_status_to_state(),
                # 'state': 'approved',
                # 'stage_id': stage
            })
        elif self.request_type == "expense_approval" and approved:
            self.expense_id.write({
                'state': self.map_request_status_to_state(),
                'expense_approval_state': 'approved'
            })
        elif self.request_type == "GoalRequest" and approved:
            self.goal_id.write({
                'state': self.map_request_status_to_state()
            })
        elif self.request_type == "AppraisalRequest" and approved:
            self.appraisal_id.write({
                'approval_state': self.map_request_status_to_state()
            })
        elif self.request_type == "ContractApproval" and approved:
            self.contract_id.write({
                'approval_state': self.map_request_status_to_state()
            })
        elif self.request_type == "purchaseOrderRequest" and approved:
            self.purchaseOrder_id.write({
                'approval_state': self.map_request_status_to_state()
            })
        elif self.request_type == "WFHRequest" and approved:
            self.wfh_request_id.write({
                'state': self.map_request_status_to_state()
            })
            self.wfh_request_id.create_wfh_attendance()
        elif self.request_type == "fuel_upgrade_approval" and approved:
            self.fuel_id.write({
                'fuel_state': self.map_request_status_to_state(),
                'fuel_allowance': self.fuel_id.request_fuel_allowance,
                'request_fuel_allowance': False
            })
        elif self.request_type == "payslip_approval" and approved:
            self.payslip_id.write({
                'payslip_state': self.map_request_status_to_state()
            })
        elif self.request_type=="salary_slip_portal_approval":
            self.print_payslip_id.write({
                'status_request_slip': 'Approved',
            })
        elif self.request_type == "EmployeePosition" and approved:
            self.employee_position_id.action_approve()
        elif self.request_type == "BudgetApproval" and approved:
            self.budget_id.write({'approval_state': self.map_request_status_to_state(), 'budget_state': 'approved'})
        elif self.request_type == "PaymentApproval1" and approved:
            self.payment_id.write({'approval_state': self.map_request_status_to_state()})
                                   # 'state': 'posted'})
        elif self.request_type == "PaymentApproval2" and approved:
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'posted'})        
        elif self.request_type == "PaymentApproval3" and approved:
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'posted'})     
        elif self.request_type == "PaymentApproval4" and approved:
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'posted'})   
        elif self.request_type == "NonCashPaymentApproval" and approved:
            self.payment_id.write({'approval_state': self.map_request_status_to_state()}) 
        # elif self.request_type == "PurchaseRequestApproval" and approved:
        #     self.purchase_request_id.write({'approval_state': 'approved',
        #                            'state': 'approved'})
        # elif self.request_type == "PurchaseRequestLineMGRApproval" and approved:
        #     if self.purchase_request_line_id.line_state == 'to_approve_mgr':
        #         if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
        #             self.purchase_request_line_id.write({'approval_state': 'manager_approved', 'line_state': 'manager_approved', 'request_state': 'approved'})
        #         else:
        #             raise UserError("This request can only be processed by the Purchase Request Manager.\nYou are not authorized to process this.")
        # elif self.request_type == "PurchaseRequestLineCTOApproval" and approved:
        #     if self.purchase_request_line_id.line_state == 'to_approve_cto':
        #         if self.env.user.has_group('recruitment_states_validation.group_CTO'):
        #             self.purchase_request_line_id.write({'approval_state': 'cto_approved', 'line_state': 'cto_approved', 'request_state': 'approved'})
        #         else:
        #             raise UserError("This request can only be processed by the CTO.\nYou are not authorized to process this.")
        #addad by SAKA
        elif self.request_type == "leave_allocation" and approved:
            self.allocation_id.write({'allocation_state': self.map_request_status_to_state(),
                                      'state':'validate'})
            

        return result
    
    def action_refuse(self, approvers=None):

        return {
            'type': 'ir.actions.act_window',
            'name': _('Reject Job Position'),
            'res_model': 'rejection.confirm.reason.wizard',
            'target': 'new',
            'view_id': self.env.ref('hr_job_custom.rejection_confirm_wizard_view').id,
            'view_mode': 'form',
            'context': {
                "request": self.id,
            }
        }

    def action_refused_confirm(self, reason):
        self.reason_for_rejection = reason
        result = super(inheritApprovalRequest, self).action_refuse()
        if self.request_type == "JobPosition":
            self.job_ids.write({
                'state': 'rejected',
                'active': False
            })
        elif self.request_type == "JobApplication":
            stage = self.env['hr.recruitment.stage'].search(
                [('name', '=', 'Refused')])
            
            self.job_application_id.write({

                'state': 'rejected',
                'stage_id': stage
            })
        elif self.request_type == "expense_approval":
            self.request_status = 'refused'
            self.expense_id.write({
                'state': 'refused',
                'expense_approval_state': 'rejected'
            })
        elif self.request_type == "EmployeePosition":
            self.employee_position_id.write({
                'state': 'rejected',
                'change_position': False
            })
        elif self.request_type == "GoalRequest":
            self.goal_id.write({
                'state': 'rejected',
            })
        elif self.request_type == "AppraisalRequest":
            self.appraisal_id.write({
                'approval_state': 'rejected',
            })
        elif self.request_type == "ContractApproval":
            
            self.contract_id.write({
                'approval_state': 'rejected',
                'state': 'cancel'
            })
        elif self.request_type == "WFHRequest":
            self.wfh_request_id.write({
                'state': 'rejected',
            })
        elif self.request_type == "fuel_upgrade_approval":
            self.fuel_id.write({
                'fuel_state': 'rejected',
                'request_fuel_allowance': False
            })
        elif self.request_type == "payslip_approval":
            self.payslip_id.write({
                'payslip_state': 'rejected'
            })
        elif self.request_type=="salary_slip_portal_approval":
            self.print_payslip_id.write({
                'status_request_slip': 'Rejected'
            })
        elif self.request_type == "purchaseOrderRequest":
            self.purchaseOrder_id.write({
                'approval_state': 'rejected',
            })
        
        elif self.request_type == "BudgetApproval":
            # self.budget_id.write({'state': 'approved', 'approval_state': 'approved'})
            self.budget_id.write({'approval_state': 'rejected', 'budget_state':'rejected', 'state': 'cancel'})
        
        elif self.request_type == "PaymentApproval1":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
            
        elif self.request_type == "PaymentApproval2":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
            
        elif self.request_type == "PaymentApproval3":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
        
        elif self.request_type == "PaymentApproval4":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
        elif self.request_type == "NonCashPaymentApproval":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
        # elif self.request_type == "PurchaseRequestApproval":
        #     self.purchase_request_id.write({'approval_state': 'rejected',
        #                            'state': 'rejected'})
        #
        # elif self.request_type == "PurchaseRequestLineMGRApproval":
        #     if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the Purchase Request Manager.\nYou are not authorized to process this.")
        #
        # elif self.request_type == "PurchaseRequestLineCTOApproval":
        #     if self.env.user.has_group('recruitment_states_validation.group_CTO'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the CTO.\nYou are not authorized to process this.")
            
        #added by SAKA
        elif self.request_type == "leave_allocation":
            self.allocation_id.write({'allocation_state':'rejected',
                                      'state':'refuse'})

        return result

    def action_cancel(self):

        result = super(inheritApprovalRequest, self).action_cancel()
        if self.request_type == "JobPosition":
            self.job_ids.write({
                'state': 'rejected',
            })
            # self.job_ids.toggle_active()
        elif self.request_type == "JobApplication":
            stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Refused')])
            self.job_application_id.write({
                'state': 'rejected',
                'stage_id': stage
            })
        elif self.request_type == "EmployeePosition":
            self.employee_position_id.write({
                'state': 'rejected',
            })
        elif self.request_type == "GoalRequest":
            self.goal_id.write({
                'state': 'rejected',
            })
        elif self.request_type == "AppraisalRequest":
            self.appraisal_id.write({
                'approval_state': 'rejected',
            })
        elif self.request_type == "ContractApproval":
            self.contract_id.write({
                'approval_state': 'rejected',
                'state': 'close'
            })
        elif self.request_type == "WFHRequest":
            self.wfh_request_id.write({
                'state': 'rejected',
            })
        elif self.request_type == "purchaseOrderRequest":
            self.purchaseOrder_id.write({
                'approval_state': 'rejected',
            })
        elif self.request_type == "fuel_upgrade_approval":
            self.fuel_id.write({
                'fuel_state': 'rejected',
                'request_fuel_allowance': False
            })
        elif self.request_type == "expense_approval":
            self.expense_id.write({
                'expense_approval_state': 'cancel'
            })
        elif self.request_type == "BudgetApproval":
            # self.budget_id.write({'state': 'approved', 'approval_state': 'approved'})
            self.budget_id.write({'approval_state': 'rejected', 'budget_state':'rejected'})
        
        elif self.request_type == "PaymentApproval1":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
            
        elif self.request_type == "PaymentApproval2":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
            
        elif self.request_type == "PaymentApproval3":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
        
        elif self.request_type == "PaymentApproval4":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})
        
        elif self.request_type == "NonCashPaymentApproval":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'cancel'})

        # elif self.request_type == "PurchaseRequestApproval":
        #     self.purchase_request_id.write({'approval_state': 'rejected',
        #                            'state': 'rejected'})
        #
        # elif self.request_type == "PurchaseRequestLineMGRApproval":
        #     if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the Purchase Request Manager.\nYou are not authorized to process this.")
        #
        # elif self.request_type == "PurchaseRequestLineCTOApproval":
        #     if self.env.user.has_group('recruitment_states_validation.group_CTO'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the CTO.\nYou are not authorized to process this.")

        #added by SAKA
        elif self.request_type == "leave_allocation":
            self.allocation_id.write({'allocation_state': 'rejected',
                                      'state':'cancel'})

        return result

    def action_draft(self):
        result = super(inheritApprovalRequest, self).action_draft()
        if self.request_type == "JobPosition":
            self.job_ids.write({
                'state': 'draft'
            })
        elif self.request_type == "JobApplication":
            self.job_application_id.write({
                'state': 'draft'

            })
        elif self.request_type == "EmployeePosition":
            self.employee_position_id.write({
                'state': 'draft',
            })
        elif self.request_type == "GoalRequest":
            self.goal_id.write({
                'state': 'draft',
            })
        elif self.request_type == "AppraisalRequest":
            self.appraisal_id.write({
                'approval_state': 'draft',
            })
        elif self.request_type == "ContractApproval":
            self.contract_id.write({
                'approval_state': 'draft',
            })
        elif self.request_type == "WFHRequest":
            self.wfh_request_id.write({
                'state': 'draft',
            })
        elif self.request_type == "purchaseOrderRequest":
            self.purchaseOrder_id.write({
                'approval_state': 'draft',
            })
        
        elif self.request_type == "BudgetApproval":
            # self.budget_id.write({'state': 'approved', 'approval_state': 'approved'})
            self.budget_id.write({'approval_state': 'draft'})

        elif self.request_type == "PaymentApproval1":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})
            
        elif self.request_type == "PaymentApproval2":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})
            
        elif self.request_type == "PaymentApproval3":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})
        
        elif self.request_type == "PaymentApproval4":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})
        
        elif self.request_type == "NonCashPaymentApproval":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})
            
        # elif self.request_type == "PurchaseRequestApproval":
        #     self.purchase_request_id.write({'approval_state': 'draft',
        #                            'state': 'draft'})
        #
        # elif self.request_type == "PurchaseRequestLineMGRApproval":
        #     if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the Purchase Request Manager.\nYou are not authorized to process this.")
        #
        # elif self.request_type == "PurchaseRequestLineCTOApproval":
        #     if self.env.user.has_group('recruitment_states_validation.group_CTO'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the CTO.\nYou are not authorized to process this.")
            
        #added by SAKA
        elif self.request_type == "leave_allocation":
            self.allocation_id.write({'allocation_state': 'draft',
                                      'state':'draft'})

        return result
    
    def action_withdraw(self):
        result = super(inheritApprovalRequest, self).action_withdraw()
        if self.request_type == "JobPosition":
            self.request_status = 'cancel'
            self.job_ids.write({
                'state': 'draft'
            })
        elif self.request_type == "JobApplication":
            stage = self.env['hr.recruitment.stage'].search([('name', '=', 'Shortlisted')])
            self.job_application_id.write({
                'state': 'submit_for_approval',
                'stage_id': stage
            })
        elif self.request_type == "EmployeePosition":
            self.employee_position_id.write({
                'state': 'draft',
            })
        elif self.request_type == "GoalRequest":
            self.goal_id.write({
                'state': 'draft',
            })
        elif self.request_type == "AppraisalRequest":
            self.appraisal_id.write({
                'approval_state': 'draft',
            })
        elif self.request_type == "ContractApproval":
            # self.contract_id.write({
            #     'approval_state': 'draft',
            # })
            self.contract_id.action_withdraw()
        elif self.request_type == "fuel_upgrade_approval":
            # self.fuel_id.write({
            #     'fuel_state': 'draft'
            # })
            self.fuel_id.action_withdraw_fuel()
        elif self.request_type == "payslip_approval":
            self.payslip_id.action_withdraw()
        elif self.request_type == "expense_approval":
            self.request_status = 'cancel'
            self.expense_id.write({
                'state': 'draft',
                'expense_approval_state': 'draft'
            })
        elif self.request_type == "WFHRequest":
            self.wfh_request_id.write({
                'state': 'draft',
            })
        elif self.request_type == "purchaseOrderRequest":
            self.purchaseOrder_id.write({
                'approval_state': 'draft',
            })
        elif self.request_type == "BudgetApproval":
            # self.budget_id.write({'state': 'approved', 'approval_state': 'approved'})
            self.budget_id.write({'approval_state': 'draft', 'budget_state': 'draft'})
            self.request_status = 'cancel'
        elif self.request_type == "PaymentApproval1":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})           
        elif self.request_type == "PaymentApproval2":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})         
        elif self.request_type == "PaymentApproval3":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})    
        elif self.request_type == "PaymentApproval4":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})   
        elif self.request_type == "NonCashPaymentApproval":
            self.payment_id.write({'approval_state': self.map_request_status_to_state(),
                                   'state': 'draft'})     
        # elif self.request_type == "PurchaseRequestApproval":
        #     self.purchase_request_id.write({'approval_state': 'draft',
        #                            'state': 'draft'})
        # elif self.request_type == "PurchaseRequestLineMGRApproval":
        #     if self.env.user.has_group('purchase_request.group_purchase_request_manager'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the Purchase Request Manager.\nYou are not authorized to process this.")
        # elif self.request_type == "PurchaseRequestLineCTOApproval":
        #     if self.env.user.has_group('recruitment_states_validation.group_CTO'):
        #         self.purchase_request_line_id.write({'approval_state': 'draft', 'line_state': 'draft', 'request_state': 'draft'})
        #     else:
        #         raise UserError("This request can only be processed by the CTO.\nYou are not authorized to process this.")
        #added by SAKA 
        elif self.request_type == "leave_allocation":
            self.request_status = 'cancel'
            self.allocation_id.write({'allocation_state': 'draft',
                                      'state':'draft'})
            
        return result

    def open_related_hr_job(self):
        return {
            'name': 'Related HR Job',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.job',
            'res_id': self.job_ids.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr.view_hr_job_form').id,
            'target': 'current',
        }

    def open_related_hr_applicant(self):
        return {
            'name': 'Related HR Applicant',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant',
            'res_id': self.job_application_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_recruitment.hr_applicant_view_form').id,
            'target': 'current',
        }
    
    # def open_related_hr_applicant(self):
    #     """Added By SAKA"""
    #     return {
    #         'name': 'Related HR Leave',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.leave.allocation',
    #         'res_id': self.allocation_id.id,
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('hr_leave_allocation.hr_holidays.hr_leave_allocation_view_form_manager').id,
    #         'target': 'current',
    #     }

    def open_related_employee(self):
        return {
            'name': 'Related HR Employee',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'res_id': self.employee_position_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr.view_employee_form').id,
            'target': 'current',
        }
    def open_related_goal(self):
        return {
            'name': 'Related Goal',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal.goal',
            'res_id': self.goal_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_appraisal.hr_appraisal_goal_view_form').id,
            'target': 'current',
        }
    def open_related_appraisal(self):
        return {
            'name': 'Related Appraisal',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal',
            'res_id': self.appraisal_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_appraisal.view_hr_appraisal_form').id,
            'target': 'current',
        }
    def open_related_contract(self):
        return {
            'name': 'Related Contract',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract',
            'res_id': self.contract_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,
            'target': 'current',
        }
    def open_related_purchaseOrder(self):
        return {
            'name': 'Related PO',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': self.purchaseOrder_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('purchase.purchase_order_form').id,
            'target': 'current',
        }
    def open_related_WFH_request(self):
        return {
            'name': 'Related WFH Request',
            'type': 'ir.actions.act_window',
            'res_model': 'wfh_request',
            'res_id': self.wfh_request_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('wfh_request.view_wfh_request_form').id,
            'target': 'current',
        }
    
    def open_related_fuel(self):
        return {
            'name': 'Related Fuel',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract',
            'res_id': self.fuel_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,
            'target': 'current',
        }

    def open_related_budget(self):
        return {
            'name': 'Related Budget',
            'type': 'ir.actions.act_window',
            'res_model': 'crossovered.budget',
            'res_id': self.budget_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('account_budget.crossovered_budget_view_form').id,
            'target': 'current',
        }
    
    def open_related_payment(self):
        return {
            'name': 'Related Payment',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'res_id': self.payment_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'target': 'current',
        }
    
    def open_related_allocation(self):
        return {
            'name': 'Related Allocation',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.allocation',
            'res_id': self.allocation_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_holidays.hr_leave_allocation_view_form_manager').id,
            'target': 'current',
        }
    
    def open_related_payslip(self):
        return {
            'name': 'Related Payslip',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'res_id': self.payslip_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('hr_payroll.view_hr_payslip_form').id,
            'target': 'current',
        }

    # def open_related_purchase_request(self):
    #     return {
    #         'name': 'Related PR',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.request',
    #         'res_id': self.purchase_request_id.id,
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('purchase_request.view_purchase_request_form').id,
    #         'target': 'current',
    #     }
    # def open_related_purchase_request_line(self):
    #     return {
    #         'name': 'Related PR Line',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'purchase.request.line',
    #         'res_id': self.purchase_request_line_id.id,
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('purchase_request.purchase_request_line_form').id,
    #         'target': 'current',
    #     }
class inheritApprovalCategory(models.Model):
    _inherit = 'approval.category'

    id_char = fields.Char(string='Unique String ID')
    minimum_approval_amount = fields.Float(string="Minimum Approval Amount", help="The minimum amount for which this approval will be triggered")

    show_minimum_approval_amount = fields.Boolean(string="Show Minimum Approval Amount", default=False, compute='_compute_minimum_approval_amount')

    @api.depends('name')
    def _compute_minimum_approval_amount(self):
        self.show_minimum_approval_amount = False
        # raise UserError(str([self.name, self.name.lower()]))
        if self.name and 'purchase order' in self.name.lower():
            self.show_minimum_approval_amount = True
        else:
            self.show_minimum_approval_amount = False