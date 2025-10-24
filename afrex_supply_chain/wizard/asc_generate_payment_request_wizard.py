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
    amount = fields.Float("Payment Amount Required")
    amount_words = fields.Char("Amount in Words", compute='_compute_amount_words')
    # note = fields.Text("Comments")
    # instructions = fields.Text("Special Instructions")
    # type = fields.Selection([('advance', "Advance"),
    #                           ('final', "Final"),],
    #                          string="Payment Type")

    payment_category = fields.Selection([
        ('supplier', 'Supplier'),
        ('service', 'Service Provider'),
    ], string="Payment Category", default='supplier', required=True)

    @api.depends('amount')
    def _compute_amount_words(self):
        for rec in self:
            rec.amount_words = rec.currency_id.amount_to_text(rec.amount)
    @api.onchange('payment_category', 'lead_id')
    def _onchange_payment_category(self):
        """Auto-select the partner based on payment category."""
        if self.lead_id:
            if self.payment_category == 'supplier' and self.purchase_order_id:
                self.partner_id = self.purchase_order_id.partner_id
            else:
                self.partner_id = False
    def generate_payment_request(self):
        purchase = self.purchase_order_id
        lead = self.lead_id
        partner = self.partner_id
        # if not invoice:
        #     raise UserError("No Afrex PFI or CI found for this trade.")
        # if not lead.sale_purchase_order_num:
        #     raise UserError("PO from buyer has not been received yet.")

        # if not purchase.payment_term_id:
        #     raise UserError("No payment terms set.")
        # if purchase.state not in ['purchase', 'done']:
        #     raise UserError("PO needs to be confirmed.")
        if not lead:
            raise UserError("No trade folder found.")
        if not partner:
            raise UserError(_("Please select a Beneficiary."))

        total = 0.0
        payment_type = 'advance'

        if self.payment_category == 'supplier':
            if not purchase:
                raise UserError(_("No Purchase Order selected."))
            if purchase.state not in ['purchase', 'done']:
                raise UserError(_("PO must be confirmed before generating a payment request."))
            if not purchase.payment_term_id or not purchase.payment_term_id.breakdown_ids:
                raise UserError(_("No payment breakdown found for this Payment Term."))

            total = purchase.amount_total
            payment_term = purchase.payment_term_id
            breakdown = payment_term.breakdown_ids
            if not breakdown:
                raise UserError("No payment breakdown found for this Payment Term(s).")
            for line in breakdown:
                amount = line.percentage * total
                type = line.payment_type
                payment_vals = {
                    'payment_category': 'supplier',
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

        else:
            vals = {
                'payment_category': self.payment_category,
                'lead_id': lead.id,
                'partner_id': partner.id,
                'bank_account_id': self.bank_account_id.id,
                'currency_id': self.env.company.currency_id.id,
                'amount': self.amount,
                'amount_words': self.amount_words,
                'type': payment_type,
                'state': 'draft',
            }
            self.env['asc.payment.request'].sudo().create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment Requests',
            'view_mode': 'tree,form',
            'res_model': 'asc.payment.request',
            'domain': [('purchase_order_id', '=', purchase.id)],
            'context': "{'create': False}",
            'target': 'current',
        }