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


class Goods_receiveing_Report_vals(models.Model):
    _inherit = 'stock.picking'

    trf_no = fields.Char('TRF No')
    mode_of_transfer_id = fields.Many2one('mode.transfer', string='Mode Of Transfer')

    def get_previous(self, product_id):
        today = fields.Date.today()  # Get today's date

        previous_picking = self.env['stock.picking'].search([
            ('move_ids_without_package.product_id', '=', product_id),
            ('scheduled_date', '<', today)
        ], order='scheduled_date DESC', limit=2)  # Get the latest previous picking

        if previous_picking and previous_picking[0]:
            previous_price = previous_picking[0].move_ids_without_package.filtered(
                lambda move: move.product_id.id == product_id
            ).mapped('price')

            return previous_price[0] if previous_price else 0.0
        return 0.0


class Mode_Of_Transfer(models.Model):
    _name = 'mode.transfer'

    name = fields.Char('Name')
