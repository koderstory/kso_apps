from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    list_price = fields.Float(
        'Sales Price',
        digits='Product Price',
        help="Sales price for this specific variant.")
    
    @api.onchange('list_price')
    def update_template_price(self):
        if self.list_price != self.product_tmpl_id.list_price:
            self.product_tmpl_id.list_price = self.list_price
            
            
# class ProductTemplate(models.Model):
#     _inherit = "product.template"

#     def _get_combination_info(self, combination, product_id, add_qty, pricelist, **kwargs):
#         """
#         Override to ensure the variant's sales price is shown on the website.
#         """
#         combination_info = super(ProductTemplate, self)._get_combination_info(
#             combination, product_id, add_qty, pricelist, **kwargs
#         )
        
#         # Get the specific variant
#         variant = self.env['product.product'].browse(combination['product_id'])
        
#         # Override the combination's list price with the variant's list_price
#         combination_info['list_price'] = variant.list_price
        
#         return combination_info
    
