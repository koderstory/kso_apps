from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    length = fields.Float(
        string='Length (cm)',
        default=None,
        digits='Product Unit of Measure',
        help='Optional length in cm',
    )
    width = fields.Float(
        string='Width (cm)',
        default=None,
        digits='Product Unit of Measure',
        help='Optional width in cm',
    )
    height = fields.Float(
        string='Height (cm)',
        default=None,
        digits='Product Unit of Measure',
        help='Optional height in cm',
    )


    @api.onchange('length', 'width', 'height')
    def _onchange_dimensions_set_uom(self):
        """
        When length, width, and height are provided, automatically set the UoM to cubic meters
        and adjust product_qty to the computed volume in m3.
        """
        for line in self:
            if line.length or line.width or line.height:
                # Compute volume in cubic meters (cm3 to m3)
                volume_m3 = (line.length * line.width * line.height) / 1000000.0
                # Try to set to the standard m3 UoM
                m3_uom = self.env['uom.uom'].search([('name', '=', 'm³')], limit=1)
                if m3_uom:
                    line.product_uom_id = m3_uom
                else:
                    _logger.warning("No UoM named 'm³' found; skipping UoM change")
                # Set the quantity to the computed volume
                line.product_qty = volume_m3