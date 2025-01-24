from email.policy import default
from odoo import fields, api, models, _


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


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def Comparison_description(self):
        active_id = self.env.context.get('active_id')
        obj = self.env['purchase.requisition'].browse(active_id)
        product_data = []

        for x in obj.line_ids:
            matching_recs = self.env['purchase.order.line'].search([('product_id', '=', x.product_id.id)])
            for rec in matching_recs:
                if (rec.name, rec.product_uom.name) not in product_data:
                    product_data.append((rec.name, rec.product_uom.name))

        return product_data






    def Comparison(self):
        active_id = self.env.context.get('active_id')
        obj = self.env['purchase.requisition'].browse(active_id)
        vendor_prices = {}

        if obj.vendor_id and len(obj.vendor_id) == 1:
            vendor = obj.vendor_id
            for line in obj.line_ids:
                matching_recs = self.env['purchase.order.line'].search([
                    ('product_id', '=', line.product_id.id),
                    ('order_id.partner_id', '=', vendor.id)
                ])

                for rec in matching_recs:
                    vendor_name = rec.order_id.partner_id.name
                    prod_qty = rec.product_qty
                    price = rec.price_unit
                    amount = price * prod_qty
                    product_name = rec.name
                    product_unit = rec.product_uom.name

                    if vendor_name not in vendor_prices:
                        vendor_prices[vendor_name] = {'products': [], 'total_each_vendor': 0}

                    vendor_prices[vendor_name]['products'].append({
                        'product': prod_qty,
                        'price': price,
                        'amount': amount,
                        'name': product_name,
                        'unit': product_unit
                    })

                    # Update the vendor's total amount
                    vendor_prices[vendor_name]['total_each_vendor'] += amount

        else:
            for vendor in obj.vendor_id:
                for line in obj.line_ids:
                    matching_recs = self.env['purchase.order.line'].search([
                        ('product_id', '=', line.product_id.id),
                        ('order_id.partner_id', '=', vendor.id)
                    ])

                    for rec in matching_recs:
                        vendor_name = rec.order_id.partner_id.name
                        prod_qty = rec.product_qty
                        price = rec.price_unit
                        amount = price * prod_qty
                        product_name = rec.name
                        product_unit = rec.product_uom.name

                        if vendor_name not in vendor_prices:
                            vendor_prices[vendor_name] = {'products': [], 'total_each_vendor': 0}

                        vendor_prices[vendor_name]['products'].append({
                            'product': prod_qty,
                            'price': price,
                            'amount': amount,
                            'name': product_name,
                            'unit': product_unit
                        })

                        vendor_prices[vendor_name]['total_each_vendor'] += amount

        # Sort vendors by `total_each_vendor` in ascending order
        sorted_vendor_prices = dict(sorted(vendor_prices.items(), key=lambda x: x[1]['total_each_vendor']))

        # Limit to the top 4 vendors
        sorted_vendor_prices = dict(list(sorted_vendor_prices.items())[:4])

        return sorted_vendor_prices














