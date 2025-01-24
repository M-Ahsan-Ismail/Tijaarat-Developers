from email.policy import default

from odoo import fields, api, models, _


class FundRequisition(models.Model):
    _name = 'fund.requisition'
    _description = 'Fund Requisition'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(readonly=True, default=lambda self: _('New'))
    # name = fields.Char('Fund Demand No')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', tracking=True)
    date = fields.Date('Date', default=fields.Date.today())
    date_start = fields.Date('Start Date', tracking=True)
    date_end = fields.Date('End Date', tracking=True)
    line_ids = fields.One2many('fund.requisition.line', 'fund_requisition_id')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('fund.requisition.seq') or _('New')
        return super().create(vals)

    def print_report(self):
        return self.env.ref('tijaarat_fund_requisition.fund_reqosition_report_action_id').report_action(self)




class FundRequisitionLine(models.Model):
    _name = 'fund.requisition.line'

    fund_requisition_id = fields.Many2one('fund.requisition')
    account_id = fields.Many2one('account.account', 'Description')
    date = fields.Date('Date', default=fields.Date.today())
    date_start = fields.Date(related='fund_requisition_id.date_start')
    date_end = fields.Date(related='fund_requisition_id.date_end')
    average_pwd = fields.Float('Avg. Men Power')
    previous_amount_paid = fields.Float('Previous Amount Paid From Last Demand',
                                        compute='_compute_previous_amount_paid')
    current_amount_demand = fields.Float('Current Demand')
    total_amount = fields.Float('Total Paid Amount To Date', compute='_compute_balance')
    remarks = fields.Text('Remarks')

    @api.depends('account_id', 'date_start', 'date_end')
    def _compute_previous_amount_paid(self):
        for fund in self:
            if fund.date_start and fund.date_end and fund.account_id:
                payments = self.env['account.payment'].search(
                    [('partner_id.name', '=', fund.account_id.name), ('date', '>=', fund.date_start),
                     ('date', '<=', fund.date_end)])
                payments_amount = sum([line.amount for line in payments if line.state == 'posted'])
                fund.previous_amount_paid = payments_amount
            else:
                fund.previous_amount_paid = 0

    @api.depends('account_id')
    def _compute_balance(self):
        for fund in self:
            AccountMoveLine = self.env['account.move.line']
            move_lines = AccountMoveLine.search([
                ('account_id', '=', fund.account_id.id),
                # ('account_id.account_type', '=', 'liability_payable'),
                ('move_id.state', '=', 'posted'),
            ])

            total_debit = sum(line.debit for line in move_lines)
            print(f'total_debit: {total_debit}')
            total_credit = sum(line.credit for line in move_lines)
            print(f'total_credit: {total_credit}')
            balance = total_debit - total_credit
            fund.total_amount = balance
