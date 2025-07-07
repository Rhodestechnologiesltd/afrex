from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GeneratePaymentWizard(models.TransientModel):
    _name = 'asc.generate.payment'
    _description = 'Generate Payment Wizard'
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    sale_invoice_id = fields.Many2one('account.move', related='lead_id.sale_invoice_id')
    purchase_order_id = fields.Many2one('purchase.order')
    supplier_id = fields.Many2one('res.partner')
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id')
    supplier_invoice_ref = fields.Char(related='lead_id.supplier_invoice_ref', string="Supplier Commercial Invoice No.")
    