from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sourcing', 'Sourcing'),
        ('approved', 'Approved'),
    ], string="Approval Stage", default="draft", tracking=True)

    def action_source(self):
        """Move Draft → Sourcing (Product Sourcing only)"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only Draft products can be sent to Sourcing."))
            rec.state = 'sourcing'

    def action_verify(self):
        """Move Sourcing → Approved (Product Manager only)"""
        for rec in self:
            if rec.state != 'sourcing':
                raise UserError(_("Product must be in Sourcing stage first."))
            # existing validations:
            if rec.purchase_ok and not rec.standard_price:
                raise UserError(_(
                    "Cannot approve '%s': Cost price is not set."
                ) % rec.display_name)
            if rec.purchase_ok and not rec.seller_ids:
                raise UserError(_(
                    "Cannot approve '%s': No supplier defined."
                ) % rec.display_name)
            if rec.sale_ok and not rec.list_price:
                raise UserError(_(
                    "Cannot approve '%s': Sales price is not set."
                ) % rec.display_name)
            rec.state = 'approved'

    def action_draft(self):
        """Reset to Draft from any stage"""
        for rec in self:
            rec.state = 'draft'


class Product(models.Model):
    _inherit = "product.product"

    def action_source(self):
        return self.product_tmpl_id.action_source()

    def action_verify(self):
        return self.product_tmpl_id.action_verify()

    def action_draft(self):
        return self.product_tmpl_id.action_draft()