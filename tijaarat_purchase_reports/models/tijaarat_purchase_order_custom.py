from odoo import fields, api, models, _
from odoo import api, models
from odoo.exceptions import ValidationError, UserError
from collections import Counter


class PurchaseOrderCustom(models.Model):
    _inherit = 'purchase.order'

    delivery_add_id = fields.Many2one('res.partner', 'Delivery Address')
    delivery_add_ids = fields.Many2many('res.partner', compute='_compute_delivery_add_ids')

    @api.depends('delivery_add_id')
    def _compute_delivery_add_ids(self):
        for rec in self:
            if rec.company_id.partner_id:
                rec.delivery_add_ids = self.env['res.partner'].search(
                    [('parent_id', '=', rec.company_id.partner_id.id), ('type', '=', 'delivery')]).ids
            else:
                rec.delivery_add_ids = False  # Use False to clear the Many2many field

    def print_quotation(self):
        # self.write({'state': "sent"})
        return self.env.ref('tijaarat_purchase_reports.tijaarat_purchase_report_action_id').report_action(self)

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.constrains('line_ids')
    def _check_exist_product_in_line(self):
        for order in self:
            products_in_lines = order.mapped('line_ids.product_id')
            for product in products_in_lines:
                lines_count = len(order.line_ids.filtered(lambda line: line.product_id == product))
                if lines_count > 1:
                    raise UserError(_('You cannot select the same product on multiple lines.'))
        return True


class ComparativeStatementFinal(models.AbstractModel):
    _name = 'report.tijaarat_purchase_reports.comparison_report_document'
    _description = 'Comparative Statement'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(docids)
        requisition = self.env['purchase.requisition'].search([('id', 'in', docids)])
        purchase_ids = sorted(requisition.purchase_ids, key=lambda po: po.amount_total, reverse=True)
        filtered_purchase_orders = (po for po in purchase_ids if po.amount_total > 0)
        sorted_purchase_orders = sorted(filtered_purchase_orders, key=lambda po: po.amount_total, reverse=False)
        print(filtered_purchase_orders)
        print(sorted_purchase_orders)
        for po in requisition.purchase_ids:
            is_same = self.check_duplicate_products(po)
        print(is_same)
        return {
            'docs': self.env['purchase.requisition'].search([('id', 'in', docids)]),
            'purchase_ids': sorted_purchase_orders[:3],
            'is_same': is_same
        }

    def check_duplicate_products(self, purchase_order):
        product_counts = Counter(line.product_id for line in purchase_order.order_line)
        return any(count > 1 for count in product_counts.values())
# 03004870629