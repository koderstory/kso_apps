from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        for rec in self:
            unapproved = ", ".join(
                line.product_id.name
                for line in rec.order_line
                if line.product_id and line.product_id.state != 'approved')
            if unapproved:
                raise UserError(_(
                    "These Products are Not Approved (%s). "
                    "Please Approve all Products before confirming Purchase Order."
                ) % unapproved)
        return super().button_confirm()