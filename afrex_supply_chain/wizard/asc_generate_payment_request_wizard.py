from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class GeneratePaymentRequestWizard(models.TransientModel):
    _name = 'asc.generate.payment.request'
    _description = 'Generate Payment Request Wizard'
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    purchase_order_id = fields.Many2one('purchase.order')
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id')
    sale_invoice_id = fields.Many2one('account.move', related='lead_id.sale_invoice_id')
    
    partner_id = fields.Many2one('res.partner', string="Beneficiary", related='purchase_order_id.partner_id')
    bank_account_id = fields.Many2one('res.partner.bank', string="Beneficiary Bank Account", required=True)
    
    # date = fields.Date("Date", default=fields.Datetime.now(), required=True)
    # amount = fields.Float("Payment Amount Required", required=True)
    # note = fields.Text("Comments")
    # instructions = fields.Text("Special Instructions")
    # type = fields.Selection([('advance', "Advance"),
    #                           ('final', "Final"),],
    #                          string="Payment Type")
    
    def generate_payment_request(self):
        purchase = self.purchase_order_id
        lead = self.lead_id
        
        # if not invoice:
        #     raise UserError("No Afrex PFI or CI found for this trade.")
        # if not lead.sale_purchase_order_num:
        #     raise UserError("PO from buyer has not been received yet.")
            
        if not purchase.payment_term_id:
            raise UserError("No payment terms set.")
        if purchase.state not in ['purchase', 'done']:
            raise UserError("PO needs to be confirmed.")
        if not lead:
            raise UserError("No trade folder found.")
        total = purchase.amount_total
        payment_term = purchase.payment_term_id
        breakdown = payment_term.breakdown_ids
        if not breakdown:
            raise UserError("No payment breakdown found for this Payment Term(s).")
        for line in breakdown:
            amount = line.percentage * total
            type = line.payment_type
            payment_vals = {
                'purchase_order_id': purchase.id,
                'lead_id': purchase.lead_id.id,
                'partner_id': purchase.partner_id.id,
                'bank_account_id': self.bank_account_id.id,
                'currency_id': purchase.currency_id.id,
                'amount': amount,
                'type': type,
                'state': 'draft'
            }
            payment = lead.env['asc.payment.request'].sudo().create(payment_vals)
        if payment:
            purchase.is_payment_request_generated = True
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Requests',
            'view_mode': 'tree,form',
            'res_model': 'asc.payment.request',
            'domain': [('purchase_order_id', '=', purchase.id)],
            'context': "{'create': False}",
            'target': 'current',
        }