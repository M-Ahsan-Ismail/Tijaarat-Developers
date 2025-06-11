from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

import math
import datetime

import logging
_logger = logging.getLogger(__name__)

class inheritHrEmployee(models.Model):
    _inherit='hr.employee'
    request_ids=fields.One2many('approval.request', 'employee_position_id', string='Request')
    # employee_type= fields.Selection(selection_add=[
    #     ('3_month_internshio','3 Month Internship'),
    #     ('permanent_employee','Permanent Employee'),
    #     ('consultant','Consultant / Freelancers (Part Time)'),
    #     ('emp_with_probabtion','Employee with Probation (3 months)'),
    #                                                ])
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default="draft")

    
    change_position=fields.Selection([
        ('3_month_internshio','3 Months Intership'),
        ('permanent_employee','Permanent Employee'),
        ('consultant','Consultant / Freelancer(Part Time)'),
        ('emp_with_probabtion','Employee with Probation (3 Months)')
    ],string="Change Position")
    show_submit_button=fields.Boolean(default=False,compute='_compute_show_submit',string="show submit button")
    
    purchaseOrder_id = fields.One2many('purchase.order','purchasingEmployee',string="Purchase Orders")
    isNewEmployee = fields.Boolean("Is Employee",default=True)
    related_position_type = fields.Selection(related="position_type",string='Related Position Type',store=True)

    job_description = fields.Text(string="Job Description")
    id_card_number = fields.Char(string="ID Card")

    joining_date = fields.Date(string="Joining Date")

    bonus_type = fields.Many2many('hr.payroll.structure',string="Bonus Type",domain="[('type_id.name', '=', 'Bonus')]")
    
    last_allocation_month = fields.Integer(string="Last Allocation Month")
    
    @api.depends('related_position_type')
    def onchange_position_type(self):
        for rec in self:
            # raise UserError(str([self.related_position_type,self.isNewEmployee]))
            if rec.isNewEmployee == True and rec.position_type:
                # raise UserError(str('ehre'))s

                rec.isNewEmployee = False
                rec.position_type = rec.position_type
                rec.employee_type = rec.position_type
            # raise UserError(self.isNewEmployee)
            if rec.position_type == 'permanent_employee':
                rec.create_default_allocations_onchange()
    

    def create_default_allocations_onchange(self):
        leave_types = self.env['hr.leave.type'].search(['|','|',('is_casual','=',True),('is_annual','=',True),('is_sick','=',True)])
        
        entry = {
                    'holiday_type': 'employee',
                    'name': 'test',
                    'holiday_status_id': False,
                    'allocation_type': 'regular',
                    'accrual_plan_id': False,
                    'date_from': self.joining_date,
                    'date_to': False,
                    'number_of_days': False,
                    'number_of_days_display': False,
                    'employee_id': self.id,
                    'category_id': False,
                    'multi_employee': False,
                    'employee_ids': [
                        [
                            6,
                            False,
                            [
                                self.id
                            ]
                        ]
                    ],
                    'department_id': self.department_id.id if self.department_id else False,  # Ensure department_id is set correctly
                    'mode_company_id': False,
                    'notes': False,
                    'lastcall': False,
                    'allocation_state': 'approved',
                }

        entry_list = []
        if self.position_type == 'permanent_employee':

            if not self.joining_date:
                raise UserError('Kindly enter joining date')
                
            elif self.joining_date.month == 1:
                for leave_type in leave_types:
                    new_entry = entry.copy()  # Create a new dictionary for each iteration
                    new_entry['holiday_status_id'] = leave_type.id
                    new_entry['number_of_days'] = float(leave_type.max_allowed)
                    entry_list.append(new_entry)
            elif 1 < self.joining_date.month < 7:
                for leave_type in leave_types:
                    new_entry = entry.copy()  # Create a new dictionary for each iteration
                    _logger.info(f"Leave Type: {leave_type.name}")
                    new_entry['holiday_status_id'] = leave_type.id

                    days_in_year = 365 if (self.joining_date.year % 4 == 0 and (self.joining_date.year % 100 != 0 or self.joining_date.year % 400 == 0)) else 366
                    joining_datetime = datetime.datetime(self.joining_date.year, self.joining_date.month, self.joining_date.day)
                    days_from_start_of_year = (joining_datetime - datetime.datetime(self.joining_date.year, 1, 1)).days
                    allowed_days = (float(leave_type.max_allowed) / days_in_year) * (days_in_year - days_from_start_of_year)

                    new_entry['number_of_days'] = round(allowed_days)
                    new_entry['name'] = f"{leave_type.name} for {self.name}",
                    entry_list.append(new_entry)
            else:
                for leave_type in leave_types:
                    if 'Jan' in leave_type.name:
                        continue
                    new_entry = entry.copy()  # Create a new dictionary for each iteration
                    _logger.info(f"Leave Type: {leave_type.name}")
                    new_entry['holiday_status_id'] = leave_type.id
                    
                    days_in_year = 365 if (self.joining_date.year % 4 == 0 and (self.joining_date.year % 100 != 0 or self.joining_date.year % 400 == 0)) else 366
                    joining_datetime = datetime.datetime(self.joining_date.year, self.joining_date.month, self.joining_date.day)
                    days_from_start_of_year = (joining_datetime - datetime.datetime(self.joining_date.year, 1, 1)).days
                    allowed_days = (float(leave_type.max_allowed) / days_in_year) * (days_in_year - days_from_start_of_year)

                    new_entry['number_of_days'] = round(allowed_days)
                    entry_list.append(new_entry)

        for i in entry_list:
            result = self.env['hr.leave.allocation'].create(i)
            result.onchange_action_approve()
            result = False

    
    def create_default_allocations(self, res):
        leave_types = self.env['hr.leave.type'].search(['|','|',('is_casual','=',True),('is_annual','=',True),('is_sick','=',True)])
        
        # raise UserError(str([res.employee_type, res.position_type]))
        entry = {
                    'holiday_type': 'employee',
                    'name': 'test',
                    'holiday_status_id': False,
                    'allocation_type': 'regular',
                    'accrual_plan_id': False,
                    'date_from': res.joining_date,
                    'date_to': False,
                    'number_of_days': False,
                    'number_of_days_display': False,
                    'employee_id': res.id,
                    'category_id': False,
                    'multi_employee': False,
                    'employee_ids': [
                        [
                            6,
                            False,
                            [
                                res.id
                            ]
                        ]
                    ],
                    'department_id': res.department_id,
                    'mode_company_id': False,
                    'notes': False,
                    'lastcall': False,
                    'allocation_state': 'approved'
                }

        entry_list = []


        if not res.joining_date:
            raise UserError('Kindly enter joining date')
        
        if res.employee_type == '3_month_internshio' or res.position_type == '3_month_internshio':
            
            casual_leave_type = self.env['hr.leave.type'].search([('is_casual','=',True)])

            #handle different months for date_to
            today = res.joining_date
            next_month = today.replace(day=1) + datetime.timedelta(days=32)
            if today.month == 12:  # Handle December
                next_month = next_month.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = next_month.replace(day=1)
                if today.month == 2:  # Handle February
                    if (today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0)):  # Leap year
                        next_month = next_month.replace(month=2, day=29)
                    else:
                        next_month = next_month.replace(month=2, day=28)
                else:
                    next_month = next_month.replace(month=today.month + 1)
            
            
            
            entry = {
                        'holiday_type': 'employee',
                        'name': f"{casual_leave_type.name} for {res.name}",
                        'holiday_status_id': casual_leave_type.id,
                        'allocation_type': 'regular',
                        'accrual_plan_id': False,
                        'date_from': today,
                        'date_to': next_month,
                        'number_of_days': 1,
                        'number_of_days_display': False,
                        'employee_id': res.id,
                        'category_id': False,
                        'multi_employee': False,
                        'employee_ids': [
                            [
                                6,
                                False,
                                [
                                    res.id
                                ]
                            ]
                        ],
                        'department_id': res.department_id,
                        'mode_company_id': False,
                        'notes': False,
                        'lastcall': False,
                        'allocation_state': 'approved'
                    }
            res.last_allocation_month = today.month
            created_entry = self.env['hr.leave.allocation'].create(entry)
            created_entry.onchange_action_approve()
            
        if entry_list:
            for i in entry_list:
                result = self.env['hr.leave.allocation'].create(i)
                result.onchange_action_approve()
                result = False



    @api.model    
    def create(self, vals_list):
        res = super(inheritHrEmployee,self).create(vals_list)
        # self.create_default_allocations(res)
        return res
    
    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Change Employee Position Approvals')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)

        approvers=[(0,0,{'user_id':admin.id})]
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Change Employee Position Approvals',
                'manager_approval':'approver',
                'description':'Change Employee Job Position Approvals',
                'approver_ids':approvers,  
            })
        
        request=self.env['approval.request'].create({
            'name':f"{dict(self._fields['position_type'].selection).get(self.position_type)} to {dict(self._fields['change_position'].selection).get(self.change_position)} for {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'employee_position_id':self.id,
            'request_type':'EmployeePosition'
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state="submit_for_approval"
        
    @api.onchange('change_position')
    def _compute_show_submit(self):
        if self.change_position == self.position_type or not self.change_position:
            self.show_submit_button=False
        else:
            self.show_submit_button=True
        if self.state != "submit_for_approval":
            self.state="draft"
            
    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('employee_position_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.state='draft' 
        # self.approval_state='draft' 
        # for request in self.request_ids:
        #     request.action_cancel()
        # self.state='draft' 
        
    def action_approve(self):
        self.position_type = self.change_position
        self.employee_type = self.change_position

        # if self.change_position == '3_month_internshio':
        #     self.employee_type = 'student'
        # elif self.change_position == 'permanent_employee':
        #     self.employee_type = 'employee'
        # elif self.change_position in ['emp_with_probabtion', 'consultant']:
        #     self.employee_type = 'trainee'
        
        
        self.change_position=False
        self.state='approved'
        
        
    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('employee_position_id','=',self.id)]
        }

    # def action_open_contracts(self):
    #     self.ensure_one()
    #     action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
    #     action['res_id'] = self.id
    #     raise UserError(str(action))
        # return action
    
    def action_open_contracts(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
        action['res_id'] = self.id
        
        # action = super(inheritHrEmployee,self).action_open_contract_history()
        return action
    
    def action_open_contracts_123(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form')
        action['res_id'] = self.id
        
        # action = super(inheritHrEmployee,self).action_open_contract_history()
        # raise UserError(str(action))
        return action
    
    # contracts_button = fields.Many2one('ir.actions.actions', string="Contracts", compute='_compute_contracts_button')
    
    # def _compute_contracts_button(self):
    #     for record in self:
    #         record.contracts_button = self.env.ref('hr_contract.hr_contract_history_view_form').id

    def action_open_contract_history(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
        action['res_id'] = self.id
        return action

class ContractHistoryExtension(models.Model):
    _inherit = 'hr.contract.history'

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Reference contract is the one with the latest start_date.
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
            WITH contract_information AS (
                SELECT DISTINCT employee_id,
                                company_id,
                                FIRST_VALUE(id) OVER w_partition AS id,
                                MAX(CASE
                                    WHEN state='open' THEN 1
                                    WHEN state='draft' AND kanban_state='done' THEN 1
                                    ELSE 0 END) OVER w_partition AS is_under_contract
                FROM   hr_contract AS contract
                WHERE  contract.active = true
                WINDOW w_partition AS (
                    PARTITION BY contract.employee_id, contract.company_id
                    ORDER BY
                        CASE
                            WHEN contract.state = 'open' THEN 0
                            WHEN contract.state = 'draft' THEN 1
                            WHEN contract.state = 'close' THEN 2
                            WHEN contract.state = 'cancel' THEN 3
                            ELSE 4 END,
                        contract.date_start DESC
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                )
            )
            SELECT DISTINCT employee.id AS id,
                            employee.id AS employee_id,
                            employee.active AS active_employee,
                            contract.id AS contract_id,
                            contract_information.is_under_contract::bool AS is_under_contract,
                            employee.first_contract_date AS date_hired,
                            %s
            FROM       hr_contract AS contract
            INNER JOIN contract_information ON contract.id = contract_information.id
            RIGHT JOIN hr_employee AS employee
                ON  contract_information.employee_id = employee.id
                AND contract.company_id = employee.company_id
            WHERE   employee.employee_type IN ('employee', 'student', 'trainee','3_month_internshio','permanent_employee','emp_with_probabtion', 'consultant')
        )""" % (self._table, self._get_fields()))
