from odoo import api, fields, models

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    width = fields.Float(string="Width (cm)")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._propagate_width_to_lot()
        return lines

    def write(self, vals):
        
        res = super().write(vals)
        # only run when width or lot_name changed
        if 'width' in vals or 'lot_name' in vals:
            self._propagate_width_to_lot()
        return res

    def _propagate_width_to_lot(self):
        Lot = self.env['stock.lot'].sudo()
        for line in self:
            # if there's no lot yet but the user gave a lot_name, create it
            if not line.lot_id and line.lot_name:
                lot = Lot.create({
                    'name':        line.lot_name,
                    'product_id':  line.product_id.id,
                    'company_id':  line.company_id.id,
                })
                # assign it back on the move line
                line.lot_id = lot.id
            # now, if we have a lot, write the width
            if line.lot_id and line.width is not None:
                line.lot_id.write({'width': line.width})
