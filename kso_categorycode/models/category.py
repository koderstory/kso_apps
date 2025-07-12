from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CustomCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char("Category Code", help="Code for category")
    display_name = fields.Char(compute='_compute_display_name')

    # @api.depends('code', 'name')
    # def _compute_display_name(self):
    #     for record in self:
    #         code = (record.code or "").strip()
    #         if code:
    #             record.display_name = f"[{code}] {record.name or ''}"
    #         else:
    #             record.display_name = record.name or ''

            
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Ensure a code is provided in the `vals`
            # if 'code' not in vals or not vals['code']:
            #     raise ValidationError("You must provide a code for the category.")

            # Check if the category has a parent
            parent_id = vals.get('parent_id')
            if parent_id:
                parent_category = self.browse(parent_id)
                # if not parent_category.code:
                #     raise ValidationError(
                #         "The parent category must have a 'code' to generate a combined code."
                #     )

                # Combine parent code with the current category's code
                if parent_category.code:
                    vals['code'] = f"{parent_category.code}{vals['code']}"

        return super(CustomCategory, self).create(vals_list)
