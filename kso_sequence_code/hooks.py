# kso_sequence_code/hooks.py
from odoo import api, SUPERUSER_ID

def post_init_sequences(env):
    pass
    # re-create env as superuser
    sudo_env = api.Environment(env.cr, SUPERUSER_ID, env.context)
    seq = sudo_env['ir.sequence'].search(
        [('name', '=', 'My Company Sequence production')],
        limit=1
    )
    if seq:
        seq.write({
            'prefix': 'WH/MO/%(year)s/%(month)s/',
            'padding': 5,
        })
