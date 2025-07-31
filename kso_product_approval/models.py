from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    state = fields.Selection([
        ('draft','Draft'),
        ('approved', 'Approved')
    ], string="Approve Status", default="draft", tracking=True)

    def action_verify(self):
        for rec in self:
            # check cost price for purchasable products
            if rec.purchase_ok and not rec.standard_price:
                raise UserError(_(
                    "Cannot approve '%s': Cost price is not set. "
                    "Please enter a Standard Cost before approval."
                ) % rec.display_name)

            # ensure at least one supplier if purchasable
            if rec.purchase_ok and not rec.seller_ids:
                raise UserError(_(
                    "Cannot approve '%s': No supplier defined. "
                    "Please add at least one supplier before approval."
                ) % rec.display_name)

            # check list price for saleable products
            if rec.sale_ok and not rec.list_price:
                raise UserError(_(
                    "Cannot approve '%s': Sales price is not set. "
                    "Please enter a Sales Price before approval."
                ) % rec.display_name)

            rec.state = 'approved'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'


class Product(models.Model):
    _inherit = "product.product"

    def action_verify(self):
        for rec in self:
            # use template values if needed
            template = rec.product_tmpl_id
            if template.purchase_ok and not template.standard_price:
                raise UserError(_(
                    "Cannot approve variant '%s': Cost price on template '%s' is not set."
                ) % (rec.display_name, template.display_name))

            # supplier defined on template
            if template.purchase_ok and not template.seller_ids:
                raise UserError(_(
                    "Cannot approve variant '%s': No supplier defined on template '%s'."
                ) % (rec.display_name, template.display_name))
            
            if template.sale_ok and not template.list_price:
                raise UserError(_(
                    "Cannot approve variant '%s': Sales price on template '%s' is not set."
                ) % (rec.display_name, template.display_name))

            rec.state = 'approved'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'


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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for rec in self:
            unapproved = ", ".join(
                line.product_id.name
                for line in rec.move_line_ids
                if line.product_id and line.product_id.state != 'approved')
            if unapproved:
                raise UserError(_(
                    "These Products are Not Approved (%s). "
                    "Please Approve all Products before validating Picking."
                ) % unapproved)
        return super().button_validate()