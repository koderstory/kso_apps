from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_code = fields.Char(
        string="Partner Code",
        copy=False,
        readonly=True,
        index=True,
    )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        # allow searching by code or by name
        if name:
            args = ['|',
                ('partner_code', operator, name),
                ('name', operator, name),
            ] + args
        partners = self.search(args, limit=limit)
        return [
            (
                p.id,
                f"[{p.partner_code or '—'}] {p.name or ''}"
            )
            for p in partners
        ]


    @api.model
    def create(self, vals):
        
        partner = super().create(vals)
        if not partner.partner_code:
            partner.partner_code = (self.env['ir.sequence'].next_by_code('res.partner.partner.code') or '/')
        return partner
