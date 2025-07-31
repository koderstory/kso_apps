from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for rec in self:
            unapproved = ", ".join(
                line.product_id.name
                for line in rec.order_line
                if line.product_id and line.product_id.state != 'approved')
            if unapproved:
                raise UserError(_(
                    "These Products are Not Approved (%s). "
                    "Please Approve all Products before confirming Sale Order."
                ) % unapproved)
        return super().action_confirm()