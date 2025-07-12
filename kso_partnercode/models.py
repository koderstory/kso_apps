from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string='Is Customer', default=False)
    is_vendor = fields.Boolean(string='Is Vendor', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        # Ensure boolean flags reflect customer/vendor ranks on create
        for vals in vals_list:
            # If partner is marked as supplier (vendor) by supplier_rank, set is_vendor
            if vals.get('supplier_rank', 0) and not vals.get('is_vendor'):
                vals['is_vendor'] = True
            # If partner is marked as customer by customer_rank, set is_customer
            if vals.get('customer_rank', 0) and not vals.get('is_customer'):
                vals['is_customer'] = True
        return super(ResPartner, self).create(vals_list)

    @api.onchange('supplier_rank')
    def _onchange_supplier_rank(self):
        for rec in self:
            rec.is_vendor = rec.supplier_rank > 0

    @api.onchange('customer_rank')
    def _onchange_customer_rank(self):
        for rec in self:
            rec.is_customer = rec.customer_rank > 0