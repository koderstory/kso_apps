# models/template_ru.py
from odoo import _, models
from odoo.addons.account.models.chart_template import template

class L10nRUChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("ru")
    def _get_ru_template_data(self):
        return {
            "name": _("Russia - Basic"),
            "visible": True,
            "code_digits": "2",
        }

    @template("ru", "res.company")
    def _get_ru_res_company(self):
        return {
            self.env.company.id: {
                "account_fiscal_country_id": "base.ru",
                "currency_id": "base.RUB",                # ← set default currency to Ruble
                "account_sale_tax_id": "ru_vat_20_sale",
                "account_purchase_tax_id": "ru_vat_20_purchase",
            }
        }
