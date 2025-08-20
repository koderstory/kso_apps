# -*- coding: utf-8 -*-
"""
Odoo 18–compatible helpers for importing product templates & variants from Excel-like rows.

Key notes:
- Uses stock.quants to set on-hand qty at an internal location (see get_default_internal_location()).
- No custom fields (e.g., is_storable, lot_valuated, fix_price). Add back if they exist in your DB.
- Disables auto variant creation via create_variant='no_variant'.
"""

import logging
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# ---------------------------
# Basic lookups / creations
# ---------------------------

def get_or_create_uom(env, uom_name):
    if not uom_name:
        return None
    uom = env['uom.uom'].search([('name', '=ilike', uom_name)], limit=1)
    if not uom:
        raise UserError(_("Unit of Measure '%s' not found.") % uom_name)
    return uom.id


def get_or_create_category(env, category_path):
    if not category_path:
        return None
    names = [n.strip() for n in category_path.split('/') if n.strip()]
    parent = None
    for name in names:
        parent_id = parent.id if parent else False
        cat = env['product.category'].search([
            ('name', '=ilike', name),
            ('parent_id', '=', parent_id),
        ], limit=1)
        if not cat:
            cat = env['product.category'].create({'name': name, 'parent_id': parent_id})
        parent = cat
    return parent.id


# ---------------------------
# Attributes & variants
# ---------------------------

def get_or_create_template_attribute_value(env, template, attribute, attr_val):
    ptav = env['product.template.attribute.value'].search([
        ('product_tmpl_id', '=', template.id),
        ('product_attribute_value_id', '=', attr_val.id)
    ], limit=1)
    if not ptav:
        ptav = env['product.template.attribute.value'].create({
            'product_tmpl_id': template.id,
            'product_attribute_id': attribute.id,
            'product_attribute_value_id': attr_val.id,
        })
    return ptav


def disable_variant_auto_creation(env, template):
    # Modern Odoo: selection field 'create_variant' supports 'no_variant'
    if 'create_variant' in template._fields:
        template.write({'create_variant': 'no_variant'})
    else:
        _logger.warning("Template lacks 'create_variant' field; cannot disable auto variant creation.")


def _attr_get_or_create(env, name):
    rec = env['product.attribute'].search([('name', '=ilike', name)], limit=1)
    return rec or env['product.attribute'].create({'name': name})


def _attr_value_get_or_create(env, attribute, value):
    rec = env['product.attribute.value'].search([
        ('name', '=ilike', value),
        ('attribute_id', '=', attribute.id)
    ], limit=1)
    return rec or env['product.attribute.value'].create({'name': value, 'attribute_id': attribute.id})


def setup_template_attributes(env, template, all_variants):
    """
    Build attribute lines from 'variant' strings like "Color:Red, Size:M".
    Returns dict[attr_key_lower][value_key_lower] = product.attribute.value record
    """
    bucket = {}
    for product in all_variants:
        vstr = (product.get('variant') or '').strip()
        if not vstr:
            continue
        for part in vstr.split(','):
            if ':' in part:
                a, v = part.split(':', 1)
                a_key = a.strip().lower()
                v_key = v.strip().lower()
                bucket.setdefault(a_key, {})
                # keep any display form we saw
                bucket[a_key].setdefault(v_key, (a.strip(), v.strip()))

    attr_map = {}
    for a_key, values in bucket.items():
        disp_attr = next(iter(values.values()))[0] if values else a_key
        attribute = _attr_get_or_create(env, disp_attr)
        value_ids = []
        attr_map[a_key] = {}
        for v_key, (_disp_a, disp_val) in values.items():
            av = _attr_value_get_or_create(env, attribute, disp_val)
            attr_map[a_key][v_key] = av
            value_ids.append(av.id)

        line = template.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attribute.id)
        if line:
            line.with_context(skip_variant_auto_create=True).write({'value_ids': [(6, 0, value_ids)]})
        else:
            template.with_context(skip_variant_auto_create=True).write({
                'attribute_line_ids': [(0, 0, {
                    'attribute_id': attribute.id,
                    'value_ids': [(6, 0, value_ids)]
                })]
            })
    return attr_map


def _ptav_ids_for_variant(variant):
    return tuple(sorted(variant.product_template_attribute_value_ids.ids))


def _ptav_ids_from_variant_str(env, template, attr_map, variant_str):
    if not variant_str:
        return tuple()
    pairs = {}
    for part in variant_str.split(','):
        if ':' in part:
            a, v = part.split(':', 1)
            pairs[a.strip().lower()] = v.strip().lower()

    ptav_ids = []
    for a_key, v_key in pairs.items():
        av = attr_map.get(a_key, {}).get(v_key)
        if not av:
            _logger.warning("Attribute pair '%s:%s' not found on template %s.", a_key, v_key, template.name)
            continue
        ptav = get_or_create_template_attribute_value(env, template, av.attribute_id, av)
        ptav_ids.append(ptav.id)
    return tuple(sorted(ptav_ids))


def create_variant_manual(env, template, product, attr_map):
    """
    Create/update one variant (product.product) from 'variant' string.
    """
    vstr = (product.get('variant') or '').strip()
    if not vstr:
        return None

    ptav_ids = _ptav_ids_from_variant_str(env, template, attr_map, vstr)

    existing = None
    for v in template.product_variant_ids:
        if _ptav_ids_for_variant(v) == ptav_ids:
            existing = v
            break

    vals = {
        'product_tmpl_id': template.id,
        'product_template_attribute_value_ids': [(6, 0, list(ptav_ids))],
    }

    # Variant pricing: Odoo standard keeps price on template; if you use pricelists or custom fields, set here.
    sale_price = product.get('sale price')
    if sale_price in (None, ''):
        raise UserError(_("No sale price provided for %s") % (product.get('name') or template.name))
    # If you have a custom field (e.g., 'x_variant_price'), uncomment and adjust:
    # try:
    #     vals['x_variant_price'] = float(sale_price)
    # except Exception:
    #     pass

    cost_price = product.get('cost price')
    if cost_price in (None, ''):
        raise UserError(_("No cost price provided for %s") % (product.get('name') or template.name))
    try:
        vals['standard_price'] = float(cost_price)
    except Exception:
        vals['standard_price'] = template.standard_price

    if existing:
        existing.write(vals)
        _logger.info("Updated variant '%s' for template '%s'.", vstr, template.name)
        return existing
    v = env['product.product'].create(vals)
    _logger.info("Created variant '%s' for template '%s'.", vstr, template.name)
    return v


# ---------------------------
# Stock (Odoo 18 via Quants)
# ---------------------------

def get_default_internal_location(env, company=None):
    """Pick an internal stock location to apply inventory (company’s main WH stock if possible)."""
    domain = [('usage', '=', 'internal')]
    if company:
        domain.append(('company_id', 'in', [False, company.id]))
    # Try main warehouse stock first
    wh = env['stock.warehouse'].search([('company_id', '=', company.id if company else env.company.id)], limit=1)
    if wh and wh.lot_stock_id:
        return wh.lot_stock_id
    # Fallback: first internal location
    loc = env['stock.location'].search(domain, limit=1)
    if not loc:
        raise UserError(_("No internal stock location found to apply inventory."))
    return loc


def _get_qty_at_location(env, product, location):
    quants = env['stock.quant'].search([
        ('product_id', '=', product.id),
        ('location_id', 'child_of', location.id),
    ])
    return sum(quants.mapped('quantity'))


def update_variant_stock_quantity(env, variant, quantity, location=None):
    """
    Set on-hand quantity at a location using stock.quant.
    This applies a delta to reach the target quantity.
    """
    location = location or get_default_internal_location(env, variant.company_id or env.company)
    current = _get_qty_at_location(env, variant, location)
    target = float(quantity or 0.0)
    delta = target - current
    if abs(delta) < 1e-6:
        _logger.info("Stock for '%s' already at %.2f; no change.", variant.display_name, target)
        return
    env['stock.quant']._update_available_quantity(variant, location, delta)
    _logger.info("Adjusted stock for '%s' at %s from %.2f to %.2f (delta %.2f).",
                 variant.display_name, location.display_name, current, target, delta)


def clean_up_unwanted_variants(env, template, wanted_variants):
    wanted = { _ptav_ids_for_variant(v) for v in wanted_variants if v }
    to_remove = [v.id for v in template.product_variant_ids if _ptav_ids_for_variant(v) not in wanted]
    total = len(template.product_variant_ids)
    keep = total - len(to_remove)
    if total > 1 and keep >= 1 and to_remove:
        env['product.product'].browse(to_remove).unlink()
        _logger.info("Removed %s unwanted variants from '%s' (ID %s).", len(to_remove), template.name, template.id)
    else:
        _logger.info("Skipping variant cleanup for '%s' (nothing extra or would remove all).", template.name)


def get_tracking_value(is_tracked, tracked_by):
    if not is_tracked:
        return 'none'
    t = (tracked_by or '').strip().lower()
    return t if t in ('lot', 'serial') else 'none'


def _normalize_type(raw):
    s = (raw or 'consu').strip().lower()
    if s in ('product', 'storable', 'stockable'):
        return 'product'
    if s in ('consu', 'consumable'):
        return 'consu'
    if s == 'service':
        return 'service'
    return 'consu'


# ---------------------------
# Main import routine
# ---------------------------

def add_or_update_product_with_variants(env, product_data):
    """
    product_data: list of dict rows
    Required: name, cost price (and sale price if no variants)
    Optional: product code, uom, purchase uom, type, is tracked, tracked by, category, stock quantity, supplier, variant
    """
    groups = {}
    for row in product_data:
        name = (row.get('name') or '').strip()
        if name:
            groups.setdefault(name, {'template_data': row, 'variants': []})
        else:
            if groups:
                last = next(reversed(groups))
                groups[last]['variants'].append(row)
            else:
                _logger.warning("Orphan variant row before any template; skipping.")
                continue

    for template_name, data in groups.items():
        template_data = data['template_data']
        variants = list(data['variants'])

        # Treat template row as a variant row too if it has 'variant'
        if (template_data.get('variant') or '').strip():
            variants.insert(0, template_data)

        # Try find template
        product_code = (template_data.get('product code') or '').strip()
        product_tmpl = None
        if product_code:
            prod = env['product.product'].search([('default_code', '=', product_code)], limit=1)
            if prod:
                product_tmpl = prod.product_tmpl_id
            else:
                _logger.info("Product code '%s' not found — will resolve by name.", product_code)
        if not product_tmpl:
            product_tmpl = env['product.template'].search([('name', '=ilike', template_name)], limit=1)

        # Normalize fields
        uom_value = (template_data.get('uom') or 'Unit').strip()
        purchase_uom_value = (template_data.get('purchase uom') or '').strip() or uom_value
        prod_type = _normalize_type(template_data.get('type'))
        is_tracked = str(template_data.get('is tracked') or '').strip().lower() == 'true'
        tracked_by_val = (template_data.get('tracked by') or '').strip().lower()
        tracking_val = get_tracking_value(is_tracked, tracked_by_val)

        # Validate prices
        cost_cell = template_data.get('cost price')
        if cost_cell in (None, ''):
            raise UserError(_("Missing required field ‘cost price’ for product ‘%s’.") % template_name)
        try:
            standard_price = float(cost_cell)
        except ValueError:
            raise UserError(_("Invalid value in ‘cost price’ for product ‘%s’: ‘%s’ is not a number.")
                            % (template_name, cost_cell))

        vals = {
            'name': template_name,
            'type': prod_type,
            'default_code': product_code or False,
            'standard_price': standard_price,
            'uom_id': get_or_create_uom(env, uom_value),
            'uom_po_id': get_or_create_uom(env, purchase_uom_value),
            'sale_ok': bool(template_data.get('is saleable', True)),
            'purchase_ok': bool(template_data.get('is purchasable', True)),
            'description': (template_data.get('internal notes') or '').strip(),
            'tracking': tracking_val,
        }

        category_name = (template_data.get('category') or '').strip()
        if category_name:
            vals['categ_id'] = get_or_create_category(env, category_name)

        if not variants:
            sale_cell = template_data.get('sale price')
            if sale_cell in (None, ''):
                raise UserError(_("Missing required field ‘sale price’ for product ‘%s’.") % template_name)
            try:
                vals['list_price'] = float(sale_cell)
            except ValueError:
                raise UserError(_("Invalid value in ‘sale price’ for product ‘%s’: ‘%s’ is not a number.")
                                % (template_name, sale_cell))

        # Create/update template
        if not product_tmpl:
            product_tmpl = env['product.template'].create(vals)
            _logger.info("Created product template: %s", template_name)
        else:
            if product_tmpl.product_variant_count > 1:
                vals.pop('list_price', None)  # multi-variant: price via pricelists/variants
            product_tmpl.write(vals)
            _logger.info("Updated product template: %s", template_name)

        product_tmpl = env['product.template'].browse(product_tmpl.id)
        disable_variant_auto_creation(env, product_tmpl)

        # Attributes from variants
        attr_map = setup_template_attributes(env, product_tmpl, variants)

        created_variants = []
        for vdata in variants:
            v = create_variant_manual(env, product_tmpl, vdata, attr_map)
            if v:
                created_variants.append(v)
                v_qty = vdata.get('stock quantity')
                if v_qty not in (None, ''):
                    try:
                        qty_value = float(v_qty)
                    except Exception:
                        qty_value = 0.0
                    update_variant_stock_quantity(env, v, qty_value)

        # Ensure at least one variant exists if no variant specs provided
        if not variants and not product_tmpl.product_variant_ids:
            v = env['product.product'].create({'product_tmpl_id': product_tmpl.id})
            created_variants.append(v)
            t_qty = template_data.get('stock quantity')
            if t_qty not in (None, ''):
                try:
                    qty_value = float(t_qty)
                except Exception:
                    qty_value = 0.0
                update_variant_stock_quantity(env, v, qty_value)
            _logger.info("Created single variant for template: %s", template_name)

        # Template-level stock on first variant (if provided and there are variants)
        if not variants and product_tmpl.product_variant_ids:
            t_qty = template_data.get('stock quantity')
            if t_qty not in (None, ''):
                try:
                    qty_value = float(t_qty)
                except Exception:
                    qty_value = 0.0
                update_variant_stock_quantity(env, product_tmpl.product_variant_ids[0], qty_value)

        # Supplier info
        if template_data.get('is purchasable', True):
            supplier_name = (template_data.get('supplier') or '').strip()
            if supplier_name:
                vendor = env['res.partner'].search([
                    ('name', '=', supplier_name),
                    ('supplier_rank', '>', 0)
                ], limit=1)
                if not vendor:
                    _logger.warning("Supplier '%s' not found; skipping purchase info for %s", supplier_name, template_name)
                else:
                    uom_id = get_or_create_uom(env, uom_value)
                    price = standard_price
                    info = env['product.supplierinfo'].search([
                        ('partner_id', '=', vendor.id),
                        ('product_tmpl_id', '=', product_tmpl.id),
                        ('product_uom', '=', uom_id),
                    ], limit=1)
                    vals_si = {
                        'partner_id':      vendor.id,
                        'product_tmpl_id': product_tmpl.id,
                        'product_uom':     uom_id,
                        'min_qty':         1,
                        'price':           price,
                    }
                    if info:
                        info.write(vals_si)
                    else:
                        env['product.supplierinfo'].create(vals_si)

        # Cleanup extras when real variant data exists
        if any((r.get('variant') or '').strip() for r in variants) and created_variants:
            clean_up_unwanted_variants(env, product_tmpl, created_variants)
        else:
            _logger.info("No variant cleanup for '%s' (no variant data).", template_name)

    # Single commit at the end
    env.cr.commit()
