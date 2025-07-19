# models/stock_quant.py
from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    lot_length = fields.Float(
        string="Length (cm)",
        related="lot_id.length",
        store=True,
        readonly=True,
    )
    lot_width = fields.Float(
        string="Width (cm)",
        related="lot_id.width",
        store=True,
        readonly=True,
    )
    lot_height = fields.Float(
        string="Height (cm)",
        related="lot_id.height",
        store=True,
        readonly=True,
    )
