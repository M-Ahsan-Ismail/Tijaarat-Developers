{
    'name': 'Approval Management',
    'version': '17.0',
    'category': 'HR',
    'author': 'Karimdad | Odolution',
    'sequence': -10000,
    'summary': 'Managing approvals in various business flows.',
    'description': """
    This module includes the following:
        * Essential models with the necessary logic for managing each approval
        * Views that extend existing views with the necessary visual implementations

    This module affects the following modules:
        *Accounting
        *Attendances
        *Approval
        *Appraisal
        *Employee
        *Expenses      
        *Payroll
        *Purchase
        *Recruitment
        *Time Off
        
    """,
    'depends': ["base", "hr", 'hr_payroll', "approvals", 'custom_employee_training',
                "ol_payroll_bonus", "wfh_request", "hr_expense",
                "hr_recruitment", "account_budget", 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'security/res_group.xml',
        'security/hr_job_security.xml',
        'views/inherit_hr_job_view.xml',
        'views/inherit_approval_request_view_form.xml',
        'views/inherit_hr_kanban_view_applicant.xml',
        'views/inherit_hr_applicant_view_form.xml',
        'views/inherit_view_hr_job_kanban.xml',
        'views/inherit_hr_employee_form.xml',
        # 'views/inherit_hr_appraisal_goal.xml',
        # 'views/inherit_hr_appraisal.xml',
        'views/inherit_hr_contract.xml',
        'views/inherit_hr_contract_fuel.xml',
        # 'views/inherit_purchase_order.xml',
        # 'views/inherit_purchase_request.xml',
        # 'views/inherit_purchase_request_line.xml',
        'views/inherit_wfh_request.xml',
        'views/inherit_hr_expense.xml',
        'views/inherit_hr_expense_sheet.xml',
        'views/inherit_hr_payslip.xml',
        'views/inherit_crossovered_budget.xml',
        'views/inherit_account_payment.xml',
        'views/inherit_account_move.xml',
        'views/inherit_hr_leave_allocation.xml',
        'views/hr_applicant_interviewer.xml',
        'views/res_config_settings.xml',
        'wizards/rejection_confirm_wizard.xml',
        'wizards/extend_budget_reason.xml',
        # Maaz
        'wizards/refuse_stage_reason.xml',
        # Maaz
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'website': '',
    'author': '',
}
