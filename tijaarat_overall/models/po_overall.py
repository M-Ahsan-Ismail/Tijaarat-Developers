from odoo import models, api, fields
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)


class Purchase_Order_Inherit(models.Model):
    _inherit = 'purchase.order'

    site_spr_no = fields.Char(string='Site SPR')

    def button_confirm(self):
        res = super(Purchase_Order_Inherit, self).button_confirm()
        for rec in self:
            print(f'SPr: {rec.site_spr_no} ---> Picking')
            if rec.site_spr_no:
                for picking in rec.picking_ids:
                    picking.site_spr_no = rec.site_spr_no
        return res

    def action_create_invoice(self):
        res = super(Purchase_Order_Inherit, self).action_create_invoice()
        for rec in self:
            print(f'SPr: {rec.site_spr_no} ---> Billing')
            if rec.site_spr_no:
                for invoice in rec.invoice_ids:
                    invoice.site_spr_no = rec.site_spr_no

            if rec.picking_ids:
                for picking in rec.invoice_ids:
                    picking.grn_ids = rec.picking_ids.ids

        return res


class Stock_Picking_Inherit(models.Model):
    _inherit = 'stock.picking'

    site_spr_no = fields.Char(string='SPR')

    purchase_notes = fields.Text('Notes', compute='_compute_notes_from_purchase', store=True, readonly=False)

    @api.depends('purchase_id', 'purchase_id.notes')
    def _compute_notes_from_purchase(self):
        for rec in self:
            if rec.purchase_id and rec.purchase_id.notes:
                rec.purchase_notes = html2plaintext(rec.purchase_id.notes)
            else:
                rec.purchase_notes = False


class Account_Move_Inherit(models.Model):
    _inherit = 'account.move'

    grn_ids = fields.Many2many(
        'stock.picking',
        string='GRN(s)',
        readonly=False
    )

    site_spr_no = fields.Char(string='SPR', index=True, tracking=True)

    cheque_no = fields.Char('Cheque No')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(cheque_no)', 'The "Cheque No" must be unique.'),
    ]

    @api.model
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves:
            # If this move is linked to a payment, pull the cheque_no
            payment = self.env['account.payment'].search([('move_id', '=', move.id)], limit=1)
            if payment and payment.cheque_no:
                move.cheque_no = payment.cheque_no
        return moves




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for rec in self:
            print(f'Data: {rec.cheque_no} --->')
            if rec.move_id:
                rec.move_id.cheque_no = rec.cheque_no
        return res
