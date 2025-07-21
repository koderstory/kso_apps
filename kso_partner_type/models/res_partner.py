from odoo import models, fields, api

# class ResPartner(models.Model):
#     _inherit = 'res.partner'

    # is_customer = fields.Boolean(
    #     string='Customer',
    #     compute='_compute_is_customer',
    #     store=True,
    # )
    # is_vendor = fields.Boolean(
    #     string='Vendor',
    #     compute='_compute_is_vendor',
    #     store=True,
    # )

    # @api.depends('customer_rank')
    # def _compute_is_customer(self):
    #     for partner in self:
    #         partner.is_customer = partner.customer_rank > 0

    # @api.depends('supplier_rank')
    # def _compute_is_vendor(self):
    #     for partner in self:
    #         partner.is_vendor = partner.supplier_rank > 0
