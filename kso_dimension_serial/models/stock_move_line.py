from odoo import api, fields, models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    # three plain Float fields on the move line
    length = fields.Float(string="Length (cm)")
    width  = fields.Float(string="Width (cm)")
    height = fields.Float(string="Height (cm)")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._propagate_dimensions_to_lot()
        return lines

    def write(self, vals):
        res = super().write(vals)
        # only propagate when one of the dims or lot_name changed
        if any(k in vals for k in ('length','width','height','lot_name')):
            self._propagate_dimensions_to_lot()
        return res

    def _propagate_dimensions_to_lot(self):
        """Create lot if needed, then write back length/width/height."""
        Lot = self.env['stock.lot'].sudo()
        for line in self:
            # 1) create the lot on‐the‐fly if user typed a lot_name
            if not line.lot_id and line.lot_name:
                lot = Lot.create({
                    'name':       line.lot_name,
                    'product_id': line.product_id.id,
                    'company_id': line.company_id.id,
                })
                line.lot_id = lot.id
            # 2) write back each non‐null dimension
            if line.lot_id:
                dims = {}
                if line.length is not None:
                    dims['length'] = line.length
                if line.width is not None:
                    dims['width'] = line.width
                if line.height is not None:
                    dims['height'] = line.height
                if dims:
                    line.lot_id.write(dims)

    @api.onchange('length', 'width', 'height')
    def _onchange_dimensions(self):
        for line in self:
            # only compute if all three are set
            if line.length or line.width or line.height:
                # cm³ → m³
                line.quantity = (line.length * line.width * line.height) / 1_000_000