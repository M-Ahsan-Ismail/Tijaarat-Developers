from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritPurchaseRequest(models.Model):
    _inherit = 'purchase.request.line'


    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ("manager_approved", "Manager Approved"),
        ("cto_approved", "CTO Approved"),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True)
    
    line_state = fields.Selection([
        ("draft", "Draft"),
        ("to_approve_mgr", "Submitted to Manager"),
        ("manager_approved", "Manager Approved"),
        ("to_approve_cto", "Submitted to CTO"),
        ("cto_approved", "CTO Approved"),
        ("rejected", "Rejected"),
        ("done", "Done")],
        string="Status",
        default="draft"
    )

    request_ids=fields.One2many('approval.request', 'purchase_request_line_id', string='Request')

    selection_vendor = fields.Many2one(comodel_name="res.partner", string="Vendor Selection")
    selection_vendor_ids = fields.One2many(comodel_name="res.partner", compute="_compute_selection_vendor_ids", string="Selection Vendor IDs")
    
    product_on_hand_qty = fields.Float(string="On Hand Quantity", related="product_id.qty_available", readonly=True)
    unit_price = fields.Float(string="Unit Price")

    @api.onchange('unit_price')
    def onchange_unit_price(self):
        if self.unit_price:
            self.estimated_cost = self.product_qty * self.unit_price
            
    @api.depends('purchase_lines')
    def _compute_selection_vendor_ids(self):
        for record in self:
            record.selection_vendor_ids = [(6, 0, record.purchase_lines.mapped('partner_id').ids)]
        
    def submit_for_approval_manager(self):
        if not self.selection_vendor:
            raise UserError('Please select a vendor.')
        else:
            approval_id=self.env['approval.category'].search([('name','=','Purchase Request Line Manager Approvals')],limit=1)
            manager = self.env['res.users'].search([('groups_id', 'in', self.env.ref('purchase_request.group_purchase_request_manager').id)])
            mgr_list = [mgr.id for mgr in manager]
            # raise UserError(str([manager.read()]))
            approvers=[(0,0,{'user_id':mgr_id}) for mgr_id in mgr_list]
            
            if not approval_id:
                approval_id=self.env['approval.category'].create({
                    'name':'Purchase Request Line Manager Approvals',
                    'manager_approval':'approver',
                    'description':'Purchase Request Line Approval requests for the Purchase Request Manager',
                    'approver_ids':approvers,
                })
            
            
            # updated_approvers = [mgr.id for mgr in approval_id.approver_ids if mgr.exists()]
            # if not updated_approvers:
            #     raise UserError("No valid approvers found for the approval category.")
            
            # raise UserError(updated_approvers)
            request=self.env['approval.request'].create({
                'name':f"Vendor({self.selection_vendor.name}) Approval by Manager for {self.name}",
                'request_owner_id':self.env.uid,
                'category_id':approval_id.id,
                'purchase_request_line_id':self.id,
                'request_type':'PurchaseRequestLineMGRApproval',
                'approver_ids': approvers
            })
            # raise UserError('here')
            # raise UserError(str([request.read()]))
            
            self.request_ids=[(4, request.id, 0)]
            request.action_confirm()
            self.approval_state="submit_for_approval"
            self.line_state = 'to_approve_mgr'

    def action_withdraw_manager(self):
        request_id = self.env['approval.request'].search([('purchase_request_line_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.approval_state = 'draft'
        self.line_state = 'draft'
        self.request_state = 'draft'
    
    def submit_for_approval_cto(self):
        approval_id=self.env['approval.category'].search([('name','=','Purchase Request Line CTO Approvals')],limit=1)
        cto = self.env['res.users'].search([('groups_id', 'in', self.env.ref('recruitment_states_validation.group_CTO').id)], limit=1)
        approvers=[(0,0,{'user_id':cto.id})]
        
        if not approval_id:
            approval_id=self.env['approval.category'].create({
                'name':'Purchase Request Line CTO Approvals',
                'manager_approval':'approver',
                'description':'Purchase Request Line Approval requests for the CTO',
                'approver_ids':approvers,
            })
        # raise UserError(str(qpproval_id.read()))
        request=self.env['approval.request'].create({
            'name':f"Vendor({self.selection_vendor.name}) Approval by CTO for {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_id.id,
            'purchase_request_line_id':self.id,
            'request_type':'PurchaseRequestLineCTOApproval',
            'approver_ids': approvers
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.approval_state="submit_for_approval"
        self.line_state = 'to_approve_cto'
        

    def action_withdraw_cto(self):
        request_id = self.env['approval.request'].search([('purchase_request_line_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        self.approval_state = 'draft'
        self.line_state = 'draft'
        self.request_state = 'draft'
    
    def open_related_approval(self):
        return {
            'name': 'Related PRL Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('purchase_request_line_id','=',self.id)]
        }
    
    @api.onchange('selection_vendor', 'selection_vendor_ids', 'purchase_lines',
                  'purchase_request_allocation_ids')
    def ristrict_at_submitted(self):
        if self.approval_state != 'draft':
            raise UserError("The request has been submitted for approval and cannot be changed!")