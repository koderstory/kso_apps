from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Add a new state after 'sent'
    state = fields.Selection(
        selection_add=[('proforma', 'Pro Forma Invoice'), ('sale', 'Sales Order')],
        ondelete={'proforma': 'set default'},
        copy=False,
        tracking=3,
    )

    def action_proforma(self):
        """Button action to switch to Pro Forma Invoice."""
        return self.write({'state': 'proforma'})
