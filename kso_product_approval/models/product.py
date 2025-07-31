from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('approved', 'Approved'),
    ], string="Approval Stage", default="draft", tracking=True)

    @api.model
    def write(self, vals):
        # Allow only reverting the state back to draft
        for rec in self:
            if rec.state == 'approved':
                # if trying to change anything other than state back to draft → block
                if not (set(vals.keys()) == {'state'} and vals.get('state') == 'draft'):
                    raise UserError(_(
                        "Product '%s' is in Approved stage and cannot be modified."
                    ) % rec.display_name)
        return super().write(vals)

    @api.model
    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(_(
                    "Approved product '%s' cannot be deleted."
                ) % rec.display_name)
        return super().unlink()

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

            # **new**: purchase route check
            if rec.purchase_ok:
                # code = rec.route_ids.filtered(lambda r: r.name == 'Buy')
                required = {'Buy', 'Replenish on Order (MTO)'}
                route_names = set(rec.route_ids.mapped('name'))
                missing = required - route_names
                if missing:
                    raise UserError(_(
                        "Cannot approve '%s': You must enable the following routes under Inventory → Operations:\n• %s"
                    ) % (
                        rec.display_name,
                        "\n• ".join(missing)
                    ))

            rec.state = 'approved'

    def action_draft(self):
        """Reset to Draft from any stage"""
        for rec in self:
            rec.state = 'draft'


class Product(models.Model):
    _inherit = "product.product"

    def action_progress(self):
        return self.product_tmpl_id.action_progress()

    def action_verify(self):
        return self.product_tmpl_id.action_verify()

    def action_draft(self):
        return self.product_tmpl_id.action_draft()

    @api.model
    def write(self, vals):
        for rec in self:
            if rec.state == 'approved':
                if not (set(vals.keys()) == {'state'} and vals.get('state') == 'draft'):
                    raise UserError(_(
                        "Product variant '%s' is in Approved stage and cannot be modified."
                    ) % rec.display_name)
        return super().write(vals)

    @api.model
    def unlink(self):
        for rec in self:
            if rec.state == 'approved':
                raise UserError(_(
                    "Approved variant '%s' cannot be deleted."
                ) % rec.display_name)
        return super().unlink()