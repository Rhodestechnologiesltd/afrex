# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
import math

class Lead(models.Model):
    _inherit = 'crm.lead'
    
    indicative_exchange_rate = fields.Float(string="Indicative Rate of Exchange (ROE) USDZAR", digits="Prices per Unit")
    exchange_rate = fields.Float(string="Booked Rate of Exchange", digits="Prices per Unit")

    banking_fee_ids = fields.One2many('asc.banking.fee', 'lead_id', string="Banking Fees")
    
    afrex_insurance_agent_id = fields.Many2one('res.partner', string="Insurance Agent")

    insurance_premium_amount = fields.Float("Insurance Premium")
    insurance_premium_unit = fields.Float("Insurance Premium per MT", compute="compute_insurance_premium_unit", readonly=False, store=True)

    afrex_freight_amount = fields.Float("Freight borne by Afrex", compute="compute_afrex_freight_amount", store=True)
    afrex_freight_rate = fields.Float("Freight Rate / MT")
    
    procurement_agent_id = fields.Many2one('res.partner', string="Procurement Agent")
    procurement_commission_fob_rate = fields.Float(string="Procurement Commission Rate against FOB")
    procurement_commission_fob_amount = fields.Float(string="Procurement Commission against FOB", compute="compute_procurement_commission_fob_amount", store=True)
    
    procurement_commission_unit = fields.Float(string="Procurement Commission per MT")
    procurement_commission_unit_amount = fields.Float(string="Procurement Commission Total", compute='compute_procurement_commission_unit_amount', store=True)
    
    procurement_fee_rate = fields.Float(string="Procurement Fee Rate against CIF")
    procurement_fee_amount = fields.Float(string="Procurement Fee against CIF Total", compute='compute_procurement_fee_amount', store=True)
    
    sales_agent_id = fields.Many2one('res.partner', string="Sales Agent")
    sales_commission_unit = fields.Float(string="Sales Commission per MT")
    sales_commission_amount = fields.Float(string="Sales Commission Total", compute='compute_sales_commission_amount', store=True)
    
    switch_bl_provision_amount = fields.Float(string="switch_bl_provision_amount")
    
    bank_fee_total  = fields.Float(string="bank_fee_total", compute='compute_bank_fee_total', store=True)
    
    credit_cost_rate = fields.Float(string="credit_cost_rate", default=0.0425)
    credit_cost_month = fields.Integer(string="No of Months for Credit Cost", default=4)
    credit_cost_amount = fields.Float(string="credit_cost_amount", compute='compute_credit_cost_amount', store=True)
    
    credit_insurance_rate = fields.Float(string="credit_insurance_rate", default=0.006)
    credit_insurance_amount = fields.Float(string="credit_insurance_amount", compute='compute_credit_insurance_amount', store=True)
    
    sales_cost = fields.Float(string="sales_cost", compute='compute_sales_cost', store=True)
    other_cost = fields.Float(string="other_cost", compute='compute_other_cost', store=True)
    total_cost = fields.Float(string="total_cost", compute='compute_total_cost', store=True)
    total_cost_unit = fields.Float(string="total_cost_unit", compute='compute_total_cost_unit', store=True)
    
    initial_sales_price_unit = fields.Float(string="initial_sales_price_unit", compute='compute_initial_sales_price_unit', store=True)
    initial_sales_price_unit_unrounded = fields.Float(string="Unrounded Initial Sales Price per MT")
    sales_price_unit = fields.Float(string="Final calculated Sales Price", compute='compute_sales_price_unit', store=True)
    sales_price_unit_unrounded = fields.Float(string="Unrounded Final Sales Price per MT")
    
    initial_sales_price = fields.Float(string="initial_sales_price", compute='compute_initial_sales_price', store=True)
    sales_price = fields.Float(string="sales_price", compute='compute_sales_price', store=True)
    sales_price_unrounded = fields.Float(string="Unrounded Final sales_price")
    
    is_sales_price_override = fields.Boolean(string="Override Sales Price", help="Check this box if you want to override the calculated sales price")
    agreed_sales_price_unit = fields.Float(string="Agreed Sales Price per MT")
    agreed_sales_price = fields.Float(string="Agreed Sales Price", compute='compute_agreed_sales_price', store=True)
    
    gross_profit_amount = fields.Float(string="gross_profit_amount", compute='compute_gross_profit_amount', store=True)
    gross_profit_percentage = fields.Float(string="gross_profit_percentage", compute='compute_gross_profit_percentage', store=True)
    
    markup_amount = fields.Float(string="markup_amount", compute='compute_markup_amount', store=True)
    markup_percentage = fields.Float(string="markup_percentage", compute='compute_markup_percentage', store=True)
    
    markup = fields.Float(string="Markup", help="Theoretical markup for Profit Estimate", default=0.06)
        
    minimum_gross_profit = fields.Float(string="Minimum Gross Profit", related='company_id.minimum_gross_profit')
    minimum_markup = fields.Float(string="Minimum Markup", related='company_id.minimum_markup')
    
    cover_report_amount = fields.Float(string="Cover Report Amount")
    
    purchase_order_freight_amount_zar = fields.Float(compute='compute_purchase_order_freight_amount_zar', store=True, digits="Prices per Unit")
    purchase_order_fob_amount_zar = fields.Float(compute='compute_purchase_order_fob_amount_zar', store=True, digits="Prices per Unit")
    purchase_order_fca_amount_zar = fields.Float(compute='compute_purchase_order_fca_amount_zar', store=True, digits="Prices per Unit")
    purchase_order_insurance_amount_zar = fields.Float(compute='compute_purchase_order_insurance_amount_zar', store=True, digits="Prices per Unit")
    afrex_freight_amount_zar = fields.Float(compute='compute_afrex_freight_amount_zar', store=True, digits="Prices per Unit")
    procurement_fee_amount_zar = fields.Float(compute='compute_procurement_fee_amount_zar', store=True, digits="Prices per Unit")
    credit_cost_amount_zar = fields.Float(compute='compute_credit_cost_amount_zar', store=True, digits="Prices per Unit")
    credit_insurance_amount_zar = fields.Float(compute='compute_credit_insurance_amount_zar', store=True, digits="Prices per Unit")
    sales_price_zar = fields.Float(compute='compute_sales_price_zar', store=True, digits="Prices per Unit")
    agreed_sales_price_zar = fields.Float(compute='compute_agreed_sales_price_zar', store=True, digits="Prices per Unit")
    insurance_premium_unit_zar = fields.Float(compute='compute_insurance_premium_unit_zar', store=True, digits="Prices per Unit")
    
    dap_amount = fields.Float(string="DAP Amount", compute="_compute_dap_amount", store=True, digits="Prices per Unit", help="The DAP amount is the total cost of the product including all costs up to delivery at the customer's premises.")
    cif_amount = fields.Float(string="CIF Amount", compute="_compute_cif_amount", store=True, digits="Prices per Unit", help="The CIF amount is the total cost of the product including all costs up to the port of discharge.")
                              
    @api.depends('purchase_order_freight_amount','indicative_exchange_rate','exchange_rate')
    def compute_purchase_order_freight_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_freight_amount_zar = rec.purchase_order_freight_amount * roe

    @api.depends('purchase_order_fob_amount','indicative_exchange_rate','exchange_rate')
    def compute_purchase_order_fob_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_fob_amount_zar = rec.purchase_order_fob_amount * roe

    @api.depends('purchase_order_fca_amount','indicative_exchange_rate','exchange_rate')
    def compute_purchase_order_fca_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_fca_amount_zar = rec.purchase_order_fca_amount * roe
            
    @api.depends('purchase_order_insurance_amount','indicative_exchange_rate','exchange_rate')
    def compute_purchase_order_insurance_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_insurance_amount_zar = rec.purchase_order_insurance_amount * roe

    @api.depends('afrex_freight_amount','indicative_exchange_rate','exchange_rate')
    def compute_afrex_freight_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.afrex_freight_amount_zar = rec.afrex_freight_amount * roe

    @api.depends('procurement_fee_amount','indicative_exchange_rate','exchange_rate')
    def compute_procurement_fee_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.procurement_fee_amount_zar = rec.procurement_fee_amount * roe

    @api.depends('credit_cost_amount','indicative_exchange_rate','exchange_rate')
    def compute_credit_cost_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.credit_cost_amount_zar = rec.credit_cost_amount * roe

    @api.depends('credit_insurance_amount','indicative_exchange_rate','exchange_rate')
    def compute_credit_insurance_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.credit_insurance_amount_zar = rec.credit_insurance_amount * roe
            
    @api.depends('sales_price','indicative_exchange_rate','exchange_rate')
    def compute_sales_price_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.sales_price_zar = rec.sales_price * roe
            
    @api.depends('agreed_sales_price','indicative_exchange_rate','exchange_rate')
    def compute_agreed_sales_price_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.agreed_sales_price_zar = rec.agreed_sales_price_zar * roe
    
    @api.depends('insurance_premium_unit','indicative_exchange_rate','exchange_rate')
    def compute_insurance_premium_unit_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.insurance_premium_unit_zar = rec.insurance_premium_unit * roe
    
    @api.depends('insurance_premium_amount', 'product_qty')
    def compute_insurance_premium_unit(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.insurance_premium_unit = rec.insurance_premium_amount / rec.product_qty
                except ZeroDivisionError:
                    rec.insurance_premium_unit = 0
    
    @api.depends('afrex_freight_rate', 'product_qty', 'packaging_weight')
    def compute_afrex_freight_amount(self):
        for rec in self:
            rec.afrex_freight_amount = rec.product_qty * (1 + (rec.packaging_weight / 1000)) * rec.afrex_freight_rate
    
    @api.depends('purchase_order_fca_amount', 'road_transportation_amount', 'logistics_service_amount')
    def _compute_dap_amount(self):
            for rec in self:
                rec.dap_amount = rec.purchase_order_fca_amount + rec.road_transportation_amount + rec.logistics_service_amount
    
    @api.depends('purchase_order_fob_amount', 'purchase_order_freight_amount', 'purchase_order_insurance_amount')                
    def _compute_cif_amount(self):
        for rec in self:
            rec.cif_amount = rec.purchase_order_fob_amount + rec.purchase_order_freight_amount + rec.purchase_order_insurance_amount
    
    @api.depends('procurement_commission_fob_rate', 'purchase_order_fob_amount')
    def compute_procurement_commission_fob_amount(self):
        for rec in self:
            rec.procurement_commission_fob_amount = rec.procurement_commission_fob_rate * rec.purchase_order_fob_amount
            
    @api.depends('procurement_commission_unit', 'product_qty')
    def compute_procurement_commission_unit_amount(self):
        for rec in self:
            rec.procurement_commission_unit_amount = rec.procurement_commission_unit * rec.product_qty
    
    @api.depends('procurement_fee_rate', 'purchase_order_cost_amount')
    def compute_procurement_fee_amount(self):
        for rec in self:
            rec.procurement_fee_amount = rec.procurement_fee_rate * rec.purchase_order_cost_amount

    @api.depends('sales_commission_unit', 'product_qty')
    def compute_sales_commission_amount(self):
        for rec in self:
            rec.sales_commission_amount = rec.sales_commission_unit * rec.product_qty
                        
    # @api.depends('road_transportation_unit', 'product_qty')
    # def compute_road_transportation_amount(self):
    #     for rec in self:
    #         rec.road_transportation_amount = rec.road_transportation_unit * rec.product_qty
                        
    # @api.depends('logistics_service_unit', 'product_qty')
    # def compute_logistics_service_amount(self):
    #     for rec in self:
    #         rec.logistics_service_amount = rec.logistics_service_unit * rec.product_qty

    @api.depends('banking_fee_ids', 'banking_fee_ids.amount')
    def compute_bank_fee_total(self):
        for rec in self:
            total = 0
            for fee in rec.banking_fee_ids:
                total += fee.amount
            rec.bank_fee_total = total

    @api.depends('purchase_order_cost_amount', 'credit_cost_rate', 'credit_cost_month')
    def compute_credit_cost_amount(self):
        # =(CIF PURCHASE PRICE *(4.25%/12))*4
        for rec in self:
            if rec.credit_cost_rate > 0:
                rec.credit_cost_amount = (rec.purchase_order_cost_amount * (rec.credit_cost_rate/12) * rec.credit_cost_month)
            else:
                rec.credit_cost_amount = 0
    
    @api.depends('supplier_delivery_method', 'purchase_order_cost_amount', 'procurement_commission_fob_amount', 'procurement_commission_unit_amount', 'sales_commission_amount', 'switch_bl_provision_amount', 'road_transportation_amount', 'logistics_service_amount')
    def compute_sales_cost(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                rec.sales_cost = rec.purchase_order_cost_amount + rec.procurement_commission_fob_amount + rec.procurement_commission_unit_amount + rec.sales_commission_amount + rec.switch_bl_provision_amount
            if rec.supplier_delivery_method == 'road':
                rec.sales_cost = rec.purchase_order_cost_amount + rec.procurement_commission_unit_amount + rec.sales_commission_amount + rec.road_transportation_amount + rec.logistics_service_amount

    @api.depends('bank_fee_total', 'credit_cost_amount', 'credit_insurance_amount')
    def compute_other_cost(self):
        for rec in self:
            if rec.is_internal:
                rec.other_cost = rec.bank_fee_total
            else:
                rec.other_cost = rec.bank_fee_total + rec.credit_cost_amount

    @api.depends('sales_cost', 'other_cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.sales_cost + rec.other_cost

    @api.depends('total_cost', 'product_qty')
    def compute_total_cost_unit(self):
        for rec in self:
            if rec.product_qty > 0:
                rec.total_cost_unit = rec.total_cost / rec.product_qty
            else:
                rec.total_cost_unit = 0

    @api.depends('sales_price', 'product_qty', 'total_cost_unit', 'markup')
    def compute_initial_sales_price_unit(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.initial_sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.initial_sales_price_unit = 0
            else:
                temp = rec.total_cost_unit * (1 + rec.markup)
                rec.initial_sales_price_unit_unrounded = temp
                rec.initial_sales_price_unit = math.ceil(temp)

    @api.depends('sales_cost', 'procurement_fee_amount', 'credit_cost_amount', 'initial_sales_price_unit', 'product_qty')
    def compute_initial_sales_price(self):
        for rec in self:
            if rec.is_internal:
                rec.initial_sales_price = rec.sales_cost + rec.procurement_fee_amount + rec.credit_cost_amount
            else:
                rec.initial_sales_price = rec.initial_sales_price_unit * rec.product_qty
    
    @api.depends('credit_insurance_rate', 'initial_sales_price')
    def compute_credit_insurance_amount(self):
        for rec in self:
            rec.credit_insurance_amount = rec.credit_insurance_rate * rec.initial_sales_price

    # @api.depends('credit_insurance_rate', 'initial_sales_price')
    # def compute_credit_insurance_amount(self):
    #     for rec in self:
    #         if rec.is_sales_price_override == 'False':
    #             rec.credit_insurance_amount = rec.credit_insurance_rate * rec.initial_sales_price
    #         else:
    #             rec.credit_insurance_amount = rec.credit_insurance_rate * rec.agreed_sales_price

    @api.depends('sales_cost', 'procurement_fee_amount', 'credit_cost_amount', 'initial_sales_price', 'credit_insurance_amount')
    def compute_sales_price(self):
        for rec in self:
            if rec.is_internal:
                rec.sales_price = rec.sales_cost + rec.procurement_fee_amount + rec.credit_cost_amount
            else:
                temp = rec.initial_sales_price + rec.credit_insurance_amount
                rec.sales_price_unrounded = temp
                rec.sales_price = math.ceil(temp)
    
    @api.depends('sales_price', 'product_qty', 'sales_price_unrounded')
    def compute_sales_price_unit(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.sales_price_unit = 0
            else:
                try:
                    rec.sales_price_unit_unrounded = rec.sales_price_unrounded / rec.product_qty
                    rec.sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.sales_price_unit_unrounded = 0
                    rec.sales_price_unit = 0
    
    @api.depends('is_sales_price_override', 'agreed_sales_price_unit', 'product_qty')
    def compute_agreed_sales_price(self):
        for rec in self:
            rec.agreed_sales_price = rec.agreed_sales_price_unit * rec.product_qty

    @api.depends('sales_price', 'sales_cost', 'is_sales_price_override', 'agreed_sales_price')
    def compute_gross_profit_amount(self):
        for rec in self:
            if rec.is_sales_price_override:
                rec.gross_profit_amount = abs(rec.agreed_sales_price - rec.sales_cost)
            else:
                rec.gross_profit_amount = abs(rec.sales_price - rec.sales_cost)

    @api.depends('gross_profit_amount', 'sales_price', 'is_sales_price_override', 'agreed_sales_price')
    def compute_gross_profit_percentage(self):
        for rec in self:
            try:
                if rec.is_sales_price_override:
                    rec.gross_profit_percentage = rec.gross_profit_amount / rec.agreed_sales_price
                else:
                    rec.gross_profit_percentage = rec.gross_profit_amount / rec.sales_price
            except ZeroDivisionError:
                rec.gross_profit_percentage = 0

    @api.depends('sales_price', 'total_cost', 'credit_cost_amount', 'is_sales_price_override', 'agreed_sales_price')
    def compute_markup_amount(self):
        for rec in self:
            if rec.is_internal:
                if rec.is_sales_price_override:
                    rec.markup_amount = rec.agreed_sales_price - (rec.total_cost + rec.credit_cost_amount)
                else:
                    rec.markup_amount = rec.sales_price - (rec.total_cost + rec.credit_cost_amount)
            else:
                if rec.is_sales_price_override:
                    rec.markup_amount = rec.agreed_sales_price - (rec.total_cost + rec.credit_insurance_amount)
                else:
                    rec.markup_amount = rec.sales_price - (rec.total_cost + rec.credit_insurance_amount)

    @api.depends('markup_amount', 'total_cost', 'credit_insurance_amount')
    def compute_markup_percentage(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.markup_percentage = rec.markup_amount / rec.total_cost
                except ZeroDivisionError:
                    rec.markup_percentage = 0
            else:
                try:
                    rec.markup_percentage = (rec.markup_amount + rec.credit_insurance_amount) / rec.total_cost
                except ZeroDivisionError:
                    rec.markup_percentage = 0
                
    def print_profit_estimate(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_profit_estimate_new').report_action(self)
