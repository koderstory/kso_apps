from odoo import models, fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_type = fields.Selection(
        [
            ('local', 'Local'),
            ('export', 'Export'),
        ],
        string='Shipping',
        default='local',
        required=True,
    )

    # Add a new state after 'sent'
    state = fields.Selection(
        selection_add=[('proforma', 'Pro Forma Invoice'), ('sale', 'Sales Order')],
        ondelete={'proforma': 'set default'},
        copy=False,
        tracking=3,
    )

    def action_confirm(self):
        # Split into valid (sent or proforma) vs invalid
        valid = self.filtered(lambda o: o.state in ('sent', 'proforma'))
        invalid = self - valid
        if invalid:
            raise UserError("Some orders are not in a state requiring confirmation.")

        # For any in proforma, temporarily set them to 'sent' so super() will accept them
        proformas = valid.filtered(lambda o: o.state == 'proforma')
        if proformas:
            proformas.write({'state': 'sent'})

        # Now call the original confirm logic on all valid orders
        return super(SaleOrder, valid).action_confirm()

    def action_proforma(self):
        """Button action to switch to Pro Forma Invoice."""
        return self.write({'state': 'proforma'})
