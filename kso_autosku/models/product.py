from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    # Make the field label show as "SKU" everywhere (forms, lists, etc)
    default_code = fields.Char(string="SKU")

    # --- Manual button on the template form ---
    def action_generate_sku(self):
        for template in self:
            template._ensure_category_code()
            template._generate_default_code_if_missing()
            template._generate_variants_codes()
            try:
                template.message_post(body="SKU generated for template and variants.")
            except Exception:
                pass
        return True

    # --- Helpers ---
    def _ensure_category_code(self):
        for t in self:
            if not t.categ_id:
                raise ValidationError("Please set a Product Category before generating SKU.")
            # requires a custom 'code' char field on product.category
            if not getattr(t.categ_id, 'code', False):
                raise ValidationError("Please set a Category Code on the Product Category before generating SKU.")

    def _generate_default_code_if_missing(self):
        """Generate template default_code only if it's empty."""
        for template in self:
            if template.default_code:
                continue
            category_code = template.categ_id.code

            # Find existing with same prefix
            existing = self.search([('default_code', 'like', f"{category_code}-%")])
            last_number = 0
            for prod in existing:
                parts = (prod.default_code or '').split('-')
                if len(parts) > 1 and parts[1].isdigit():
                    last_number = max(last_number, int(parts[1]))

            template.default_code = f"{category_code}-{last_number + 1:05d}"

    def _generate_variants_codes(self):
        """Generate/refresh codes for each variant under this template."""
        for template in self:
            for variant in template.product_variant_ids:
                variant._generate_variant_default_code()


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    # keep readonly in UI; label as SKU
    default_code = fields.Char(string="SKU", readonly=True)

    # --- Manual button on the variant form ---
    def action_generate_sku(self):
        for variant in self:
            template = variant.product_tmpl_id
            template._ensure_category_code()
            template._generate_default_code_if_missing()
            variant._generate_variant_default_code()
            try:
                variant.message_post(body="SKU generated for this variant.")
            except Exception:
                pass
        return True

    # --- Bulk actions (Actions menu on list view) ---
    def action_batch_generate_sku(self, skip_existing=False, overwrite=False):
        """
        Process selected variants.
        - Only variants with a category (categ_id) are processed; others skipped.
        - skip_existing=True -> leave variants that already have default_code
        - overwrite=True     -> clear default_code first then regenerate
        """
        eligible = self.filtered(lambda p: p.categ_id)
        processed = 0
        for p in eligible:
            if skip_existing and p.default_code:
                continue
            if overwrite:
                p.default_code = False

            tmpl = p.product_tmpl_id
            tmpl._ensure_category_code()
            tmpl._generate_default_code_if_missing()
            p._generate_variant_default_code()
            processed += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "SKU Generation",
                "message": f"Processed {processed} of {len(self)} selected (only those with Category).",
                "sticky": False,
            },
        }

    # --- Helper for variants ---
    def _generate_variant_default_code(self):
        for variant in self:
            template = variant.product_tmpl_id
            base = template.default_code or ''
            attribute_values = variant.product_template_attribute_value_ids

            if attribute_values:
                # Build short code from THIS variant's values (in a stable order)
                ordered = attribute_values.sorted(
                    key=lambda x: (x.attribute_id.sequence, x.product_attribute_value_id.sequence)
                )
                pieces = []
                for av in ordered:
                    sc = ''.join(word[:2].upper() for word in (av.name or '').split())
                    pieces.append(sc)
                variant_code = '-'.join([p for p in pieces if p])
                base_default_code = f"{base}-{variant_code}" if variant_code else base
            else:
                base_default_code = base

            # Ensure uniqueness; append numeric suffix if needed
            unique = base_default_code
            suffix = 1
            Product = self.sudo()  # safe search
            while Product.search([('id', '!=', variant.id), ('default_code', '=', unique)], limit=1):
                unique = f"{base_default_code}-{suffix}"
                suffix += 1

            variant.default_code = unique
