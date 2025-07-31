from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('approved', 'Approved'),
    ], string="Approval Stage", default="draft", tracking=True)

    def action_progress(self):
        """Move Draft → Progress (Product Progress only)"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only Draft products can be sent to Progress."))
            rec.state = 'progress'

    def action_verify(self):
        """Move Progress → Approved (Product Manager only)"""
        for rec in self:
            if rec.state != 'progress':
                raise UserError(_("Product must be in Progress stage first."))
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

    def action_progress(self):
        return self.product_tmpl_id.action_source()

    def action_verify(self):
        return self.product_tmpl_id.action_verify()

    def action_draft(self):
        return self.product_tmpl_id.action_draft()