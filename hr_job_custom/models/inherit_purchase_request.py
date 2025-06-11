from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritPurchaseRequest(models.Model):
    _inherit = 'purchase.request'


    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('submit_for_approval', 'Submit For Approval'),
        ('assigned_from_inventory', 'Assigned From Inventory'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')],
        string="Approval Status",
        default='draft',
        readonly=True)
    
    request_ids = fields.One2many('approval.request', 'purchase_request_id', string='Request')
    
    # product_on_hand_qty = fields.Float(string="On Hand Quantity", related="line_ids.product_on_hand_qty", readonly=True)

    def action_assign_from_inventory(self):
        if self.state != 'approved':
            raise UserError('Purchase Request must be approved first!')
        else:
            self.approval_state = 'assigned_from_inventory'

    def submit_for_approval(self):
        approval_id=self.env['approval.category'].search([('name','=','Purchase Request Approvals')],limit=1)
        admin = self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_system').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_id:
            approval_id=self.env['approval.category'].create({
                'name':'Purchase Request Approvals',
                'manager_approval':'approver',
                'description':'Purchase Request Approval requests',
                'approver_ids':approvers,
            })
        # raise UserError(str(qpproval_id.read()))
        request=self.env['approval.request'].create({
            'name':self.name,
            'request_owner_id':self.env.uid,
            'category_id':approval_id.id,
            'purchase_request_id':self.id,
            'request_type':'PurchaseRequestApproval',
            'approver_ids': approvers
        })
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.approval_state="submit_for_approval"
        self.state = 'to_approve'

    def action_withdraw(self):
        request_id = self.env['approval.request'].search([('purchase_request_id','=',self.id),('request_status','=','pending')])
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
            'domain':[('purchase_request_id','=',self.id)]
        }
    
    @api.onchange('partner_id','partner_ref','requisition_id','currency_id','date_order',
        'date_planned','picking_type_id','purchasingEmployee','order_line','user_id',
        'payment_term_id','origin','fiscal_position_id','incoterm_id','incoterm_location',
        'on_time_rate_perc','name','notes')
    def ristrict_at_submitted(self):
        if self.approval_state =='submit_for_approval':
            raise UserError("Request is submitted for approval cannot change until approved")