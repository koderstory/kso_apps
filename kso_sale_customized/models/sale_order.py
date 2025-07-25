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

    # add SQL constraints for code uniqueness
    _sql_constraints = [
        ('code_quotation_unique', 'unique(code_quotation)', 'Quotation code must be unique!'),
        ('code_pi_unique', 'unique(code_pi)', 'Pro Forma code must be unique!'),
        ('code_salesorder_unique', 'unique(code_salesorder)', 'Sales Order code must be unique!'),
    ]

    # ─── TEMPLATE STATES ───────────────────────────────────────────────────
    state = fields.Selection(
        selection_add=[('proforma', 'Pro Forma Invoice'), ('sale', 'Sales Order')],
        ondelete={'proforma': 'set default'},
        copy=False,
        tracking=3,
    )

    # code fields
    code_quotation = fields.Char(string="Quotation Code", copy=False)
    code_pi = fields.Char(string="Pro Forma Code", copy=False)
    code_salesorder = fields.Char(string="Sales Order Code", copy=False)

    @api.model
    def create(self, vals):
        # auto-name quotation if name not provided
        if not vals.get('name') or vals['name'] in ('/', False, ''):
            if not vals.get('code_quotation'):
                today = fields.Date.context_today(self)
                dt = datetime.strptime(today, '%Y-%m-%d').date() if isinstance(today, str) else today
                yy = dt.strftime('%y')
                y_start = datetime(dt.year, 1, 1)
                y_end = y_start + relativedelta(years=1)
                # count quotations this year
                count = self.search_count([
                    ('create_date', '>=', y_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<', y_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                name = f"SO{yy}-{count:05d}"
                vals['name'] = name
                vals['code_quotation'] = name
        return super().create(vals)

    def action_proforma(self):
        for order in self:
            partner_code = order.partner_id.partner_code
            if not partner_code:
                raise UserError("Please set a Partner Code on the customer before generating Pro Forma.")
            if not order.code_pi:
                dt = order.create_date or fields.Datetime.now()
                dt = datetime.strptime(dt, DEFAULT_SERVER_DATETIME_FORMAT) if isinstance(dt, str) else dt
                m_start = dt.replace(day=1, hour=0, minute=0, second=0)
                m_end = m_start + relativedelta(months=1)
                # count all PIs in the same month, regardless of state
                count = self.search_count([
                    ('id', '!=', order.id),
                    ('code_pi', '!=', False),
                    ('create_date', '>=', m_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<',  m_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                order.code_pi = f"PI-{partner_code}-{dt.strftime('%Y%m')}-{count:04d}"
            order.write({'name': order.code_pi, 'state': 'proforma'})
        return True

    def action_confirm(self):
        valid = self.filtered(lambda o: o.state in ('sent', 'proforma'))
        if (self - valid):
            raise UserError("Some orders are not in a state requiring confirmation.")
        # move proforma to sent
        pro = valid.filtered(lambda o: o.state == 'proforma')
        if pro:
            pro.write({'state': 'sent'})

        for order in valid:
            if not order.code_salesorder:
                ship_code = 'L' if order.shipping_type == 'local' else 'E'
                today = fields.Date.context_today(order)
                dt = datetime.strptime(today, '%Y-%m-%d').date() if isinstance(today, str) else today
                yy = dt.strftime('%y')
                y_start = datetime(dt.year, 1, 1)
                y_end = y_start + relativedelta(years=1)
                # count SO for this shipping type and year
                count = self.search_count([
                    ('code_salesorder', '!=', False),
                    ('shipping_type', '=', order.shipping_type),
                    ('create_date', '>=', y_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    ('create_date', '<', y_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ]) + 1
                new_code = f"P{ship_code}{yy}-{count:04d}"
                order.write({'code_salesorder': new_code, 'name': new_code})
            else:
                order.write({'name': order.code_salesorder})

        return super(SaleOrder, valid).action_confirm()

    def write(self, vals):
        confirmed = self.filtered(lambda o: o.state == 'sale')
        if confirmed:
            locked = {'payment_term_id', 'shipping_type', 'order_line'} & set(vals)
            if locked:
                raise UserError(f"You cannot modify {', '.join(locked)} once the order is confirmed.")
        return super().write(vals)
