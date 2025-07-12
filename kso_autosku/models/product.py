from odoo import models, fields, api, exceptions
import itertools
from odoo.exceptions import ValidationError


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        templates = super(CustomProductTemplate, self).create(vals_list)
        for template in templates:
            self._generate_default_code(template)
        return templates

    def write(self, vals):
        result = super(CustomProductTemplate, self).write(vals)
        for template in self:
            # Regenerate default code only if category has changed
            if 'categ_id' in vals and template.categ_id and template.categ_id.code:
                self._generate_default_code(template)
        return result

    def _generate_default_code(self, template):
        if not template.default_code and template.categ_id and template.categ_id.code:
            category_code = template.categ_id.code

            # Find existing products with matching category code pattern
            existing_products = self.search(
                [('default_code', 'like', f"{category_code}-%")]
            )

            # Determine the highest number from existing product codes
            last_number = 0
            for product in existing_products:
                parts = product.default_code.split('-')
                if len(parts) > 1 and parts[1].isdigit():
                    number = int(parts[1])
                    last_number = max(last_number, number)

            # Assign the new default code
            template.default_code = f"{category_code}-{last_number + 1:05d}"


class CustomProductProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        products = super(CustomProductProduct, self).create(vals_list)
        for variant in products:
            self._generate_variant_default_code(variant)
        return products

    def write(self, vals):
        result = super(CustomProductProduct, self).write(vals)
        for variant in self:
            # Regenerate default code only if category has changed
            if 'product_tmpl_id' in vals:
                self._generate_variant_default_code(variant)
        return result

    def _generate_variant_default_code(self, variant):
        template = variant.product_tmpl_id

        # Generate template default_code if it doesn't exist
        if not template.default_code:
            template._generate_default_code(template)

        # Generate variant codes based on attribute values
        attribute_values = variant.product_template_attribute_value_ids
        if attribute_values:
            # Group attribute values by attribute
            attribute_groups = {}
            for av in attribute_values:
                attribute_groups.setdefault(av.attribute_id.id, []).append(av.name)

            # Generate all combinations of attribute values
            attribute_combinations = list(itertools.product(
                *[attribute_groups[attr_id] for attr_id in attribute_groups]
            ))

            # Generate variant codes for each combination
            for combination in attribute_combinations:
                short_codes = [''.join(word[:2].upper() for word in value.split()) for value in combination]
                variant_code = '-'.join(short_codes)

                # Combine with template.default_code
                base_default_code = f"{template.default_code}-{variant_code}"

                # Ensure uniqueness
                unique_code = base_default_code
                suffix = 1
                while self.search([('default_code', '=', unique_code)], limit=1):
                    unique_code = f"{base_default_code}-{suffix}"
                    suffix += 1

                variant.default_code = unique_code
        else:
            # No attributes: use the template default_code
            variant.default_code = template.default_code