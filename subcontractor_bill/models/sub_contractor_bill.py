from odoo import models, fields, api, _
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
    sub_contractor_id = fields.Many2one('res.partner', 'Subcontractor', tracking=True, index=True)

    work_lines = fields.One2many('contractor.work.done', 'subcontractor_id', 'Work Lines')
    deduction_lines = fields.One2many('contractor.deduction.advance', 'subcontractor_id', 'Deduction Lines')

    date_from = fields.Date('Period From')
    date_to = fields.Date('Period To')

    sum_total_amount = fields.Float('Total Amount', compute='_compute_work_line_sum', store=True)
    sum_previous = fields.Float('Total Previous', compute='_compute_work_line_sum', store=True)
    sum_this_bill = fields.Float('Total Current Bill', compute='_compute_work_line_sum', store=True)
    total_deduction = fields.Float(string='Total Deduction', compute='_compute_total_deduction', store=True)
    net_payable_amount = fields.Float(string='Net Payable Amount', compute='_compute_net_payable_amount', store=True)

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
