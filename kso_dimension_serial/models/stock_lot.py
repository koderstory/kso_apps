from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'    # was 'stock.production.lot' in older versions

    length = fields.Float(
        string='Length',
        digits='Product Unit of Measure',
    )
    width = fields.Float(
        string='Width',
        digits='Product Unit of Measure',
    )
    height = fields.Float(
        string='Height',
        digits='Product Unit of Measure',
    )
