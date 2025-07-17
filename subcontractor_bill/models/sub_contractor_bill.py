from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import datetime


class Subcontractor_Bill(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'subcontractor.bill'

    priority = fields.Selection([('low', 'Low'), ('high', 'High')], string='Priority')
    name = fields.Char('Bill Name', readonly=True, default=lambda self: _('New'))
    project_id = fields.Many2one('project.project', 'Project', tracking=True, index=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.user.company_id, readonly=True, tracking=True,
                                 index=True)
    sub_contractor_id = fields.Many2one('res.partner', 'Subcontractor', tracking=True, index=True,
                                        domain=[('is_subcontractor', '=', True)],required=True)

    work_lines = fields.One2many('contractor.work.done', 'subcontractor_id', 'Work Lines')
    deduction_lines = fields.One2many('contractor.deduction.advance', 'subcontractor_id', 'Deduction Lines')

    date_from = fields.Date('Period From')
    date_to = fields.Date('Period To')

    sum_total_amount = fields.Float('Total Amount', compute='_compute_work_line_sum', store=True)
    sum_previous = fields.Float('Total Previous', compute='_compute_work_line_sum', store=True)
    sum_this_bill = fields.Float('Total Current Bill', compute='_compute_work_line_sum', store=True)
    total_deduction = fields.Float(string='Total Deduction', compute='_compute_total_deduction', store=True)
    net_payable_amount = fields.Float(string='Net Payable Amount', compute='_compute_net_payable_amount', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], string='Status', default='draft')

    bill_date = fields.Date('Bill Date', index=True,tracking=True)
    accounting_date = fields.Date('Accounting Date', index=True, required=True,tracking=True)
    due_date = fields.Date('Due Date', index=True, required=True,tracking=True)
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('name', '=', 'Customer Invoices')],
                                 default=lambda self: self.env['account.journal'].search(
                                     domain=[('code', '=', 'SCB')], limit=1).id)

    analytic_account_ids = fields.Many2many('account.analytic.account')
    bill_reference = fields.Char('Bill Reference')
    move_id = fields.Many2one('account.move', 'Bill', copy=False)
    count_bill_id = fields.Integer('Bills', compute='_compute_bills')

    deduction_adv_account_id = fields.Many2one(
        'account.account',
        string="Deduction/Advance Account",
        help="Default account used for subcontractor deduction or advance entries.",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super(Subcontractor_Bill, self).default_get(fields_list)

        get_default_account = self.env['ir.config_parameter'].sudo().get_param(
            'subcontractor_bill.ded_adv_account_id')  # Updated key to match settings
        print('get_default_account Id:', get_default_account)
        if get_default_account:
            try:
                defaults['deduction_adv_account_id'] = int(get_default_account)
            except (ValueError, TypeError):
                defaults['deduction_adv_account_id'] = False

        return defaults


    @api.depends('move_id')
    def _compute_bills(self):
        for x in self:
            relevant_counts = self.env['account.move'].search_count([('id', '=', self.move_id.id)])
            x.count_bill_id = relevant_counts

    def action_view_related_bills(self):
        return {
            'name': 'Related Sub Contractors',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', '=', self.move_id.id)],
            'context': {'create': False, 'delete': False},
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.onchange('project_id')
    def _onchange_project_id(self):
        for rec in self:
            if rec.project_id and rec.project_id.analytic_account_id:
                rec.analytic_account_ids = [rec.project_id.analytic_account_id.id]
            else:
                rec.analytic_account_ids = None

    def button_confirm(self):
        for rec in self:
            if not rec.project_id:
                raise UserError('Project is required')
            if not rec.bill_date:
                raise UserError(_('Bill Date is required'))
            if not rec.journal_id:
                raise UserError(_('Journal ID is required'))
            if not rec.sub_contractor_id:
                raise UserError(_('Subcontractor is required'))
            self.write({'state': 'posted'})

    def reset_to_draft(self):
        for rec in self:
            if rec.move_id and rec.move_id.state == 'posted':
                raise ValidationError('1st Cancel or Delete bill.')
            self.write({'state': 'draft'})

    def unlink(self):
        for rec in self:
            if rec.move_id and rec.move_id.state == 'posted':
                raise ValidationError(
                    _('You cannot delete a subcontractor bill that is linked to a posted accounting entry. Please cancel or delete the related bill first.'))
        return super(Subcontractor_Bill, self).unlink()

    def create_accounting_entry(self):
        for rec in self:
            if rec.move_id:
                raise ValidationError('Bill is already created...')
            if not rec.work_lines:
                raise ValidationError(_('Work Lines are required'))
            if not rec.analytic_account_ids:
                raise ValidationError(_('At least one analytic account is required'))

            invoice_line_vals = []
            for line in rec.work_lines:
                invoice_line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_id': line.uom.id,
                    'price_unit': line.unit_price,
                    'quantity': line.todated,
                    'account_id': rec.journal_id.default_account_id.id,
                    'analytic_distribution': {str(rec.analytic_account_ids[0].id): 100},
                }))

            for line in rec.deduction_lines:
                account_id = rec.deduction_adv_account_id.id
                if not account_id:
                    raise ValidationError(
                        _('No valid deduction account found. Please set a default deduction account in the settings or ensure a journal default account is configured.'))
                invoice_line_vals.append((0, 0, {
                    'name': line.description,
                    'price_unit': -line.amount,
                    'account_id': account_id,
                }))

            vals = {
                'partner_id': rec.sub_contractor_id.id,
                'analytic_account_id': rec.analytic_account_ids.ids,
                'ref': rec.bill_reference,
                'invoice_date': rec.bill_date,
                'date': rec.accounting_date,
                'invoice_date_due': rec.due_date,
                'journal_id': rec.journal_id.id,
                'invoice_line_ids': invoice_line_vals,
                'sub_contractor_id': rec.id,
                'move_type': 'in_invoice',
            }

            try:
                bill_id = self.env['account.move'].sudo().create(vals)
                rec.write({'move_id': bill_id.id})
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': f'Bill for {rec.bill_date} created successfully',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            except Exception as e:
                raise UserError(_(f'Failed to create bill: {str(e)}'))

    @api.depends('work_lines', 'work_lines.total_amount', 'work_lines.previous_work_done', 'work_lines.this_bill')
    def _compute_work_line_sum(self):
        for bill in self:
            bill.sum_total_amount = sum(line.total_amount for line in bill.work_lines)
            bill.sum_previous = sum(line.total_previous for line in bill.work_lines)
            bill.sum_this_bill = sum(line.total_this_bill for line in bill.work_lines)

    @api.depends('deduction_lines.amount')
    def _compute_total_deduction(self):
        for rec in self:
            rec.total_deduction = sum(line.amount for line in rec.deduction_lines)

    @api.depends('sum_total_amount', 'total_deduction')
    def _compute_net_payable_amount(self):
        for bill in self:
            bill.net_payable_amount = (bill.sum_total_amount or 0.0) - (bill.total_deduction or 0.0)

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('subcontractor.bill.sequence') or '/'
        return super(Subcontractor_Bill, self).create(vals)


class Contractor_Work_Done(models.Model):
    _name = 'contractor.work.done'
    _description = 'Contractor Work Done'

    subcontractor_id = fields.Many2one('subcontractor.bill', 'ID')

    product_id = fields.Many2one('product.product', string='Product', tracking=True, index=True)
    uom = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=True, store=True,
                          tracking=True)
    unit_price = fields.Float('Unit Price', digits=(16, 2), tracking=True)

    previous_work_done = fields.Float('Previous', digits=(16, 2))
    this_bill = fields.Float('This Bill', digits=(16, 2))
    todated = fields.Float('Todated', digits=(16, 2), compute='_compute_todated', store=True)
    total_amount = fields.Float('Total Amount', digits=(16, 2), compute='_compute_total_amount', store=True)
    total_this_bill = fields.Float('SubTotal This Bill', digits=(16, 2), compute='_compute_total_amount', store=True)
    total_previous = fields.Float('SubTotal Previous', digits=(16, 2), compute='_compute_total_amount', store=True)

    @api.depends('previous_work_done', 'this_bill')
    def _compute_todated(self):
        for rec in self:
            rec.todated = (rec.previous_work_done or 0) + (rec.this_bill or 0)

    @api.depends('unit_price', 'todated')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = (rec.unit_price or 0) * (rec.todated or 0)
            rec.total_this_bill = (rec.unit_price or 0) * (rec.this_bill or 0)
            rec.total_previous = (rec.unit_price or 0) * (rec.previous_work_done or 0)



class Contractor_Deduction_Advance(models.Model):
    _name = 'contractor.deduction.advance'
    _description = 'Contractor Deduction Advance'

    subcontractor_id = fields.Many2one('subcontractor.bill', 'ID')

    description = fields.Char(string='Description')
    amount = fields.Float(string='Amount', digits=(16, 2))
