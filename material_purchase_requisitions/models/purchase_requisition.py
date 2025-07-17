# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date

from odoo.addons.material_requisition_cost_sheet.models.material_purchase_requisition import PurchaseRequisition
# from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError


class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']  # odoo11
    _order = 'id desc'

    # @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise UserError(
                    _('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        #                raise UserError(_('You can not delete Purchase Requisition which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()

    name = fields.Char(
        string='Number',
        index=True,
        # readonly=1,
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Approved'),
        ('stock', "RFQ Created"),
        ('receive', 'Material Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        # tracking=True,
        tracking=True
    )
    request_date = fields.Date(
        string='Requisition Date',
        # default=fields.Date.today(),
        default=lambda self: fields.Date.context_today(self),
        required=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True,
        copy=True,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        readonly=True,
        copy=False,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager Reject',
        readonly=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rejected by',
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True,
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        string='Purchase Requisitions Line',
        copy=True,
    )
    date_end = fields.Date(
        string='Requisition Deadline',
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )
    date_done = fields.Date(
        string='Date Done',
        readonly=True,
        help='Date of Completion of Purchase Requisition',
    )
    managerapp_date = fields.Date(
        string='Department Approval Date',
        readonly=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Department Manager Reject Date',
        readonly=True,
    )
    userreject_date = fields.Date(
        string='Rejected Date',
        readonly=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    receive_date = fields.Date(
        string='Received Date',
        readonly=True,
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Requisitions',
        required=False,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True,
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        string='Requisition Responsible',
        copy=True,
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmed by',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )

    purchase_order_ids = fields.One2many(
        'purchase.order',
        'custom_requisition_id',
        string='Purchase Orders',
    )
    purchase_order_line_ids = fields.One2many(
        'purchase.order.line',
        compute='_compute_purchase_order_lines',
        string='Purchase Order Lines',
        store=False  # Set to True if you need to filter/sort on this field
    )

    site_spr_no = fields.Char('Site SPR')

    def _compute_purchase_order_lines(self):
        for rec in self:
            rec.purchase_order_line_ids = self.env['purchase.order'].search([
                ('custom_requisition_id', '=', self.id), ('amount_total', '>=', 0)
            ]).mapped('order_line')

    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False,
    )
    requisition_type = fields.Selection([
        ('task', 'Task/Activity'),
        ('sheet', 'Cost Sheet'),
        ('other', 'Other'),
    ], default='other')
    partner_id = fields.Many2many(
        'res.partner',
        string='Vendors',
    )

    @api.onchange('partner_id')
    def _on_partner_id_change(self):
        for rec in self:
            if rec.partner_id:
                for line in rec.requisition_line_ids:
                    line.partner_id = rec.partner_id.ids

    # @api.model
    # def create(self, vals):
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name = self.env['ir.sequence'].next_by_code('purchase.requisition.seq')
            vals.update({
                'name': name
            })
        res = super(MaterialPurchaseRequisition, self).create(vals_list)
        return res

    # @api.multi
    def requisition_confirm(self):
        for rec in self:
            manager_mail_template = self.env.ref(
                'material_purchase_requisitions.email_confirm_material_purchase_requistion')
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'dept_confirm'
            if manager_mail_template:
                manager_mail_template.send_mail(self.id)

    # @api.multi
    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    # @api.multi
    def manager_approve(self):
        for rec in self:
            rec.managerapp_date = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            employee_mail_template = self.env.ref(
                'material_purchase_requisitions.email_purchase_requisition_iruser_custom')
            email_iruser_template = self.env.ref('material_purchase_requisitions.email_purchase_requisition')
            # employee_mail_template.sudo().send_mail(self.id)
            # email_iruser_template.sudo().send_mail(self.id)
            employee_mail_template.send_mail(self.id)
            email_iruser_template.send_mail(self.id)
            rec.state = 'ir_approve'

    # @api.multi
    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    # @api.multi
    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False):
        pick_vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': line.qty,
            'product_uom': line.uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,
            'name': line.product_id.name,
            'picking_type_id': self.custom_picking_type_id.id,
            'picking_id': stock_id.id,
            'custom_requisition_line_id': line.id,
            'company_id': line.requisition_id.company_id.id,
        }
        return pick_vals

    @api.model
    def _prepare_po_line(self, line=False, purchase_order=False):
        seller = line.product_id._select_seller(
            partner_id=self._context.get('partner_id'),
            quantity=line.qty,
            date=purchase_order.date_order and purchase_order.date_order.date(),
            uom_id=line.uom
        )
        po_line_vals = {
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_qty': line.qty,
            'product_uom': line.uom.id,
            'date_planned': fields.Date.today(),
            # 'price_unit': line.product_id.standard_price,
            'price_unit': 0.0,
            'order_id': purchase_order.id,
            # 'account_analytic_id': self.analytic_account_id.id,
            'analytic_distribution': {self.sudo().analytic_account_id.id: 100} if self.analytic_account_id else False,
            'custom_requisition_line_id': line.id,
            'brand_id': line.brand_id.id
        }
        return po_line_vals

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        purchase_obj = self.env['purchase.order']
        purchase_line_obj = self.env['purchase.order.line']

        for rec in self:
            if not rec.requisition_line_ids:
                raise UserError(_('Please create some requisition lines.'))

            # Internal Requisition (Stock Transfer)
            if any(line.requisition_type == 'internal' for line in rec.requisition_line_ids):
                if not rec.location_id:
                    raise UserError(_('Select Source location under the picking details.'))
                if not rec.custom_picking_type_id:
                    raise UserError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise UserError(_('Select Destination location under the picking details.'))

                # Prepare picking data
                picking_vals = {
                    'partner_id': rec.employee_id.sudo().user_partner_id.id if rec.employee_id else False,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id.id,
                    'picking_type_id': rec.custom_picking_type_id.id,
                    'note': rec.reason,
                    'custom_requisition_id': rec.id,
                    'origin': rec.name,
                    'company_id': rec.company_id.id,
                }

                stock_id = stock_obj.sudo().create(picking_vals)
                rec.write({'delivery_picking_id': stock_id.id})

                # Create stock moves
                for line in rec.requisition_line_ids.filtered(lambda l: l.requisition_type == 'internal'):
                    pick_vals = rec._prepare_pick_vals(line, stock_id)
                    if pick_vals:  # Ensure valid data
                        move_obj.sudo().create(pick_vals)

            # Purchase Requisition
            po_dict = {}
            for line in rec.requisition_line_ids.filtered(lambda l: l.requisition_type == 'purchase'):
                if not line.partner_id:
                    raise UserError(_('Please enter at least one vendor on Requisition Lines for Purchase Action.'))

                for partner in line.partner_id:
                    if partner not in po_dict:
                        po_vals = {
                            'partner_id': partner.id,
                            'currency_id': rec.env.user.company_id.currency_id.id,
                            'date_order': fields.Date.today(),
                            'company_id': rec.company_id.id,
                            'custom_requisition_id': rec.id,
                            'origin': rec.name,
                            'requisition_type': rec.requisition_type,
                            'requisition_id': False,
                            'analytic_account_id': rec.analytic_account_id.id,
                            'project_id': rec.project_id.id,
                            'task_id': rec.task_id.id,
                            'site_spr_no': rec.site_spr_no,
                            'notes': rec.reason,
                            # 'task_id': rec.task_id.id,
                            #                             'project_id': rec.project_id.id,
                            #                             'analytic_account_id': rec.analytic_account_id.id,
                        }
                        purchase_order = purchase_obj.sudo().create(po_vals)
                        po_dict[partner] = purchase_order
                    else:
                        purchase_order = po_dict[partner]

                    # Create purchase order lines
                    po_line_vals = rec.with_context(partner_id=partner)._prepare_po_line(line, purchase_order)
                    if po_line_vals:  # Ensure valid data
                        purchase_line_obj.sudo().create(po_line_vals)
            rec.state = 'stock'

    # @api.multi
    def action_received(self):
        for rec in self:
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'

    # @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.onchange('employee_id')
    def set_department(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id

            # @api.multi

    def show_picking(self):
        # for rec in self:
        # res = self.env.ref('stock.action_picking_tree_all')
        # res = res.sudo().read()[0]
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('stock.action_picking_tree_all')
        res['domain'] = str([('custom_requisition_id', '=', self.id)])
        return res

    # @api.multi
    def action_show_po(self):
        # for rec in self:
        #     purchase_action = self.env.ref('purchase.purchase_rfq')
        #     purchase_action = purchase_action.sudo().read()[0]
        self.ensure_one()
        purchase_action = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_rfq')
        purchase_action['domain'] = str([('custom_requisition_id', '=', self.id)])
        return purchase_action

    is_rfq = fields.Boolean(compute='_compute_is_frq')

    def _compute_is_frq(self):
        for rec in self:
            draft_pos = self.env['purchase.order'].search([
                ('custom_requisition_id', '=', self.id),
                ('state', 'in', ['draft', 'sent'])
            ])
            rec.is_rfq = len(draft_pos) > 1

    def action_cancel_draft_po(self):
        draft_pos = self.env['purchase.order'].search([
            ('custom_requisition_id', '=', self.id),
            ('state', 'in', ['draft', 'sent'])
        ])
        for po in draft_pos:
            po.button_cancel()

    def action_show_po_lines(self):
        self.ensure_one()
        purchase_action = self.env['ir.actions.act_window']._for_xml_id(
            'material_purchase_requisitions.action_purchase_order_line_comparison')
        purchase_action['domain'] = str([('id', 'in', self.purchase_order_line_ids.ids)])
        return purchase_action
