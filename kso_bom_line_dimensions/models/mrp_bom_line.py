from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    length = fields.Float(
        string='Length (cm)',
        digits='Product Unit of Measure',
        help='Optional length in cm',
    )
    width = fields.Float(
        string='Width (cm)',
        digits='Product Unit of Measure',
        help='Optional width in cm',
    )
    height = fields.Float(
        string='Height (cm)',
        digits='Product Unit of Measure',
        help='Optional height in cm',
    )