from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64


class PaymentRequest(models.Model):
    _name = 'asc.payment.request'
    _description = 'Payment Requests'

    name = fields.Char(string='Name')
    scheduled_date = fields.Date("Scheduled Date")
    date = fields.Date("Date")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    partner_id = fields.Many2one('res.partner', string="Beneficiary", required=True)
    partner_address = fields.Text(related='partner_id.address_payment_request', string="Beneficiary Address")
    
    bank_account_id = fields.Many2one('res.partner.bank', string="Beneficiary Bank Account")
    bank_id = fields.Many2one('res.bank', related='bank_account_id.bank_id', string="Bank")
    bank_branch = fields.Char(related='bank_account_id.branch')
    bank_address = fields.Text(related='bank_id.address_text')
    bank_swift = fields.Char(related='bank_id.bic')
    bank_ifsc = fields.Char(related='bank_account_id.ifsc')
    correspondent_bank_id = fields.Many2one('res.bank', related='bank_account_id.correspondent_bank_id', string="Correspondence Bank")
    correspondent_bank_acc_num = fields.Char(related='bank_account_id.correspondent_bank_acc_num')
    correspondent_bank_swift = fields.Char(related='correspondent_bank_id.bic')
    correspondent_bank_fedwire = fields.Char(related='correspondent_bank_id.fedwire', string="Fedwire ABA No.")
    correspondent_bank_chips_aba = fields.Char(related='bank_account_id.chips_aba')
    correspondent_bank_chips_uid = fields.Char(related='bank_account_id.chips_uid')
    bank_iban = fields.Char(related='bank_account_id.iban')
    
    lead_id = fields.Many2one('crm.lead')
    purchase_order_id = fields.Many2one('purchase.order')
    sale_order_id = fields.Many2one('sale.order')
    sale_invoice_id = fields.Many2one('account.move', related='lead_id.sale_invoice_id')
    
    supplier_proforma_num = fields.Char(related='purchase_order_id.partner_ref', string="Supplier PFI No.")
    supplier_invoice_ref = fields.Text(related='lead_id.supplier_invoice_list', string="Supplier CI No.")
    payment_term_id = fields.Many2one('account.payment.term', related="purchase_order_id.payment_term_id", string="Payment Terms")
    
    currency_id = fields.Many2one('res.currency', related='purchase_order_id.currency_id')
    amount = fields.Float("Payment Amount Required", required=True)
    amount_words = fields.Char("Amount in Words", compute='_compute_amount_words')
    
    note = fields.Text("Comments")
    instructions = fields.Text("Special Instructions")
    
    type = fields.Selection([('advance', "Advance"),
                              ('final', "Final"),],
                             string="Payment Type")
    
    approval_ids = fields.One2many('asc.approval', 'payment_request_id', string="Approvals")
    
    state = fields.Selection([('draft', "Draft"),
                              ('confirm', "Submitted"),
                              ('approve', "Approved"),
                              ('cancel', "Rejected/Cancelled")],
                             string="Status", default='draft', required=True)
    
    @api.constrains('type', 'purchase_order_id')
    def _check_single_final_payment_per_purchase(self):
        for record in self:
            if record.type == 'final' and record.purchase_order_id:
                # Count other final payments for the same PO (excluding self)
                final_requests = self.search_count([
                    ('id', '!=', record.id),
                    ('purchase_order_id', '=', record.purchase_order_id.id),
                    ('type', '=', 'final')
                ])
                if final_requests:
                    raise ValidationError(
                        "There is already a final payment request for this Purchase Order."
                    )

    @api.depends('amount')
    def _compute_amount_words(self):
        for rec in self:
            rec.amount_words = rec.currency_id.amount_to_text(rec.amount)
            
    @api.depends('approval_ids','approval_ids.approve_date')
    def check_approval(self):
        for rec in self:
            if rec.approval_ids and all(approval.is_approved for approval in rec.approval_ids):
                rec.state = 'approve'
            
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('asc.payment.request.seq')
        vals['name'] = sequence
        payment_request = super(PaymentRequest, self).create(vals)
        return payment_request
    
    def confirm_wizard(self):
        self.ensure_one()
        # if not self.sale_invoice_id:
        #     raise UserError("No Afrex PFI or CI found for this trade.")
        return {
            'res_id': self.id,
            'res_model': 'asc.payment.request',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('afrex_supply_chain.asc_payment_request_submit_form_view').id,
            'context': {},
            'target': 'new'
        }
        
    def action_confirm(self):
        self.ensure_one()
        self.write({'state': "confirm",
                    'date': fields.Datetime.now()})
        approvers = self.env.company.payment_request_approver_ids
        for approver in approvers:
            approval_vals = {
                'user_id': approver.id,
                'payment_request_id': self.id
            }
            approval = self.env['asc.approval'].sudo().create(approval_vals)
        return self.env.ref('afrex_supply_chain.action_report_asc_payment_request').report_action(self)
    
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            
    def action_approve(self):
        for rec in self:
            rec.state = 'approve'
    
    def action_reset(self):
        for rec in self:
            rec.state = 'draft'
            
    def print_payment_request(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_payment_request').report_action(self)
            
                