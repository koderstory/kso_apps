from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_type = fields.Selection(
        [
            ('local', 'Local'),
            ('export', 'Export'),
        ],
        string='Shipping',
        default='local',
        required=True,
    )

    # ─── STATES ────────────────────────────────────────────────────────────────
    state = fields.Selection(
        selection_add=[('proforma', 'Pro Forma Invoice'), ('sale', 'Sales Order')],
        ondelete={'proforma': 'set default'},
        copy=False,
        tracking=3,
    )

    # ─── NEW CODE FIELDS ──────────────────────────────────────────────────────
    code_quotation   = fields.Char(string="Quotation Code",    copy=False)
    code_pi          = fields.Char(string="Pro Forma Code",    copy=False)
    code_salesorder  = fields.Char(string="Sales Order Code",  copy=False)

    # ─── QUOTATION: name + code on create ────────────────────────────────────
    @api.model
    def create(self, vals):
        # only auto‑name & set code if no explicit name given
        if not vals.get('name') or vals.get('name') in ('/', False, ''):
            # compute SO<YY>-<00001…>
            if vals.get('code_quotation'):
                vals['name'] = vals['code_quotation']
            else:
                today = fields.Date.context_today(self)
                date_obj = (
                    today if not isinstance(today, str)
                    else datetime.strptime(today, '%Y-%m-%d').date()
                )
                yy = date_obj.strftime('%y')
                year_start = datetime(date_obj.year, 1, 1)
                year_end   = year_start + relativedelta(years=1)
                count = self.search_count([
                    ('create_date', '>=', year_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<',  year_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                name = f"SO{yy}-{count:05d}"
                vals.update({
                    'name': name,
                    'code_quotation': name,
                })
        return super().create(vals)

    # ─── PRO FORMA: name + code when you click Pro Forma ──────────────────────
    def action_proforma(self):
        for order in self:
            partner_code = order.partner_id.partner_code
            if not partner_code:
                raise UserError("Please set a Partner Code on the customer before generating Pro Forma.")
            # build PI-<CODE>-YYYYMM-0001…
            if order.code_pi:
                code = order.code_pi
            else:
                dt = order.create_date or fields.Datetime.now()
                dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT) if isinstance(dt, str) else dt
                m_start = dt.replace(day=1, hour=0, minute=0, second=0)
                m_end   = m_start + relativedelta(months=1)
                count = self.search_count([
                    ('id', '!=', order.id),
                    ('state', '=', 'proforma'),
                    ('create_date', '>=', m_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<',  m_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                code = f"PI-{partner_code}-{dt.strftime('%Y%m')}-{count:04d}"
                order.code_pi = code
            # set name & state
            order.write({
                'name': code,
                'state': 'proforma',
            })
        return True

    # ─── SALES ORDER: name + code on confirm ─────────────────────────────────
    def action_confirm(self):
        valid = self.filtered(lambda o: o.state in ('sent', 'proforma'))
        invalid = (self - valid)
        if invalid:
            raise UserError("Some orders are not in a state requiring confirmation.")
        # allow super() by moving proforma→sent
        pro = valid.filtered(lambda o: o.state == 'proforma')
        if pro:
            pro.write({'state': 'sent'})
        # set sales‑order code if empty
        for order in valid:
            if order.code_salesorder:
                code = order.code_salesorder
                order.write({'name': code})
            else:
                # P<L/E><YY>-0001…
                ship = 'L' if order.shipping_type == 'local' else 'E'
                today = fields.Date.context_today(order)
                dobj = (
                    today if not isinstance(today, str)
                    else datetime.strptime(today, '%Y-%m-%d').date()
                )
                yy = dobj.strftime('%y')
                y_start = datetime(dobj.year, 1, 1)
                y_end   = y_start + relativedelta(years=1)
                cnt = self.search_count([
                    ('code_salesorder', '!=', False),
                    ('create_date', '>=', y_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<',  y_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                code = f"P{ship}{yy}-{cnt:04d}"
                order.write({
                    'name': code,
                    'code_salesorder': code,
                })
        return super(SaleOrder, valid).action_confirm()

    def write(self, vals):
        # only check confirmed orders
        confirmed = self.filtered(lambda o: o.state=='sale')
        if confirmed:
            locked = {'payment_term_id','shipping_type','order_line'} & set(vals)
            if locked:
                raise UserError(f"You cannot modify {', '.join(locked)} once the order is confirmed.")
        return super().write(vals)