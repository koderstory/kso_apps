from odoo import api, models, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        Quant = self.env['stock.quant']
        in_popup = self.env.context.get('default_move_id') or \
                   self.env.context.get('force_fill_lot_available_qty')
        if in_popup and not self.env.context.get('skip_autofill_qty'):
            for vals in vals_list:
                pid, loc, lot = vals.get('product_id'), vals.get('location_id'), vals.get('lot_id')
                if pid and loc and lot:
                    product  = self.env['product.product'].browse(pid)
                    location = self.env['stock.location'].browse(loc)
                    lot_rec  = self.env['stock.lot'].browse(lot)
                    avail = Quant._get_available_quantity(
                        product, location,
                        lot_id=lot_rec,
                        package_id=vals.get('package_id') and self.env['stock.quant.package'].browse(vals['package_id']) or False,
                        owner_id=vals.get('owner_id') and self.env['res.partner'].browse(vals['owner_id']) or False,
                    )
                    vals['quantity'] = float_round(max(0.0, avail), precision_rounding=product.uom_id.rounding)
                    # Let Odoo compute quantity_product_uom; no need to set it manually
        return super().create(vals_list)

    def write(self, vals):
        Quant = self.env['stock.quant']
        in_popup = self.env.context.get('default_move_id') or \
                   self.env.context.get('force_fill_lot_available_qty')
        if not in_popup or self.env.context.get('skip_autofill_qty'):
            return super().write(vals)

        # Precompute target qty per line using the *new* values from vals
        targets = {}
        for line in self:
            pid = vals.get('product_id', line.product_id.id)
            loc = vals.get('location_id', line.location_id.id)
            lot = vals.get('lot_id', line.lot_id.id)
            if pid and loc and lot:
                product  = self.env['product.product'].browse(pid)
                location = self.env['stock.location'].browse(loc)
                lot_rec  = self.env['stock.lot'].browse(lot)
                avail = Quant._get_available_quantity(
                    product, location,
                    lot_id=lot_rec,
                    package_id=vals.get('package_id', line.package_id.id) and self.env['stock.quant.package'].browse(vals.get('package_id', line.package_id.id)) or False,
                    owner_id=vals.get('owner_id', line.owner_id.id) and self.env['res.partner'].browse(vals.get('owner_id', line.owner_id.id)) or False,
                )
                targets[line.id] = float_round(max(0.0, avail), precision_rounding=product.uom_id.rounding)

        res = super().write(vals)

        # Now set each line’s quantity individually (avoid recursion)
        if targets:
            for line in self:
                if line.id in targets:
                    super(StockMoveLine, line.with_context(skip_autofill_qty=True)).write({
                        'quantity': targets[line.id]
                    })
        return res
