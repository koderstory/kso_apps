from odoo import api, models, _ 
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    @api.onchange('quantity', 'product_uom_id')
    def _onchange_quantity(self):
        res = {}
        # if self.quantity and self.product_id.tracking == 'serial':
        #     if float_compare(self.quantity_product_uom, 1.0, precision_rounding=self.product_id.uom_id.rounding) != 0 and not float_is_zero(self.quantity_product_uom, precision_rounding=self.product_id.uom_id.rounding):
        #         raise UserError(_('You can only process 1.0 %s of products with unique serial number.', self.product_id.uom_id.name))
        return res
    
class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.constrains('quantity')
    def check_quantity(self):
        sn_quants = self.filtered(lambda q: q.product_id.tracking == 'serial' and q.location_id.usage != 'inventory' and q.lot_id)
        if not sn_quants:
            return
        domain = expression.OR([
            [('product_id', '=', q.product_id.id), ('location_id', '=', q.location_id.id), ('lot_id', '=', q.lot_id.id)]
            for q in sn_quants
        ])
        groups = self._read_group(
            domain,
            ['product_id', 'location_id', 'lot_id'],
            ['quantity:sum'],
        )
        # for product, _location, lot, qty in groups:
        #     if float_compare(abs(qty), 1, precision_rounding=product.uom_id.rounding) > 0:
        #         raise ValidationError(_('The serial number has already been assigned: \n Product: %(product)s, Serial Number: %(serial_number)s', product=product.display_name, serial_number=lot.name))

    
    