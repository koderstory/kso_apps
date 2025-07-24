from odoo import api, SUPERUSER_ID

def post_init_sequences(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    seq = env['ir.sequence'].search(
        [('name', '=', 'My Company Sequence production')], limit=1
    )
    if seq:
        seq.write({
            'prefix': 'WH/MO/%(year)s/%(month)s/',
            'padding': 5,
        })
