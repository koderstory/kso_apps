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

    # Add a new state after 'sent'
    state = fields.Selection(
        selection_add=[('proforma', 'Pro Forma Invoice'), ('sale', 'Sales Order')],
        ondelete={'proforma': 'set default'},
        copy=False,
        tracking=3,
    )

    def action_proforma(self):
        for order in self:
            partner_code = order.partner_id.partner_code
            if not partner_code:
                raise UserError("Please set a Partner Code on the customer before generating Pro Forma.")
            # parse creation date
            create_dt = fields.Datetime.from_string(order.create_date)
            # month window
            month_start = create_dt.replace(day=1, hour=0, minute=0, second=0)
            month_end = month_start + relativedelta(months=1)
            # count existing proformas this month
            count = self.search_count([
                ('id', '!=', order.id),
                ('state', '=', 'proforma'),
                ('create_date', '>=', month_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('create_date', '<',  month_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
            ]) + 1
            seq = f"{count:04d}"
            date_str = create_dt.strftime('%Y%m')
            proforma_name = f"PI-{partner_code}-{date_str}-{seq}"
            order.write({
                'name': proforma_name,
                'state': 'proforma',
            })
        return True

    def action_confirm(self):
        # only allow confirm from 'sent' or 'proforma'
        valid = self.filtered(lambda o: o.state in ('sent', 'proforma'))
        invalid = (self - valid)
        if invalid:
            raise UserError("Some orders are not in a state requiring confirmation.")
        # drop proforma → sent so super() will accept
        proformas = valid.filtered(lambda o: o.state == 'proforma')
        if proformas:
            proformas.write({'state': 'sent'})
        # assign custom name per year
        for order in valid:
            ship_code = 'L' if order.shipping_type == 'local' else 'E'
            today = fields.Date.context_today(order)
            yy = today.strftime('%y')
            # year window
            year_start = datetime.strptime(today.strftime('%Y-01-01 00:00:00'),
                                           DEFAULT_SERVER_DATETIME_FORMAT)
            year_end   = year_start + relativedelta(years=1)
            # count prior sales this year
            count = self.search_count([
                ('id', '!=', order.id),
                ('name', 'ilike', f"P{ship_code}{yy}-%"),
                ('create_date', '>=', year_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                ('create_date', '<',  year_end.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
            ]) + 1
            seq = f"{count:04d}"
            sale_name = f"P{ship_code}{yy}-{seq}"
            order.write({'name': sale_name})
        # now run the normal confirmation
        return super(SaleOrder, valid).action_confirm()
