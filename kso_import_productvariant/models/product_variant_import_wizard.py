# -*- coding: utf-8 -*-
"""
This module defines the Product Variant Import Wizard.
It provides a wizard form where the user can upload an Excel file
containing product and variant data, and includes a button to download
a sample template file.
"""

import base64
import io
import openpyxl
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Import the main helper function from the helper file.
from .import_variant_helpers import add_or_update_product_with_variants

_logger = logging.getLogger(__name__)


class ProductVariantImportWizard(models.TransientModel):
    """
    Transient Model for importing product variants from an Excel file.
    
    This wizard lets the user select an Excel file, which is then processed
    to update or create product templates and their associated variants.
    It also includes functionality to download a sample/template file.
    """
    _name = "kso.import.productvariant.wizard"
    _description = "Product Variant Import Wizard"

    file = fields.Binary(string="File", required=True)
    filename = fields.Char(string="Filename")

    def action_import_productvariant(self):
        """
        Import product variants from the provided Excel file.
        
        The method performs the following steps:
          1. Validates and decodes the uploaded Base64 file data.
          2. Loads the Excel workbook using openpyxl.
          3. Reads header and data rows to form a list of dictionaries.
          4. Calls the helper function to process and update products/variants.
          5. Closes the wizard window upon successful import.
        
        :raises UserError: If any step of the import process fails.
        :return: An action to close the wizard view.
        """
        self.ensure_one()

        if not self.file:
            raise UserError(_("Please provide a file to import."))

        try:
            file_data = base64.b64decode(self.file)
        except Exception:
            raise UserError(_("The file could not be decoded. Please try again."))

        try:
            workbook = openpyxl.load_workbook(io.BytesIO(file_data))
            sheet = workbook.active
        except Exception as e:
            raise UserError(_("Error reading Excel file: %s") % str(e))

        headers = [str(cell.value).strip().lower() if cell.value else '' for cell in sheet[1]]
        product_data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            product = dict(zip(headers, row))
            product_data.append(product)

        _logger.info("Product import data: %s", product_data)

        try:
            add_or_update_product_with_variants(self.env, product_data)
        except Exception as e:
            raise UserError(_("Import failed: %s") % e)

        return {'type': 'ir.actions.act_window_close'}

    def action_download_template(self):
        """
        Provide a download link for the sample product variant Excel template.
        
        This method returns an action that directs the user to the URL of
        the static template file. Ensure the file is located at:
            static/description/PRODUCTS_VARIANTS.xlsx
        
        :return: An action of type 'ir.actions.act_url' to download the template.
        """
        # Retrieve the base URL configured in Odoo.
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            # Concatenate the base URL with your relative static file path.
            'url': base_url + '/kso_import_productvariant/static/description/PRODUCTS_VARIANTS.xlsx?download=true',
            'target': 'self',
        }
