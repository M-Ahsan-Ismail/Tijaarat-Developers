from odoo import _,api, fields, models
from odoo.exceptions import UserError, ValidationError

class InheritHrExpense(models.Model):
    _inherit = 'hr.expense'

    expense_approval_state = fields.Selection([
        ('none','None'),
        ('draft','Draft'),
        ('submit_for_approval', 'Submit for approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default="draft",string="Expense approval Status" ,readonly=True)

    request_ids=fields.One2many('approval.request', 'expense_id', string='Request')

    def submit_for_approval_expense(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Expense Approval')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]

        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Expense Approval',
                'manager_approval':'approver',
                'description':'Expense Approval',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':f"Expense Approval {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'expense_id':self.id,
            'request_type':'expense_approval', 
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.state = 'reported'
        self.expense_approval_state="submit_for_approval"

    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('expense_id','=',self.id),('request_status','=','pending')])
        request_id.action_withdraw()

    def open_related_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Expense Approval')],limit=1)
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('expense_id','=',self.id),('category_id','=',approval_category_id.id)]
        }
    
    
    @api.onchange('product_id','product_description','total_amount','currency_id','tax_ids','employee_id','payment_mode','reference','date','account_id','extract_remote_id','sale_order_id','description')        
    def restrict_at_submitted(self):
        if self.expense_approval_state =='submit_for_approval':
            raise UserError("Can't update anything until the status is 'Submit for approval' .")
        


    def check_account_id_in_expenses(self,record=None):
        if record == None:
            record = self
        expense_accounts = self.env['account.account'].search([('account_type', '=', 'expense')])
        if record.account_id in expense_accounts:
            return True
        else:
            return False
        


class InheritHrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'


    def check_account_id_in_expenses(self,record=None):
        if record == None:
            record = self
        expense_accounts = self.env['account.account'].search([('account_type', '=', 'expense')])
        if record.account_id in expense_accounts:
            return True
        else:
            return False
        
    def open_related_payments(self):
        
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('ref','=',self.name), ('payment_type','=', 'outbound')]
        }