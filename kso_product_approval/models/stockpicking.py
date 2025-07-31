from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for rec in self:
            unapproved = ", ".join(
                line.product_id.name
                for line in rec.move_line_ids
                if line.product_id and line.product_id.state != 'approved')
            if unapproved:
                raise UserError(_(
                    "These Products are Not Approved (%s). "
                    "Please Approve all Products before validating Picking."
                ) % unapproved)
        return super().button_validate()