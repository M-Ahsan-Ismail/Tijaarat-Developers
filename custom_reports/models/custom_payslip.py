
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class GroupAging(models.Model):
    _inherit = 'hr.payslip'
    basic_salary = fields.Float(string='Basic salary from lines', tracking=True, compute='_compute_values', default='0.0')
    bonus = fields.Float(string='bonus from lines', tracking=True, default='0.0')
    eobi_d = fields.Float(string='eobi from lines', tracking=True,  compute='_compute_values', default='0.0')
    loan_d = fields.Float(string='loan from lines', tracking=True,  compute='_compute_values', default='0.0')
    health_d = fields.Float(string='health from lines', tracking=True, default='0.0')
    leave_d = fields.Float(string='leave from lines', tracking=True, compute='_compute_values', default='0.0')
    income_tax_d = fields.Float(string='income tax from lines', tracking=True, compute='_compute_values', default='0.0')
    other_d = fields.Float(string='other deductions from lines', tracking=True, default='0.0')
    gross = fields.Float(string='gross salary from lines', tracking=True, compute='_compute_values', default='0.0')
    net_salary = fields.Float(string='net salary from lines', tracking=True, compute='_compute_values')
    fuel_allowance=fields.Char(string="Fuel Allowance",compute='_compute_allowance')
    gym=fields.Char(string="Gym",compute='_check_employee_type')
    insurance=fields.Char(string="Insurance",compute='_check_employee_type')
    
    
    api.onchange('employee_id')
    def _compute_allowance(self):
        for rec in self:
            contract=self.env['hr.contract'].search([('state','in', ['open']),('employee_id','=',rec.employee_id.id)])
            if contract and contract.fuel_allowance:
                rec.fuel_allowance=contract.fuel_allowance
            else:
                rec.fuel_allowance=" "
                
    api.onchange('employee_id')
    def _check_employee_type(self):
        for rec in self:
            if rec.employee_id.position_type=='permanent_employee':
                rec.gym="Yes"
                rec.insurance="Yes"
            else:
                rec.gym="NA"
                rec.insurance="NA"

    def print_report(self):
        return self.env.ref('custom_reports.custom_payslip_report').report_action(self.id)

    @api.model
    def get_month(self):
        # Get the current date in the desired format
        if self.date:
            month = self.date.strftime('%B %Y')
            return month
        else:
            month = self.date_to.strftime('%B %Y')
            return month
        
    def action_print_batch_payslip(self):
        landscape_paperformat = self.env['report.paperformat'].create({
        'name': 'Landscape',
        # 'default': True,
        'format': 'A4',
        # 'page_height': 210,
        # 'page_width': 297,
        'orientation': 'Landscape',
        })

        return {
            'name': 'Batch Payslips',
            'type': 'ir.actions.report',
            'report_type': 'qweb-pdf',
            'report_name': 'custom_reports.batch_payslip_report_id',
            'report_file': 'custom_reports.batch_payslip_report_id',
            'data': {
                'model': 'hr.payslip',
                'ids': self.ids,
                'report_type': 'pdf',
                'paperformat_id': landscape_paperformat.id
            },
        }
        # result = self.env.ref('custom_reports.action_print_batch_payslip').read()[0]
        # return result

    # @api.depends('net_salary')
    def _compute_values(self):
        deduction=[]
        payAndAllowance=[]
        
        for rec in self:
            
            rec.net_salary =rec.basic_salary =rec.gross= rec.loan_d=rec.leave_d= rec.income_tax_d=rec.eobi_d=0.0
            for line in rec.line_ids:
                if line.category_id.name == "Deduction":
                    deduction.append({f"{line.name}": line.total})
                else:
                    payAndAllowance.append({f"{line.name}": line.total})
                if line.name == 'Net Salary':
                    rec.net_salary = line.total
                elif line.name == 'Basic Salary':
                    rec.basic_salary = line.total
                elif line.name == 'Gross':
                    rec.gross = line.total
                elif line.name == 'Loan':
                    rec.loan_d = line.total
                elif line.name == 'Unpaid Leave':
                    rec.leave_d = line.total
                elif line.name == 'Income Tax':
                    rec.income_tax_d = line.total
                elif line.name == 'EOBI':
                    rec.eobi_d = line.total

    def separateDeductionAndAllowance(self):
        categDict={
        "deductionKeys":[],
        "deductionValues":[],
        "payAndAllowanceKeys":[],
        "payAndAllowanceValues":[]
        }
        for rec in self:
            for line in rec.line_ids:
                if line.category_id.name == "Deduction":
                    categDict["deductionKeys"].append(line.name)
                    categDict["deductionValues"].append(line.total)
                else:
                    categDict["payAndAllowanceKeys"].append(line.name)
                    categDict["payAndAllowanceValues"].append(line.total)
        return categDict