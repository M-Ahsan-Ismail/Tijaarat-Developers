from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class inheritPurchaseOrder(models.Model):
    _inherit='purchase.order'
    
    

    # approval_state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('submit_for_approval', 'Submit For Approval'),
    #     ('approved', 'Approved'),
    #     ('rejected', 'Rejected')],
    #     string="Approval Status",
    #     default='draft',
    #     readonly=True)
    # request_ids=fields.One2many('approval.request', 'purchaseOrder_id', string='Request')
    purchasingEmployee=fields.Many2one('hr.employee','Purchasing For Employee')
    # isPurchaseForEmployee=fields.Boolean(default=False, compute='_compute_is_purchasing_for_employee')
    # show_confirm_order=fields.Boolean(default=False, compute='_compute_show_confirm_order')
    # total = fields.Float(string = "PO Total", onchange='_onchange_amount_total')
    #
    # show_submit_button = fields.Boolean(default=False, compute='_onchange_approval_buttons')
    # # show_withdraw_button = fields.Boolean(default=False)
    # minimum_approval_amount = fields.Float(string="Minimum Amount Limit")
    #
    #
    # #attrs="{'invisible': ['|',('isPurchaseForEmployee','!=',True),('approval_state', '!=', 'draft')]}"/>
    # #attrs="{'invisible': ['|','|',('isPurchaseForEmployee','=',True),('amount_total','&lt;','minimum_approval_amount'),('approval_state', '!=', 'draft')]}"/>
    # #Withdraw buttons vv
    # #attrs="{'invisible': ['|',('isPurchaseForEmployee','!=',True),('approval_state', 'in', ['draft','approved','rejected'])]}"/>
    # #attrs="{'invisible': ['|','|',('isPurchaseForEmployee','=',True),('amount_total','&lt;','minimum_approval_amount'),('approval_state', 'in', ['draft','approved','rejected'])]}"/>
    #
    # @api.onchange('isPurchaseForEmployee','approval_state','state','amount_total')
    # def _onchange_approval_buttons(self):
    #     # MIN_APPROVAL_AMOUNT = float(self.env['ir.config_parameter'].get_param('hr_job_custom.minimum_approval_amount'))
    #     # self.minimum_approval_amount = MIN_APPROVAL_AMOUNT
    #     MIN_APPROVAL_AMOUNT = 5000
    #
    #     if self.isPurchaseForEmployee:
    #         # self.show_submit_button = (self.approval_state == 'draft' or self.state == 'draft')
    #         self.show_submit_button = True
    #         if self.approval_state != 'draft':
    #             self.show_submit_button = False
    #     else:
    #         # self.show_submit_button = (self.amount_total > MIN_APPROVAL_AMOUNT or self.approval_state == 'draft')
    #         if self.amount_total > MIN_APPROVAL_AMOUNT:
    #             self.show_submit_button = True
    #             if self.approval_state not in ['draft']:
    #                 self.show_submit_button = False
    #         else:
    #             self.show_submit_button = False
    #
    # @api.onchange('purchasingEmployee','amount_total')
    # def _compute_is_purchasing_for_employee(self):
    #     MIN_APPROVAL_AMOUNT = float(self.env['ir.config_parameter'].get_param('hr_job_custom.minimum_approval_amount'))
    #     self.minimum_approval_amount = MIN_APPROVAL_AMOUNT
    #
    #     total = self.amount_total
    #     self.total = total
    #
    #     if self.purchasingEmployee or self.total >= MIN_APPROVAL_AMOUNT:
    #         self.isPurchaseForEmployee=True
    #     else:
    #         self.isPurchaseForEmployee=False
    #
    # @api.onchange('isPurchaseForEmployee','approval_state','state')
    # def _compute_show_confirm_order(self):
    #     MIN_APPROVAL_AMOUNT = float(self.env['ir.config_parameter'].get_param('hr_job_custom.minimum_approval_amount'))
    #     self.minimum_approval_amount = MIN_APPROVAL_AMOUNT
    #
    #     if self.state in ['done']:
    #         self.show_confirm_order = False
    #
    #     if self.isPurchaseForEmployee:
    #         ######CONFIRM BUTTON LOGIC######
    #         self.show_confirm_order = False
    #         if self.approval_state in ['approved']:
    #             self.show_confirm_order = True
    #
    #         if self.state == 'done':
    #             self.show_confirm_order = False
    #         ######CONFIRM BUTTON LOGIC######
    #
    #         # ######SUBMIT BUTTON LOGIC######
    #         # self.show_submit_button = True
    #         # if self.approval_state not in ['draft']:
    #         #     self.show_submit_button = False
    #
    #         # ######SUBMIT BUTTON LOGIC######
    #     else:
    #         self.show_confirm_order = (self.amount_total < MIN_APPROVAL_AMOUNT or self.approval_state == 'approved') and self.state != 'done'
    #
    #
    # def submit_for_approval(self):
    #     approval_id=self.env['approval.category'].search([('name','=','Purchase Order Approvals')],limit=1)
    #     admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_system').id)], limit=1)
    #     approvers=[(0,0,{'user_id':admin.id})]
    #
    #     if not approval_id:
    #         approval_id=self.env['approval.category'].create({
    #             'name':'Purchase Order Approvals',
    #             'manager_approval':'approver',
    #             'description':'Purchase Order Approval requests',
    #             'approver_ids':approvers,
    #         })
    #     # raise UserError(str(qpproval_id.read()))
    #     request=self.env['approval.request'].create({
    #         'name':self.name,
    #         'request_owner_id':self.env.uid,
    #         'category_id':approval_id.id,
    #         'purchaseOrder_id':self.id,
    #         'request_type':'purchaseOrderRequest'
    #
    #     })
    #     self.request_ids=[(4, request.id, 0)]
    #     request.action_confirm()
    #     self.approval_state="submit_for_approval"
    #
    # def action_withdraw(self):
    #     request_id = self.env['approval.request'].search([('purchaseOrder_id','=',self.id),('request_status','=','pending')])
    #     request_id.action_cancel()
    #     self.approval_state='draft'
    #     # self.request_ids.action_cancel()
    #     # self.approval_state='draft'
    #
    # def open_related_po_approval(self):
    #     return {
    #         'name': 'Related Approval',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'approval.request',
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #         'domain':[('purchaseOrder_id','=',self.id)]
    #     }
    #
    # @api.onchange('partner_id','partner_ref','requisition_id','currency_id','date_order',
    #     'date_planned','picking_type_id','purchasingEmployee','order_line','user_id',
    #     'payment_term_id','origin','fiscal_position_id','incoterm_id','incoterm_location',
    #     'on_time_rate_perc','name','notes')
    # def ristrict_at_submitted(self):
    #     if self.approval_state =='submit_for_approval':
    #         raise UserError("Request is submitted for approval cannot change until approved")