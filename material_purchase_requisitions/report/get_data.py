from odoo import fields, api, models, _
from odoo import api, models
from odoo.exceptions import ValidationError, UserError
from collections import Counter




class ComparativeStatementFinalMPR(models.AbstractModel):
    _name = 'report.material_purchase_requisitions.comparison_report_mpr'
    _description = 'Comparison Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print(docids)
        requisition = self.env['material.purchase.requisition'].search([('id', 'in', docids)])
        purchase_ids = self.env['purchase.order'].search([('custom_requisition_id', '=', requisition.id)])
        purchase_ids = sorted(purchase_ids, key=lambda po: po.amount_total, reverse=True)
        filtered_purchase_orders = (po for po in purchase_ids if po.amount_total > 0)
        sorted_purchase_orders = sorted(filtered_purchase_orders, key=lambda po: po.amount_total, reverse=False)
        print(filtered_purchase_orders)
        print(sorted_purchase_orders)
        for po in purchase_ids:
            is_same = self.check_duplicate_products(po)
        print(is_same)
        return {
            'docs': self.env['material.purchase.requisition'].search([('id', 'in', docids)]),
            'purchase_ids': sorted_purchase_orders[:3],
            'is_same': is_same
        }

    def check_duplicate_products(self, purchase_order):
        product_counts = Counter(line.product_id for line in purchase_order.order_line)
        return any(count > 1 for count in product_counts.values())