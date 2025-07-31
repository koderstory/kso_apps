from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            unapproved = ", ".join(
                line.product_id.name
                for line in rec.invoice_line_ids
                if line.product_id and line.product_id.state != 'approved')
            if unapproved:
                if rec.move_type in ('in_invoice', 'in_refund'):
                    raise UserError(_(
                        "These Products are Not Approved (%s). "
                        "Please Approve all Products before posting Vendor Bill/Refund."
                    ) % unapproved)
                if rec.move_type == 'out_refund':
                    raise UserError(_(
                        "These Products are Not Approved (%s). "
                        "Please Approve all Products before posting Credit Note."
                    ) % unapproved)
                if rec.move_type == 'out_invoice':
                    raise UserError(_(
                        "These Products are Not Approved (%s). "
                        "Please Approve all Products before posting Invoice."
                    ) % unapproved)
        return super().action_post()