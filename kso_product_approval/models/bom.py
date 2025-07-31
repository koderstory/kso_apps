from odoo import models, fields, api, _
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
        for bom in self:
            # 1) gather any BoM lines whose product is not in Approved state
            bad_lines = bom.bom_line_ids.filtered(
                lambda line: line.product_id.state != 'approved'
            )
            if bad_lines:
                names = bad_lines.mapped('product_id.display_name')
                raise UserError(_(
                    "Cannot approve BoM '%s': the following components are not approved:\n• %s"
                ) % (bom.display_name, "\n• ".join(names)))

        # 2) if we reach here, all components are OK—proceed to set state
        return super().write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def write(self, vals):
        # Prevent any edits on approved BOMs
        if 'state' not in vals:
            approved = self.filtered(lambda b: b.state == 'approved')
            if approved:
                raise UserError("You cannot modify a BOM once it is Approved.")
        return super().write(vals)
