from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    CASH_APPROVAL_LIMIT_1 = 5000
    CASH_APPROVAL_LIMIT_2 = 50000
    CASH_APPROVAL_LIMIT_3 = 100000
    STANDARD_APPROVAL_LIMIT = 50000

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True)

    request_ids = fields.One2many('approval.request', 'payment_id', string="Request")
    show_submit_button = fields.Boolean(default=False)
    show_confirm_button = fields.Boolean(default=True)

    @api.onchange('approval_state')
    def _onchange_show_confirm_button(self):
        # self.show_confirm_button = True
        # if self.journal_id.name != 'Cash':
        #     self.show_confirm_button = True  
        #     self.show_submit_button = False          
        # else:
        #     self.show_confirm_button = False
        #     self.show_submit_button = True

        #     if self.approval_state not in ['approved']:
        #         self.show_confirm_button = False
        #     else:
        #         self.show_confirm_button = True

        if self.approval_state != 'draft':
            self.show_confirm_button = True

    def action_draft(self):
        res = super(InheritAccountPayment, self).action_draft()

        self.approval_state = 'draft'
        for i in self.request_ids:
            if i.request_status in ['approved', 'refused']:
                i.action_draft()

    def check_approval_type(self):
        approval_category_id = False
        request_type = ''
        if 'cash' not in self.journal_id.name.lower():
            if self.amount:
                if self.amount <= self.CASH_APPROVAL_LIMIT_1:
                    approval_category_id = self.env['approval.category'].search(
                        [('id_char', '=', 'non_cash_payment_approval')], limit=1)
            request_type = 'NonCashPaymentApproval'
            return approval_category_id, request_type
        else:
            if self.amount:
                if self.amount <= self.CASH_APPROVAL_LIMIT_1:
                    approval_category_id = self.env['approval.category'].search(
                        [('id_char', '=', 'payment_approval_1')], limit=1)
                    request_type = 'PaymentApproval1'
                    if not approval_category_id:
                        raise UserError(
                            'Approval Category "Payment Approval for Amounts less than or equal to 5000" not found!')
                    else:
                        return approval_category_id, request_type
                if self.CASH_APPROVAL_LIMIT_1 < self.amount <= self.CASH_APPROVAL_LIMIT_2:
                    approval_category_id = self.env['approval.category'].search(
                        [('id_char', '=', 'payment_approval_2')], limit=1)
                    request_type = 'PaymentApproval2'
                    if not approval_category_id:
                        raise UserError(
                            'Approval Category "Payment Approval for Amounts less than or equal to 50000 and greater than 5000" not found!')
                    else:
                        return approval_category_id, request_type

                if self.CASH_APPROVAL_LIMIT_2 < self.amount <= self.CASH_APPROVAL_LIMIT_3:
                    approval_category_id = self.env['approval.category'].search(
                        [('id_char', '=', 'payment_approval_3')], limit=1)
                    request_type = 'PaymentApproval3'
                    if not approval_category_id:
                        raise UserError(
                            'Approval Category "Payment Approval for Amounts less than or equal to 100000 and greater than 50000" not found!')
                    else:
                        return approval_category_id, request_type

                elif self.amount > self.CASH_APPROVAL_LIMIT_3:
                    approval_category_id = self.env['approval.category'].search(
                        [('id_char', '=', 'payment_approval_4')], limit=1)
                    request_type = 'PaymentApproval4'
                    if not approval_category_id:
                        raise UserError(
                            'Approval Category "Payment Approval for Amounts greater than 100000" not found!')
                    else:
                        return approval_category_id, request_type
            else:
                raise UserError("Amount can't be zero!\nPlease enter a non-zero number.")

    def submit_for_approval(self):

        # approval_category_id, request_type = self.check_approval_type()
        approval_category_id = self.env[
            'approval.category'].search([('name', '=', 'Payment Approvals')], limit=1)
        if not approval_category_id:
            raise UserError('Payment Approvals not defined')
        admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)

        approvers = [(0, 0, {'user_id': admin.id})]

        request = self.env['approval.request'].create({
            'name': f"{self.name}  ({self.partner_id.name})",
            'request_owner_id': self.env.uid,
            'category_id': approval_category_id.id,
            'payment_id': self.id,
            'request_type': 'PaymentApproval1'
        })

        self.request_ids = [(4, request.id, 0)]
        request.action_confirm()
        self.approval_state = "submit_for_approval"

    def action_withdraw(self):
        request_id = self.env['approval.request'].search(
            [('payment_id', '=', self.id), ('request_status', '=', 'pending')])
        request_id.action_cancel()
        self.approval_state = 'draft'
        self.state = 'draft'

    def open_related_approval(self):
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('payment_id', '=', self.id)]
        }

    @api.onchange('is_internal_transfer', 'payment_type', 'amount',
                  'date', 'ref', 'journal_id', 'payment_method_line_id', 'auto_post')
    def ristrict_at_submitted(self):
        if self.approval_state != 'draft':
            raise UserError("Request is submitted for approval! Changes can only be made in the draft state!")


# class InheritAccountPaymentRegister(models.TransientModel):
#     _inherit = 'account.payment.register'
#
#     def action_create_payments(self):
#         res = super().action_create_payments()
#         self.move_id.payment_state = 'paid'
#         return res
#
#     def _create_payments(self):
#         self.ensure_one()
#         batches = self._get_batches()
#         first_batch_result = batches[0]
#         edit_mode = self.can_edit_wizard and (len(first_batch_result['lines']) == 1 or self.group_payment)
#         to_process = []
#
#         if edit_mode:
#             payment_vals = self._create_payment_vals_from_wizard(first_batch_result)
#             to_process.append({
#                 'create_vals': payment_vals,
#                 'to_reconcile': first_batch_result['lines'],
#                 'batch': first_batch_result,
#             })
#         else:
#             # Don't group payments: Create one batch per move.
#             if not self.group_payment:
#                 new_batches = []
#                 for batch_result in batches:
#                     for line in batch_result['lines']:
#                         new_batches.append({
#                             **batch_result,
#                             'payment_values': {
#                                 **batch_result['payment_values'],
#                                 'payment_type': 'inbound' if line.balance > 0 else 'outbound'
#                             },
#                             'lines': line,
#                         })
#                 batches = new_batches
#
#             for batch_result in batches:
#                 to_process.append({
#                     'create_vals': self._create_payment_vals_from_batch(batch_result),
#                     'to_reconcile': batch_result['lines'],
#                     'batch': batch_result,
#                 })
#
#         payments = self._init_payments(to_process, edit_mode=edit_mode)
#         if payments['journal_id'].name == 'Cash':
#             payments['show_submit_button'] = True
#             # raise UserError(str([payments['show_submit_button']]))
#         # self._post_payments(to_process, edit_mode=edit_mode)
#         # self._reconcile_payments(to_process, edit_mode=edit_mode)
#         return payments
#
#     def action_create_payments(self):
#         # raise UserError(str('here'))
#         payments = self._create_payments()
#         # payments.action_draft()
#         # _logger.info(str(payments))
#         if self._context.get('dont_redirect_to_payments'):
#             return True
#         action = {
#             'name': _('Payments'),
#             'type': 'ir.actions.act_window',
#             'res_model': 'account.payment',
#             'context': {'create': False, 'state': 'draft'},
#         }
#         if len(payments) == 1:
#             action.update({
#                 'view_mode': 'form',
#                 'res_id': payments.id,
#             })
#         else:
#             action.update({
#                 'view_mode': 'tree,form',
#                 'domain': [('id', 'in', payments.ids)],
#             })
#         return action


class InheritAccountMove(models.Model):
    _inherit = 'account.move'

    # so what I've thought about for this problem is that I must check the
    # practical_amount in the current budget and check if that is greater
    # than the planned_amount of the current budget. If it is greater than
    # the planned_amount of the current budget, then I must raise an error
    # that the budget is being exceeded. This must be done for all order_lines.

    def chec_extended_budget_approval(self, record):
        if 'extension' in record.name.lower():
            if record.state == 'confirm':
                return True

            else:
                return False

    def check_account_id_in_expenses(self, record):
        # expense_accounts = self.env['account.account'].search([('account_type', 'in', ['expense','expense_direct_cost','liability_current','liability_non_current'])])
        expense_accounts = self.env['account.account'].search(
            [('account_type', 'in', ['expense', 'expense_direct_cost'])])
        if record.account_id in expense_accounts:
            return True
        else:
            return False

    def check_practical_amount(self):
        '''
        This function is called by an automated action when the journal entry's status changed to 'posted'

        '''
        count = 0
        if self.line_ids:
            for line in self.line_ids:
                if line.account_id.account_type == 'expense':
                    count += 1
        elif self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if line.account_id.account_type == 'expense':
                    count += 1
        elif self.expense_sheet_id:
            if self.expense_sheet_id.expense_line_ids:
                for line in self.expense_sheet_id.expense_line_ids:
                    if line.account_id.account_type == 'expense':
                        count += 1
        if count > 0:
            if self.state == 'posted':
                # check whether the budget for this is confirmed or not
                if self.line_ids:
                    # raise UserError(str([self.line_ids.read()]))
                    for line in self.line_ids:
                        if not self.check_account_id_in_expenses(line):
                            continue
                        # raise UserError(self.line_ids)
                        else:
                            if line.analytic_distribution:
                                analytic_distribution_id = list(line.analytic_distribution.keys())[0]
                                budgetary_record = self.env['crossovered.budget.lines'].search(
                                    [('analytic_account_id', '=', int(analytic_distribution_id)),
                                     ('date_from', '<=', self.date), ('date_to', '>=', self.date),
                                     ('budget_state', '=', 'confirm')])
                                # ^this fails when creating an expense. Try using the expense_id field in account.move in this search
                                if not budgetary_record:
                                    raise UserError("The budget for this is either not created or confirmed yet!")
                                else:
                                    if line.account_id in budgetary_record.general_budget_id.account_ids:
                                        budgetary_record._compute_practical_amount()

                                        # this code block will only run on expense accounts
                                        if budgetary_record.planned_amount < 0:
                                            if (-1 * budgetary_record.practical_amount) > (
                                                    -1 * budgetary_record.planned_amount):
                                                raise UserError(
                                                    f"Planned Budget in {budgetary_record.general_budget_id.name} is being exceeded!")
                                            else:
                                                continue
                            else:
                                budgetary_records = self.env['crossovered.budget.lines'].search(
                                    [('analytic_account_id', '=', False), ('date_from', '<=', self.date),
                                     ('date_to', '>=', self.date), ('related_account_ids', 'in', [line.account_id.id]),
                                     ('budget_state', '=', 'confirm')])

                                # raise UserError(self.date)
                                if not budgetary_records:

                                    raise UserError("The budget for this is either not created or confirmed yet!")

                                else:
                                    for budget_line in budgetary_records:
                                        if line.account_id in budget_line.general_budget_id.account_ids:

                                            # this code block will only run on expense accounts because planned_amount is lesser than 0
                                            if budget_line.planned_amount < 0:
                                                if line.account_id in budget_line.general_budget_id.account_ids:
                                                    budget_line._compute_practical_amount()
                                                    if (-1 * budget_line.practical_amount) > (
                                                            -1 * budget_line.planned_amount):
                                                        raise UserError(
                                                            f"Planned Budget in {budget_line.crossovered_budget_id.name} is being exceeded!")
                                                    else:
                                                        continue
                                        else:
                                            continue
                elif self.invoice_line_ids:
                    for line in self.invoice_line_ids:
                        if not self.check_account_id_in_expenses(line):
                            continue
                        else:
                            if line.analytic_distribution:
                                analytic_distribution_id = list(line.analytic_distribution.keys())[0]
                                budgetary_record = self.env['crossovered.budget.lines'].search(
                                    [('analytic_account_id', '=', int(analytic_distribution_id)),
                                     ('date_from', '<=', self.date), ('date_to', '>=', self.date),
                                     ('budget_state', '=', 'confirm')])

                                if not budgetary_record:
                                    raise UserError(
                                        "The budget for this is either not created or confirmed yet!Invoices")
                                else:
                                    if line.account_id in budgetary_record.general_budget_id.account_ids:
                                        budgetary_record._compute_practical_amount()

                                        # this code block will only run on expense accounts
                                        if budgetary_record.planned_amount < 0:
                                            if (-1 * budgetary_record.practical_amount) > (
                                                    -1 * budgetary_record.planned_amount):
                                                raise UserError(
                                                    f"Planned Budget in {budgetary_record.general_budget_id.name} is being exceeded!")
                                            else:
                                                continue

                            else:
                                budgetary_records = self.env['crossovered.budget.lines'].search(
                                    [('analytic_account_id', '=', False), ('date_from', '<=', self.date),
                                     ('date_to', '>=', self.date), ('related_account_ids', 'in', [line.account_id.id]),
                                     ('budget_state', '=', 'confirm')])
                                if not budgetary_records:
                                    raise UserError(
                                        "The budget for this is either not created or confirmed yet!Invoices")

                                else:
                                    for budget_line in budgetary_records:
                                        if line.account_id in budget_line.general_budget_id.account_ids:

                                            # this code block will only run on expense accounts
                                            if budget_line.planned_amount < 0:
                                                if line.account_id in budget_line.general_budget_id.account_ids:
                                                    budget_line._compute_practical_amount()
                                                    if (-1 * budget_line.practical_amount) > (
                                                            -1 * budget_line.planned_amount):
                                                        raise UserError(
                                                            f"Planned Budget in {budget_line.crossovered_budget_id.name} is being exceeded!")
                                                    else:
                                                        continue
                                        else:
                                            continue
                elif self.expense_sheet_id:
                    if self.expense_sheet_id.expense_line_ids:
                        for line in self.expense_sheet_id.expense_line_ids:
                            if not self.check_account_id_in_expenses(line):
                                continue
                            # raise UserError(self.line_ids)
                            else:
                                if line.analytic_distribution:
                                    analytic_distribution_id = list(line.analytic_distribution.keys())[0]
                                    budgetary_record = self.env['crossovered.budget.lines'].search(
                                        [('analytic_account_id', '=', int(analytic_distribution_id)),
                                         ('date_from', '<=', self.date), ('date_to', '>=', self.date),
                                         ('budget_state', '=', 'confirm')])

                                    if not budgetary_record:
                                        raise UserError(
                                            "The budget for this is either not created or confirmed yet! Expenses")
                                    else:
                                        if line.account_id in budgetary_record.general_budget_id.account_ids:
                                            budgetary_record._compute_practical_amount()

                                            # this code block will only run on expense accounts
                                            if budgetary_record.planned_amount < 0:
                                                if (-1 * budgetary_record.practical_amount) > (
                                                        -1 * budgetary_record.planned_amount):
                                                    raise UserError(
                                                        f"Planned Budget in {budgetary_record.general_budget_id.name} is being exceeded!")
                                                else:
                                                    continue
                                else:
                                    budgetary_records = self.env['crossovered.budget.lines'].search(
                                        [('analytic_account_id', '=', False), ('date_from', '<=', self.date),
                                         ('date_to', '>=', self.date),
                                         ('related_account_ids', 'in', [line.account_id.id]),
                                         ('budget_state', '=', 'confirm')])
                                    if not budgetary_records:
                                        raise UserError(
                                            "The budget for this is either not created or confirmed yet! Expenses")

                                    else:
                                        for budget_line in budgetary_records:
                                            if line.account_id in budget_line.general_budget_id.account_ids:

                                                # this code block will only run on expense accounts
                                                if budget_line.planned_amount < 0:
                                                    if line.account_id in budget_line.general_budget_id.account_ids:
                                                        budget_line._compute_practical_amount()
                                                        if (-1 * budget_line.practical_amount) > (
                                                                -1 * budget_line.planned_amount):
                                                            raise UserError(
                                                                f"Planned Budget in {budget_line.crossovered_budget_id.name} is being exceeded!")
                                                        else:
                                                            continue
                                            else:
                                                continue

    payment_count = fields.Integer(string="", compute="_compute_payment_count")

    def open_related_payments(self):
        return {
            'name': 'Related Payments',
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('ref', 'like', self.name)]
        }

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(self.env['account.payment'].search([('ref', 'like', rec.name)]))

    # def action_post(self):
    #     res = super().action_post()
    #     for rec in self:
    #         rec.check_practical_amount()
    #     return res


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_distribution = fields.Json()
    # @api.onchange('analytic_distribution')
    # def check_analytic_account_budget(self):
    #     # json_data = json.loads(self.analytic_distribution)
    #     if self.analytic_distribution:
    #         # analytic_distribution_dict = json.loads(self.analytic_distribution)
    #         analytic_distribution_id = list(self.analytic_distribution.keys())[0]

    #         budgetary_record = self.env['crossovered.budget.lines'].search([('analytic_account_id','=',int(analytic_distribution_id)),('date_from', '<=',self.date),('date_to', '>=',self.date)])

    #         _logger.info("Invoice Date: %s", self.invoice_date)
    #         _logger.info("Date: %s", self.date)
    #         # raise UserError(budgetary_record)
    #         if budgetary_record:
    #             if budgetary_record.date_from <= self.date <= budgetary_record.date_to:
    #                 if budgetary_record.crossovered_budget_id.approval_state != 'approved':
    #                     self.analytic_distribution = {}
    #                     raise UserError(f"The designated budget, named {budgetary_record.crossovered_budget_id.name}, is not approved!")
    #                 elif budgetary_record.crossovered_budget_id.state != 'confirm':
    #                     raise UserError(f"The designated budget, named {budgetary_record.crossovered_budget_id.name}, is not confirmed!")
    #         else:
    #             self.analytic_distribution = {}
    #             raise UserError('A budget for this has not been created yet!')


class InheritAccountAccount(models.Model):
    _inherit = 'account.account'

    parent_group_id = fields.Many2one('account.group', string="Parent Group", related='group_id.parent_id', store=True)
    grandparent_group_id = fields.Many2one('account.group', string="Grandparent Group",
                                           related='group_id.parent_id.parent_id', store=True)
    great_grandparent_group_id = fields.Many2one('account.group', string="Great Grandarent Group",
                                                 related='group_id.parent_id.parent_id.parent_id', store=True)

#
# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     has_abnormal_deferred_dates = fields.Date()
