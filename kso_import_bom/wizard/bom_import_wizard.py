import base64
import io
import logging

import openpyxl
from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class BomImportWizard(models.TransientModel):
    _name = 'bom.import.wizard'
    _description = 'BoM Import Wizard'

    file = fields.Binary('Excel File', required=True)
    filename = fields.Char('File Name')

    def action_import_bom(self):
        if not self.file:
            raise UserError(_("Please upload an Excel file."))

        # 1) Load workbook & read rows
        data = base64.b64decode(self.file)
        wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
        sheet = wb.active
        rows = [list(r) for r in sheet.iter_rows(values_only=True)]
        if not rows:
            raise UserError(_("Worksheet is empty."))

        # 2) Parse Header (key:value until first non‑key row)
        header = {}
        idx = 0
        while idx < len(rows):
            row = rows[idx]
            if row and isinstance(row[0], str) and ':' in row[0]:
                key = row[0].split(':', 1)[0].strip().lower()
                val = row[1] if len(row) > 1 else ''
                header[key] = val
                idx += 1
            else:
                break

        if not header.get('name'):
            raise UserError(_("Header missing “name:” value."))
        product_name = header['name']
        bom_qty      = float(header.get('qty') or 1.0)
        bom_type     = (header.get('type') or '').strip() or 'normal'

        # 3) Move to Components header
        while idx < len(rows) and not any(rows[idx]):
            idx += 1
        if idx >= len(rows) or not rows[idx] or \
           not str(rows[idx][0]).strip().lower().startswith('component code'):
            raise UserError(_("Cannot find “Components” table header."))
        comp_header = [str(c).strip().lower() for c in rows[idx]]
        idx += 1

        comp_map = {name: i for i, name in enumerate(comp_header)}
        for col in ('component code', 'component name', 'qty'):
            if col not in comp_map:
                raise UserError(_("Components header missing “%s” column.") % col)

        # 4) Parse Components
        comps = []
        while idx < len(rows) and any(rows[idx]):
            row = rows[idx]
            comps.append({
                'code': row[comp_map['component code']],
                'name': row[comp_map['component name']],
                'qty':  float(row[comp_map['qty']] or 0),
            })
            idx += 1

        # 5) Move to Operations header (if present)
        while idx < len(rows) and not any(rows[idx]):
            idx += 1
        ops = []
        if idx < len(rows) and rows[idx] and \
           str(rows[idx][0]).strip().lower().startswith('operation'):
            op_header = [str(c).strip().lower() for c in rows[idx]]
            idx += 1
            op_map = {name: i for i, name in enumerate(op_header)}
            for col in ('operation', 'work center', 'duration'):
                if col not in op_map:
                    raise UserError(_("Operations header missing “%s” column.") % col)
            while idx < len(rows) and any(rows[idx]):
                row = rows[idx]
                ops.append({
                    'operation':  row[op_map['operation']],
                    'workcenter': row[op_map['work center']],
                    'duration':   float(row[op_map['duration']] or 0),
                })
                idx += 1

        # 6) Find/Create main product & BoM
        product = self.env['product.product'].search(
            [('name', '=', product_name)], limit=1
        )
        if not product:
            product = self.env['product.product'].create({'name': product_name})

        bom = self.env['mrp.bom'].search([
            ('product_tmpl_id', '=', product.product_tmpl_id.id),
            ('type', '=', bom_type),
        ], limit=1)
        if not bom:
            bom = self.env['mrp.bom'].create({
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_qty':     bom_qty,
                'product_uom_id':  product.uom_id.id,
                'type':            bom_type,
            })

        # 7) Create component lines
        imported = skipped = failed = 0
        errors = []
        Uom = self.env['uom.uom']
        for comp in comps:
            code = comp['code']
            if not code:
                skipped += 1
                continue
            try:
                cprod = self.env['product.product'].search(
                    [('default_code', '=', code)], limit=1
                )
                if not cprod:
                    cprod = self.env['product.product'].create({
                        'name':         comp['name'],
                        'default_code': code,
                    })

                # 1) Determine line_uom_id
                if comp.get('uom'):
                    # try to find a UoM by name or by lookup
                    u = Uom.search([('name','=', comp['uom'])], limit=1)
                    if not u:
                        raise UserError(_("Unknown UoM “%s” for component %s") %
                                        (comp['uom'], code))
                    line_uom_id = u.id
                else:
                    # fallback to the product’s own UoM
                    line_uom_id = cprod.uom_id.id

                # 2) Create line
                self.env['mrp.bom.line'].create({
                    'bom_id':        bom.id,
                    'product_id':    cprod.id,
                    'product_qty':   comp['qty'],
                    'product_uom_id': line_uom_id,
                })
                imported += 1
            except Exception as e:
                _logger.exception("Component import error")
                failed += 1
                errors.append(f"{code}: {e}")

        # 8) Write Operations onto the BoM, auto-creating missing WCs
        if ops:
            WC = self.env['mrp.workcenter']
            ops_vals = []
            seq = 1
            for o in ops:
                wc = WC.search([('name', '=', o['workcenter'])], limit=1)
                if not wc:
                    wc = WC.create({'name': o['workcenter']})
                ops_vals.append((0, 0, {
                    'name':              o['operation'],
                    'workcenter_id':     wc.id,
                    'sequence':          seq,
                    'time_cycle_manual': o['duration'],
                }))
                seq += 1
            if ops_vals:
                bom.write({'operation_ids': ops_vals})

        # 9) Final result
        msg = _("%(imp)s imported, %(skp)s skipped, %(err)s errors") % {
            'imp': imported, 'skp': skipped, 'err': failed
        }
        if errors:
            msg += "\n" + "\n".join(errors)

        if skipped or failed:
            raise UserError(msg)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title':   _('BoM Import Successful'),
                'message': msg,
                'type':    'success',
                'duration': 3000,
                'sticky':  False,
                'on_close': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
