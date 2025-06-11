from odoo import fields, models, api
from odoo.exceptions import UserError


class Report_Stock_Transfer(models.AbstractModel):
    _name = "report.goods_receiving_report.tijaarat_stock_transfer_report_id"
    _description = "Stock Transfer Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["stock.picking"].browse(docids)

        # Restrict report access to only internal transfers
        if any(doc.picking_type_id.code != "internal" for doc in docs):
            raise UserError("This report is only available for internal transfers.")

        return {
            "doc_ids": docids,
            "doc_model": "stock.picking",
            "docs": docs,
        }


class StockMoveLine(models.Model):
    _inherit = 'stock.move'

    price = fields.Float('Price', digits=(16, 2), compute='_compute_price')

    @api.depends('purchase_line_id', 'sale_line_id')
    def _compute_price(self):
        for rec in self:
            if rec.purchase_line_id:
                rec.price = rec.purchase_line_id.price_unit
            elif rec.sale_line_id:
                rec.price = rec.sale_line_id.price_unit
            else:
                rec.price = 0.0



class GoodsReceivingReportVals(models.Model):
    _inherit = 'stock.picking'

    trf_no = fields.Char('TRF No')
    mode_of_transfer_id = fields.Many2one('mode.transfer', string='Mode Of Transfer')

    def get_previous(self, product_id):
        today = fields.Date.today()  # Get today's date
        active_schedule_date = self.scheduled_date  # Current picking's scheduled date
        print(f"Current picking scheduled date: {active_schedule_date}")

        # Search for the latest stock picking before the current one with the given product
        previous_picking = self.env['stock.picking'].search([
            ('move_ids_without_package.product_id', '=', product_id),
            ('scheduled_date', '<', active_schedule_date),
        ], order='scheduled_date DESC', limit=1)  # Latest picking first

        if previous_picking:
            print(f"Found previous picking: {previous_picking.name}, Date: {previous_picking.scheduled_date}")
            # Get the stock.move related to the product
            move = previous_picking.move_ids_without_package.filtered(
                lambda m: m.product_id.id == product_id
            )
            if move:
                print(f"Found move for product {move.product_id.name}, Price Unit: {move[0].price}")
                return move[0].price or 0.0  # Return price_unit, fallback to 0.0 if None
            else:
                print("No matching stock.move found in previous picking.")
        else:
            print(f"No previous picking found for product ID {product_id} before {active_schedule_date}")
        return 0.0


class Mode_Of_Transfer(models.Model):
    _name = 'mode.transfer'

    name = fields.Char('Name')
