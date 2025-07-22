from odoo import models, fields, api
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    state = fields.Selection([
        ('cancelled', 'Cancelled'),
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        
    ], string="Approval State", readonly=True, copy=False, default='draft', tracking=True)

    def action_submit(self):
        self.write({'state': 'to_approve'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def write(self, vals):
        # Prevent any edits on approved BOMs
        if 'state' not in vals:
            approved = self.filtered(lambda b: b.state == 'approved')
            if approved:
                raise UserError("You cannot modify a BOM once it is Approved.")
        return super().write(vals)
