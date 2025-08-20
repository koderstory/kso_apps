from odoo import api, fields, models, _

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _sum_done_qty(self, moves):
        """Look at all move_line_ids on these moves and sum whichever 'done' field exists."""
        lines = moves.mapped('move_line_ids')
        # try the two usual suspects:
        for fld in ('quantity_done', 'qty_done'):
            if fld in lines._fields:
                return sum(lines.mapped(fld))
        # fallback if neither field is present:
        return 0.0

    def button_mark_done(self):
        self.ensure_one()
        # if we've already confirmed via the wizard, skip the check
        if self.env.context.get('skip_consume_check'):
            return super().button_mark_done()

        consumed_qty = self._sum_done_qty(self.move_raw_ids)
        produced_qty = self._sum_done_qty(self.move_finished_ids)

        if consumed_qty != produced_qty:
            return {
                'name': _('Confirm Production'),
                'type': 'ir.actions.act_window',
                'res_model': 'mrp.produce.check.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_production_id': self.id,
                    'default_consumed_qty': consumed_qty,
                    'default_produced_qty': produced_qty,
                },
            }
        return super().button_mark_done()

class MrpProduceCheckWizard(models.TransientModel):
    _name = 'mrp.produce.check.wizard'
    _description = 'Check production vs consumption'

    production_id = fields.Many2one('mrp.production', readonly=True)
    consumed_qty   = fields.Float(string="Consumed Quantity", readonly=True)
    produced_qty   = fields.Float(string="Produced Quantity", readonly=True)
    difference     = fields.Float(string="Difference", compute='_compute_diff')

    @api.depends('consumed_qty', 'produced_qty')
    def _compute_diff(self):
        for rec in self:
            rec.difference = rec.produced_qty - rec.consumed_qty

    def action_confirm(self):
        # re-call button_mark_done, but now skip the check
        return self.production_id.with_context(skip_consume_check=True).button_mark_done()

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
