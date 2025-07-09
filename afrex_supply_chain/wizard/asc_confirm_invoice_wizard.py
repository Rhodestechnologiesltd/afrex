from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import base64

_logger = logging.getLogger(__name__)

class ConfirmInvoiceWizard(models.TransientModel):
    _name = 'asc.confirm.invoice'
    _description = 'Confirm Invoice Wizard'

    sale_invoice_id = fields.Many2one('account.move', string='Invoice', required=True)
    lead_id = fields.Many2one('crm.lead', related='sale_invoice_id.lead_id', string='Trade Folder')
    purchase_order_id = fields.Many2one('purchase.order', related='lead_id.purchase_order_id', string='Purchase Order')
    is_internal = fields.Boolean("Internal deal", related='lead_id.is_internal')
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm', related="sale_invoice_id.invoice_incoterm_id")
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    date = fields.Date(string='Invoice Date', required=True)
    quantity = fields.Float(string='Quantity', related='sale_invoice_id.qty_delivered', digits="Product Unit of Measure")
    
    invoice_ref = fields.Char(string='PO Reference', related='sale_invoice_id.ref', readonly=False, required=True)
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', related='sale_invoice_id.invoice_payment_term_id', readonly=False, required=True)
    payment_due_date = fields.Date(string='Payment Due Date', related='sale_invoice_id.payment_due_date', readonly=False)
    
    vessel = fields.Char("Vessel Name", related='sale_invoice_id.vessel', readonly=False, required=True)
    voyage = fields.Char("Voyage", related='sale_invoice_id.voyage', readonly=False, required=True)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related='sale_invoice_id.expected_arrival_date', readonly=False, required=True)
    sob_date = fields.Date("Shipped on Board Date", related='sale_invoice_id.sob_date', readonly=False, required=True)

    currency_id = fields.Many2one('res.currency', related='sale_invoice_id.currency_id')
    is_currency_zar = fields.Boolean("Currency is ZAR", compute='_compute_is_currency_zar')
    exchange_rate = fields.Float(string="Rate of Exchange (ROE) USDZAR", related='lead_id.exchange_rate', digits="Prices per Unit", readonly=False)
    
    tariff_code = fields.Char(string="Tariff Code", related='sale_invoice_id.tariff_code', readonly=False)
    
    insurance_amount = fields.Float("Insurance", readonly=False)
    freight_amount = fields.Float("Freight", readonly=False)
    interest_amount = fields.Float("Interest", readonly=False)
    procurement_documentation_amount = fields.Float("Procurement and Documentation", readonly=False)
    cost_amount = fields.Float("Sales Price", readonly=False)
    fob_amount = fields.Float("FOB", compute='compute_fob_amount')
    
    fob_amount_zar = fields.Float("FOB")
    freight_amount_zar = fields.Float("Freight")
    cost_amount_zar = fields.Float("Cost")
    insurance_amount_zar = fields.Float("Insurance")
    interest_amount_zar = fields.Float("Interest")
    procurement_documentation_amount_zar = fields.Float("Procurement & Documentation")
    
    fob_unit = fields.Float("FOB/MT", compute="_compute_fob_unit", store=True, digits="Prices per Unit")
    freight_unit = fields.Float("Freight/MT", compute="_compute_freight_unit", store=True, digits="Prices per Unit")
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit")
    
    fob_unit_zar = fields.Float("FOB/MT in ZAR", compute="_compute_fob_unit_zar", store=True, digits="Prices per Unit")
    freight_unit_zar = fields.Float("Freight/MT in ZAR", compute="_compute_freight_unit_zar", store=True, digits="Prices per Unit")
    cost_unit_zar = fields.Float("Cost/MT in ZAR", compute="_compute_cost_unit_zar", store=True, digits="Prices per Unit")
    
    can_confirm = fields.Boolean(compute='_compute_can_confirm')
    
    @api.onchange('sale_invoice_id')
    def _onchange_sale_invoice_id(self):
        for rec in self:
            if rec.sale_invoice_id:
                lead = rec.sale_invoice_id.lead_id
                if lead:
                    rec.interest_amount = lead.credit_cost_amount
                    rec.procurement_documentation_amount = lead.procurement_fee_amount
                    rec.cost_amount = lead.sales_price
                    if lead.purchase_order_id:
                        if rec.incoterm_selection == 'cfr':
                            rec.insurance_amount = 0.0
                            rec.freight_amount = rec.purchase_order_id.freight_amount
                        elif rec.incoterm_selection == 'cif':
                            rec.insurance_amount = rec.purchase_order_id.insurance_amount
                            rec.freight_amount = rec.purchase_order_id.freight_amount
                        elif rec.incoterm_selection == 'fob':
                            rec.insurance_amount = 0.0
                            rec.freight_amount = 0.0
    
    @api.depends('incoterm_id')
    def _compute_incoterm_selection(self):
        for rec in self:
            incoterm = rec.incoterm_id
            if incoterm:
                if incoterm == self.env.ref('account.incoterm_CFR'):
                    rec.incoterm_selection = 'cfr'
                    rec.insurance_amount = 0.0
                    rec.insurance_amount_zar = 0.0
                    rec.freight_amount = rec.purchase_order_id.freight_amount
                    rec.freight_amount_zar = rec.purchase_order_id.freight_amount * rec.exchange_rate
                elif incoterm == self.env.ref('account.incoterm_CIF'):
                    rec.incoterm_selection = 'cif'
                    rec.insurance_amount = rec.purchase_order_id.insurance_amount
                    rec.insurance_amount_zar = rec.purchase_order_id.insurance_amount * rec.exchange_rate
                    rec.freight_amount = rec.purchase_order_id.freight_amount
                    rec.freight_amount_zar = rec.purchase_order_id.freight_amount * rec.exchange_rate
                elif incoterm == self.env.ref('account.incoterm_FOB'):
                    rec.incoterm_selection = 'fob'
                    rec.insurance_amount = 0.0
                    rec.insurance_amount_zar = 0.0
                    rec.freight_amount = 0.0
                    rec.freight_amount_zar = 0.0
                elif incoterm == self.env.ref('account.incoterm_DAP'):
                    rec.incoterm_selection = 'dap'
                    rec.fob_amount = 0.0
                    rec.fob_amount_zar = 0.0
                    rec.insurance_amount = 0.0
                    rec.insurance_amount_zar = 0.0
                    rec.freight_amount = 0.0
                    rec.freight_amount_zar = 0.0
                elif incoterm == self.env.ref('account.incoterm_FCA'):
                    rec.incoterm_selection = 'fca'
                    rec.fob_amount = 0.0
                    rec.fob_amount_zar = 0.0
                    rec.insurance_amount = 0.0
                    rec.insurance_amount_zar = 0.0
                    rec.freight_amount = 0.0
                    rec.freight_amount_zar = 0.0
                else:
                    raise UserError("This incoterm is not allowed for a deal yet.")
            else:
                rec.incoterm_selection = False

    @api.depends('currency_id', 'quantity', 'date', 'vessel', 'voyage', 'expected_arrival_date', 'sob_date','invoice_ref','invoice_payment_term_id','payment_due_date')
    def _compute_can_confirm(self):
        for rec in self:
            rec.can_confirm = all([
                rec.currency_id,
                rec.quantity,
                rec.date,
                rec.vessel,
                rec.voyage,
                rec.expected_arrival_date,
                rec.sob_date,
                rec.invoice_ref,
                rec.invoice_payment_term_id,
                rec.payment_due_date,
            ])
    
    @api.onchange('exchange_rate','insurance_amount','freight_amount','interest_amount','procurement_documentation_amount','cost_amount')
    def compute_zar_amount(self):
        for rec in self:
            rec.freight_amount_zar = rec.freight_amount * rec.exchange_rate
            rec.cost_amount_zar = rec.cost_amount * rec.exchange_rate
            rec.insurance_amount_zar = rec.insurance_amount * rec.exchange_rate
            rec.interest_amount_zar = rec.interest_amount * rec.exchange_rate
            rec.procurement_documentation_amount_zar = rec.procurement_documentation_amount * rec.exchange_rate
            rec.fob_unit_zar = rec.fob_unit * rec.exchange_rate
            rec.freight_unit_zar = rec.freight_unit * rec.exchange_rate
            rec.cost_unit_zar = rec.cost_unit * rec.exchange_rate
    
    @api.depends('currency_id')
    def _compute_is_currency_zar(self):
        for rec in self:
            if rec.currency_id == self.env.ref('base.ZAR'):
                rec.is_currency_zar = True
            else:
                rec.is_currency_zar = False
                
    @api.depends('cost_amount', 'insurance_amount', 'freight_amount', 'interest_amount', 'procurement_documentation_amount','exchange_rate')
    def compute_fob_amount(self):
        lead = self.lead_id
        if not lead.is_internal:
            self.fob_amount = self.cost_amount - (self.insurance_amount + self.freight_amount)
            self.fob_amount_zar = (self.cost_amount - (self.insurance_amount + self.freight_amount)) * self.exchange_rate
        else:
            self.fob_amount = self.cost_amount - (self.insurance_amount + self.freight_amount + self.interest_amount + self.procurement_documentation_amount)
            self.fob_amount_zar = (self.cost_amount - (self.insurance_amount + self.freight_amount + self.interest_amount + self.procurement_documentation_amount)) * self.exchange_rate
    
    @api.depends('fob_amount','quantity')
    def _compute_fob_unit(self):
        for rec in self:
            try:
                rec.fob_unit = rec.fob_amount / rec.quantity
            except ZeroDivisionError:
                rec.fob_unit = 0
            
    @api.depends('freight_amount','quantity')
    def _compute_freight_unit(self):
        for rec in self:
            try:
                rec.freight_unit = rec.freight_amount / rec.quantity
            except ZeroDivisionError:
                rec.freight_unit = 0
    
    @api.depends('cost_amount','quantity')
    def _compute_cost_unit(self):
        for rec in self:
            try:
                rec.cost_unit = rec.cost_amount / rec.quantity
            except ZeroDivisionError:
                rec.cost_unit = 0
                
    @api.depends('fob_amount_zar','quantity')
    def _compute_fob_unit_zar(self):
        for rec in self:
            try:
                rec.fob_unit_zar = rec.fob_amount_zar / rec.quantity
            except ZeroDivisionError:
                rec.fob_unit_zar = 0
            
    @api.depends('freight_amount_zar','quantity')
    def _compute_freight_unit_zar(self):
        for rec in self:
            try:
                rec.freight_unit_zar = rec.freight_amount_zar / rec.quantity
            except ZeroDivisionError:
                rec.freight_unit_zar = 0
    
    @api.depends('cost_amount_zar','quantity')
    def _compute_cost_unit_zar(self):
        for rec in self:
            try:
                rec.cost_unit_zar = rec.cost_amount_zar / rec.quantity
            except ZeroDivisionError:
                rec.cost_unit_zar = 0

    def action_confirm(self):
        invoice = self.sale_invoice_id
        lead = self.lead_id
        quantity = invoice.qty_delivered
        if not invoice:
            raise UserError(_('No invoice found.'))
        invoice.invoice_date = self.date
        invoice.action_post()
        invoice.invoice_date = self.date
        invoice.invoice_date_due = invoice.payment_due_date
        lead.is_afrex_commercial_raised = True
        
        if self.currency_id == self.env.ref('base.ZAR'):
            invoice.fob_amount = self.fob_amount_zar
            invoice.freight_amount = self.freight_amount_zar
            invoice.cost_amount = self.cost_amount_zar
            invoice.insurance_amount = self.insurance_amount_zar
            invoice.interest_amount = self.interest_amount_zar
            invoice.procurement_documentation_amount = self.procurement_documentation_amount_zar
            invoice.fob_unit = self.fob_unit_zar
            invoice.freight_unit = self.freight_unit_zar
            invoice.cost_unit = self.cost_unit_zar
        else:
            invoice.fob_amount = self.fob_amount
            invoice.freight_amount = self.freight_amount
            invoice.cost_amount = self.cost_amount
            invoice.insurance_amount = self.insurance_amount
            invoice.interest_amount = self.interest_amount
            invoice.procurement_documentation_amount = self.procurement_documentation_amount
            invoice.fob_unit = self.fob_unit
            invoice.freight_unit = self.freight_unit
            invoice.cost_unit = self.cost_unit
        
        if not invoice.is_internal:
            invoice.interest_amount = 0.0
            invoice.procurement_documentation_amount = 0.0
        
        for line in invoice.invoice_line_ids:
            line.quantity = quantity
            line.price_unit = invoice.cost_unit
                
        _logger.info(f"Invoice {invoice.name} has been confirmed through wizard.")