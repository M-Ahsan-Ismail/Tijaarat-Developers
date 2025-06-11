from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritHrContractFuel(models.Model):

    _inherit = 'hr.contract'

    fuel_state = fields.Selection([
        ('none','None'),
        ('draft','Draft'),
        ('submit_for_approval', 'Submit for approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Request Status", default='draft', readonly=True )

    request_ids=fields.One2many('approval.request', 'fuel_id', string='Request')
    
    request_fuel_allowance = fields.Selection([
        ('20', '20 Liters'),
        ('50', '50 Liters'),
        ('75', '75 Liters'),
        ('100', '100 Liters'),
        ('150', '150 Liters'),
        ('250', '250 Liters'),
        ('0', '0 Liters'),
    ], default=False, string="Request Fuel Allowance" )
    
    
    initial_fuel= fields.Boolean(string='Initial fuel',default= False)
    
    
    request_fuel_allowance_booloean= fields.Boolean(string='Request fuel allowance booloean',default=False,store=True,compute='_compute_update_fuel_allowance')
    

    @api.model
    def create(self, vals):
        if 'request_fuel_allowance' not in vals or not vals.get('request_fuel_allowance'):
            vals['request_fuel_allowance'] = vals.get('fuel_allowance', False)
        return super(InheritHrContractFuel, self).create(vals)
    
    @api.depends('request_fuel_allowance')
    def _compute_update_fuel_allowance(self):
        for rec in self:
            if rec.request_fuel_allowance!=rec.fuel_allowance:
                rec.request_fuel_allowance_booloean=True
                rec.fuel_state = 'draft' 
            else:
                rec.request_fuel_allowance_booloean=False

    def submit_for_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Fuel Upgrade Approval')],limit=1)
        admin=self.env['res.users'].search([('groups_id', 'in', self.env.ref('base.group_erp_manager').id)], limit=1)
        approvers=[(0,0,{'user_id':admin.id})]
        
        if not approval_category_id:
            approval_category_id=self.env['approval.category'].create({
                'name':'Fuel Upgrade Approval',
                'manager_approval':'approver',
                'description':'Fuel Upgrade Approval',
                'approver_ids':approvers,
            })
        
        request=self.env['approval.request'].create({
            'name':f"Fuel Upgrade {self.name}",
            'request_owner_id':self.env.uid,
            'category_id':approval_category_id.id,
            'fuel_id':self.id,
            'request_type':'fuel_upgrade_approval', 
        })
        
        self.request_ids=[(4, request.id, 0)]
        request.action_confirm()
        self.fuel_state = "submit_for_approval"
        # raise UserError(self.fuel_state)

    def open_related_approval(self):
        approval_category_id=self.env['approval.category'].search([('name','=','Fuel Upgrade Approval')],limit=1)
        # raise UserError(approval_category_id)
        return {
            'name': 'Related Approval',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.request',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('fuel_id','=',self.id),('category_id','=',approval_category_id.id)]
        }
    
    def action_withdraw_fuel(self):
        request_id = self.env['approval.request'].search([('fuel_id','=',self.id),('request_status','=','pending')])
        request_id.action_cancel()
        request_id.request_status = 'cancel'
        self.fuel_state='draft' 


    def action_approve(self):
        self.fuel_state='approved'
        self.fuel_allowance = self.request_fuel_allowance
        self.request_fuel_allowance = False