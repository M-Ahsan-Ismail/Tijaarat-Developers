from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _order = 'price_subtotal asc'

    price_unit = fields.Float(
        string='Unit Price', required=True, digits='Product Price',
        compute="_compute_price_unit_and_date_planned_and_name", readonly=False, store=True, group_operator=None)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True,
                               compute='_compute_product_qty', store=True, readonly=False, group_operator=None)
    is_minimum = fields.Boolean(string="Is Minimum", compute="_compute_is_minimum", store=True)

    @api.depends('product_id', 'price_unit')
    def _compute_is_minimum(self):
        for line in self:
            min_price = self.env['purchase.order.line'].search([
                ('product_id', '=', line.product_id.id),
            ], order='price_unit asc', limit=1)
            line.is_minimum = line.price_unit == min_price.price_unit if min_price else False
