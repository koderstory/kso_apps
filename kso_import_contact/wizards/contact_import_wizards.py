# -*- coding: utf-8 -*-
"""
This wizard lets users import contacts from an Excel file and download a sample template.
"""

import base64
import io
import openpyxl
from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ContactImportWizard(models.TransientModel):
    _name = 'contact.import.wizard'
    _description = 'Import Contacts Wizard'

    file = fields.Binary(string="Upload Excel File", required=True)
    filename = fields.Char(string="Filename")

    def action_import_contacts(self):
        self.ensure_one()

        if not self.file:
            raise UserError(_("Please upload a file."))

        # Decode and load the workbook
        try:
            file_data = base64.b64decode(self.file)
            workbook = openpyxl.load_workbook(io.BytesIO(file_data))
            sheet = workbook.active
        except Exception as e:
            raise UserError(_("Failed to read Excel file: %s") % str(e))

        # Normalize headers: lower-case, strip, replace spaces with underscores
        headers = [
            str(cell.value).strip().lower().replace(' ', '_')
            for cell in sheet[1]
        ]

        contacts = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            contact = dict(zip(headers, row))
            contacts.append(contact)

        for data in contacts:
            name = data.get('name')
            code = data.get('code') or False

            # Parse boolean flags
            is_vendor = str(data.get('is_vendor')).strip().lower() in ['1', 'true', 'yes']
            is_customer = str(data.get('is_customer')).strip().lower() in ['1', 'true', 'yes']

            # Prepare values (always set ranks)
            vals = {
                'name': name,
                'street': data.get('address'),
                'phone': data.get('phone'),
                'mobile': data.get('mobile'),
                'email': data.get('email'),
                'website': data.get('website'),
                'supplier_rank': 1 if is_vendor else 0,
                'customer_rank': 1 if is_customer else 0,
            }
            if code:
                vals['ref'] = code

            # Build search domain, excluding system users
            domain = [('user_ids', '=', False)]
            if code:
                domain.append(('ref', '=', code))
            else:
                domain.append(('name', '=', name))

            partner = self.env['res.partner'].search(domain, limit=1)
            if partner:
                partner.write(vals)
            else:
                self.env['res.partner'].create(vals)

        return {'type': 'ir.actions.act_window_close'}

    def action_download_template(self):
        """
        Returns an action that downloads a predefined Excel template.
        Place the template file at: static/description/DEMO_CONTACT.xlsx
        """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': base_url + '/kso_import_contact/static/description/DEMO_CONTACT.xlsx?download=true',
            'target': 'self',
        }
