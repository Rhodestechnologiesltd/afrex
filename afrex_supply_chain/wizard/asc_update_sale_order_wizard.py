from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class UpdateSaleOrderWizard(models.TransientModel):
    _name = 'asc.update.sale.order'
    _description = 'Update Sale Order Wizard'

    purchase_order_id = fields.Many2one('purchase.order')
    sale_order_id = fields.Many2one('sale.order', related='purchase_order_id.sale_order_id', string="Offer/Quote")
    
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id', string="Trade Folder")
    is_internal = fields.Boolean("Trademaw", related='lead_id.is_internal')
    
    qty_total = fields.Float(string="MT Ordered", related='sale_order_id.qty_total')

    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms", related='sale_order_id.incoterm_id')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    currency_id = fields.Many2one('res.currency', related='sale_order_id.currency_id')
    is_currency_zar = fields.Boolean("Currency is ZAR", compute="_compute_is_currency_zar")
    exchange_rate = fields.Float(related="lead_id.indicative_exchange_rate", string="Indicative Rate of Exchange (ROE) USDZAR", digits="Prices per Unit", readonly=False)
    
    initial_fob_amount = fields.Float("FOB", related='sale_order_id.fob_amount')
    initial_freight_amount = fields.Float("Freight", related='sale_order_id.freight_amount')
    initial_cost_amount = fields.Float("Cost", related='sale_order_id.cost_amount')
    initial_insurance_amount = fields.Float("Insurance", related='sale_order_id.insurance_amount')
    initial_interest_amount = fields.Float("Interest", related='sale_order_id.interest_amount')
    initial_procurement_documentation_amount = fields.Float("Procurement & Documentation", related='sale_order_id.procurement_documentation_amount')
    initial_fob_unit = fields.Float("FOB/MT", related='sale_order_id.fob_unit', digits="Prices per Unit")
    initial_freight_unit = fields.Float("Freight/MT", related='sale_order_id.freight_unit', digits="Prices per Unit")
    initial_cost_unit = fields.Float("Cost/MT", related='sale_order_id.cost_unit', digits="Prices per Unit")
    
    fob_amount = fields.Float("FOB", compute="_compute_fob_amount", store=True)
    freight_amount = fields.Float("Freight")
    cost_amount = fields.Float("Cost")
    insurance_amount = fields.Float("Insurance")
    interest_amount = fields.Float("Interest")
    procurement_documentation_amount = fields.Float("Procurement & Documentation")
    
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit")
    
    fob_amount_zar = fields.Float("FOB in ZAR", compute="compute_zar_amount")
    freight_amount_zar = fields.Float("Freight in ZAR", compute="compute_zar_amount")
    cost_amount_zar = fields.Float("Cost in ZAR", compute="compute_zar_amount")
    insurance_amount_zar = fields.Float("Insurance in ZAR", compute="compute_zar_amount")
    interest_amount_zar = fields.Float("Interest in ZAR", compute="compute_zar_amount")
    procurement_documentation_amount_zar = fields.Float("Procurement & Documentation in ZAR", compute="compute_zar_amount")
    
    fob_unit = fields.Float("FOB/MT", compute="_compute_fob_unit", store=True, digits="Prices per Unit")
    freight_unit = fields.Float("Freight/MT", compute="_compute_freight_unit", store=True, digits="Prices per Unit")
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit")
    
    fob_unit_zar = fields.Float("FOB/MT in ZAR", compute="_compute_fob_unit_zar", store=True, digits="Prices per Unit")
    freight_unit_zar = fields.Float("Freight/MT in ZAR", compute="_compute_freight_unit_zar", store=True, digits="Prices per Unit")
    cost_unit_zar = fields.Float("Cost/MT in ZAR", compute="_compute_cost_unit_zar", store=True, digits="Prices per Unit")
    
    
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
                
    @api.depends('currency_id')
    def _compute_is_currency_zar(self):
        for rec in self:
            if rec.currency_id == self.env.ref('base.ZAR'):
                rec.is_currency_zar = True
            else:
                rec.is_currency_zar = False
    
    @api.depends('currency_id','exchange_rate')
    def compute_zar_amount(self):
        for rec in self:
            rec.fob_amount_zar = rec.fob_amount * rec.exchange_rate
            rec.freight_amount_zar = rec.freight_amount * rec.exchange_rate
            rec.cost_amount_zar = rec.cost_amount * rec.exchange_rate
            rec.insurance_amount_zar = rec.insurance_amount * rec.exchange_rate
            rec.interest_amount_zar = rec.interest_amount * rec.exchange_rate
            rec.procurement_documentation_amount_zar = rec.procurement_documentation_amount * rec.exchange_rate
            rec.fob_unit_zar = rec.fob_unit * rec.exchange_rate
            rec.freight_unit_zar = rec.freight_unit * rec.exchange_rate
            rec.cost_unit_zar = rec.cost_unit * rec.exchange_rate
                
    @api.depends('cost_amount','freight_amount','insurance_amount','interest_amount','procurement_documentation_amount')
    def _compute_fob_amount(self):
        for rec in self:
            if rec.is_internal:
                rec.fob_amount = rec.cost_amount - (rec.freight_amount +  rec.insurance_amount + rec.interest_amount + rec.procurement_documentation_amount)
                rec.fob_amount_zar = (rec.cost_amount - (rec.freight_amount +  rec.insurance_amount + rec.interest_amount + rec.procurement_documentation_amount)) * self.exchange_rate
            else:
                rec.fob_amount = rec.cost_amount - (rec.freight_amount +  rec.insurance_amount)
                rec.fob_amount_zar = (rec.cost_amount - (rec.freight_amount +  rec.insurance_amount)) * self.exchange_rate
            
    @api.depends('fob_amount','qty_total')
    def _compute_fob_unit(self):
        for rec in self:
            try:
                rec.fob_unit = rec.fob_amount / rec.qty_total
            except ZeroDivisionError:
                rec.fob_unit = 0
            
    @api.depends('freight_amount','qty_total')
    def _compute_freight_unit(self):
        for rec in self:
            try:
                rec.freight_unit = rec.freight_amount / rec.qty_total
            except ZeroDivisionError:
                rec.freight_unit = 0
    
    @api.depends('cost_amount','qty_total')
    def _compute_cost_unit(self):
        for rec in self:
            try:
                rec.cost_unit = rec.cost_amount / rec.qty_total
            except ZeroDivisionError:
                rec.cost_unit = 0
                
    @api.depends('fob_amount_zar','qty_total')
    def _compute_fob_unit_zar(self):
        for rec in self:
            try:
                rec.fob_unit_zar = rec.fob_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.fob_unit_zar = 0
            
    @api.depends('freight_amount_zar','qty_total')
    def _compute_freight_unit_zar(self):
        for rec in self:
            try:
                rec.freight_unit_zar = rec.freight_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.freight_unit_zar = 0
    
    @api.depends('cost_amount_zar','qty_total')
    def _compute_cost_unit_zar(self):
        for rec in self:
            try:
                rec.cost_unit_zar = rec.cost_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.cost_unit_zar = 0
    
    
    def update_sale_order(self):
        lead = self.lead_id
        purchase_order = self.purchase_order_id
        sale_order = self.sale_order_id
        
        if sale_order.state == 'sale':
            raise UserError("An offer has already been confirmed for this deal.")

        if self.currency_id == self.env.ref('base.ZAR'):
            fob_amount = self.fob_amount_zar
            freight_amount = self.freight_amount_zar
            cost_amount = self.cost_amount_zar
            insurance_amount = self.insurance_amount_zar
            interest_amount = self.interest_amount_zar
            procurement_documentation_amount = self.procurement_documentation_amount_zar
            fob_unit = self.fob_unit_zar
            freight_unit = self.freight_unit_zar
            cost_unit = self.cost_unit_zar
        else:
            fob_amount = self.fob_amount 
            freight_amount = self.freight_amount
            cost_amount = self.cost_amount
            insurance_amount = self.insurance_amount
            interest_amount = self.interest_amount
            procurement_documentation_amount = self.procurement_documentation_amount
            fob_unit = self.fob_unit
            freight_unit = self.freight_unit
            cost_unit = self.cost_unit
        
        order_vals = {
            'fob_amount': fob_amount,
            'freight_amount': freight_amount,
            'cost_amount': cost_amount,
            'insurance_amount': insurance_amount,
            'interest_amount': interest_amount,
            'procurement_documentation_amount': procurement_documentation_amount,
        }
        order = sale_order.sudo().write(order_vals)
        
        return {
            'res_id': sale_order.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }