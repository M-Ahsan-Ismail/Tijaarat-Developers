from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


# Karimdad Start
class InheritCrossoveredBudgets(models.Model):
    _inherit = 'crossovered.budget'

    budget_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')], default="draft")

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True)

    request_ids = fields.One2many('approval.request', 'budget_id', string='Request')

    def submit_for_approval(self):
        approval_category_id = self.env['approval.category'].search([('name', '=', 'Budget Approvals')], limit=1)

        admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)

        approvers = [(0, 0, {'user_id': admin.id})]
        if not approval_category_id:
            raise UserError('Approval Category "Budget Approvals" not found!')

        request = self.env['approval.request'].create({
            'name': f"{self.name}  ({self.user_id.name})",
            'request_owner_id': self.env.uid,
            'category_id': approval_category_id.id,
            'budget_id': self.id,
            'request_type': 'BudgetApproval'
        })

        self.request_ids = [(4, request.id, 0)]
        request.action_confirm()
        self.approval_state = "submit_for_approval"

    def action_withdraw(self):
        request_id = self.env['approval.request'].search(
            [('budget_id', '=', self.id), ('request_status', '=', 'pending')])
        request_id.action_cancel()
        self.approval_state = 'draft'
        self.budget_state = 'draft'

    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('budget_id', '=', self.id)]
        }

    extension_reason = fields.Text(string="Extension Reason")
    isExtended = fields.Boolean(string="isFirstExtension", default=False)
    extension_count = fields.Integer(string="Extension Count", default=0)
    parent_budget = fields.Many2one('crossovered.budget', string="Parent Budget")

    def action_cancel(self):

        self.state = 'cancel'
        self.approval_state = 'rejected'
        self.budget_state = 'rejected'

    def extend_budget_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Extend Budget'),
            'res_model': 'rejection.confirm.reason.wizard',
            'target': 'new',
            'view_id': self.env.ref('hr_job_custom.extend_button_reason_view').id,
            'view_mode': 'form',
            'context': {
                "request": self.id,
            }
        }

    def extend_budget(self, reason):

        extended_budget = self.copy()
        extended_budget.isExtended = True
        extended_budget.extension_count = self.extension_count + 1
        extended_budget.parent_budget = self.id
        extended_budget.name = self.name + ': Extension ' + str(self.extension_count + 1)
        extended_budget.extension_reason = reason
        extended_budget.approval_state = 'draft'
        extended_budget.budget_state = 'draft'

        idx = self.name.find(':')
        if idx > 0:
            extended_budget.name = self.name[:idx] + ': Extension ' + str(self.extension_count + 1)
        else:
            extended_budget.name = self.name + ': Extension ' + str(self.extension_count + 1)

        self.action_cancel()

        return {
            'name': 'Extend Budget',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            # 'view_id': self.env.ref('account_budget.crossovered_budget_view_form').id,
            'res_id': extended_budget.id,
            'res_model': 'crossovered.budget',
            'target': 'current',
        }

    def action_budget_draft(self):
        res = super().action_budget_draft()
        self.approval_state = 'draft'
        return res


class InheritCrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    budget_state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancel'),
        ('confirm', 'Confirm'),
        ('validate', 'Validate'),
        ('done', 'Done')
    ], related='crossovered_budget_id.state', string="Budget State", readonly=True)

    related_account_ids = fields.Many2many('account.account', related='general_budget_id.account_ids',
                                           string="Related Account IDs", readonly=True)

# Karimdad End
