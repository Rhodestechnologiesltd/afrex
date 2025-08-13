# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    state = fields.Selection(selection_add=[('draft', 'Offer'),
                                            ('sent', 'Offer Sent')])
    
    is_sent = fields.Boolean("Sent to buyer", compute="_compute_is_sent", store=True)
    is_invoice_generated = fields.Boolean("Afrex Invoice generated", compute="_compute_is_invoice_generated")
    
    lead_id = fields.Many2one('crm.lead')
    purchase_order_id = fields.Many2one('purchase.order')
    supplier_id = fields.Many2one('res.partner', related='purchase_order_id.partner_id')
    
    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method', string="Supplier Delivery Method", tracking=True)
    
    is_currency_zar = fields.Boolean("Currency is ZAR", compute="_compute_is_currency_zar")
    indicative_exchange_rate = fields.Float(related='lead_id.indicative_exchange_rate', digits="Prices per Unit")
    exchange_rate = fields.Float(related='lead_id.exchange_rate', digits="Prices per Unit")

    consignee_id = fields.Many2one('res.partner', string="Consignee", related="lead_id.consignee_id", readonly=False)
    
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms")
    is_indicative = fields.Boolean(string="Quote is indicative", default=True)
    
    is_internal = fields.Boolean("Internal deal", related='lead_id.is_internal')
    
    product_combination_id = fields.Many2one('asc.product.combination', related="lead_id.product_combination_id")
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')
    
    loading_port_id = fields.Many2one('asc.port', "Port of Loading", related="lead_id.loading_port_id", store=True, readonly=False)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related='lead_id.discharge_port_id', readonly=False)
    
    shipment_window_start = fields.Date("Shipment Window Start", related='lead_id.shipment_window_start', readonly=False)
    shipment_window_end = fields.Date("Shipment Window End", related='lead_id.shipment_window_end', readonly=False)
    
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", default='container', related='purchase_order_id.breakbulk_container')
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", related='purchase_order_id.container_type_id')
    container_stuffing = fields.Integer("Container Stuffing", related='purchase_order_id.container_stuffing')
    container_count = fields.Integer("Container Count", related='purchase_order_id.container_count')
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", related='purchase_order_id.is_palletised')
    qty_total = fields.Float("Total Quantity", related='lead_id.product_qty')
    origin_country_id = fields.Many2one('res.country', string="Origin", related='purchase_order_id.origin_country_id')
    
    incoterm_implementation_year = fields.Char("Last Incoterm implentation", related='lead_id.incoterm_implementation_year')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    fob_unit = fields.Float("FOB/MT", compute="_compute_fob_unit", store=True, digits="Prices per Unit", tracking=True)
    freight_unit = fields.Float("Freight/MT", compute="_compute_freight_unit", store=True, digits="Prices per Unit", tracking=True)
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit", tracking=True)
    
    fob_amount = fields.Float("FOB", tracking=True)
    freight_amount = fields.Float("Freight", tracking=True)
    cost_amount = fields.Float("Cost", tracking=True)
    
    insurance_amount = fields.Float("Insurance", tracking=True)
    
    fca_amount = fields.Float("FCA", tracking=True)
    road_transportation_amount = fields.Float(string="Road Transportation and Clearance", tracking=True)
    logistics_service_amount = fields.Float(string="Logistics Service fee", tracking=True)
        
    fca_unit = fields.Float("FCA/MT", compute='_compute_fca_unit', digits="Prices per Unit", tracking=True)
    road_transportation_unit = fields.Float(string="Road Transportation and Clearance per MT", compute='_compute_road_transportation_unit', digits="Prices per Unit", tracking=True)
    logistics_service_unit = fields.Float(string="Logistics Service fee per MT", compute='_compute_logistics_service_unit', digits="Prices per Unit", tracking=True)
    
    show_transportation = fields.Boolean("Display Transportation", help="Show transportation costs in the quotation")
    show_breakdown = fields.Boolean("Display Breakdown", help="Show breakdown of costs in the quotation")
    
    interest_amount = fields.Float("Interest", tracking=True)
    procurement_documentation_amount = fields.Float("Procurement & Documentation", tracking=True)
    
    bank_account_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account")
    
    logistics_state = fields.Selection(related='lead_id.logistics_state')
    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date", readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)
    gross_weight = fields.Float(string="Gross Weight (kg)", related="lead_id.gross_weight", readonly=False)
    net_weight = fields.Float(string="Net Weight (kg)", related="lead_id.net_weight", readonly=False)
    doc_ids = fields.One2many('asc.document', 'sale_order_id', string="Documents to be provided")
    
    quote_request_doc = fields.Binary(string="Request for Quote (RFQ)", attachment=True)
    purchase_order_doc = fields.Binary(string="Purchase Order", attachment=True)
    swift_doc = fields.Binary(string="SWIFT / Proof of Payment", attachment=True)
    kyc_doc = fields.Binary(string="KYC Documents", attachment=True)
    buyer_registration_doc = fields.Binary(string="Buyer Registration Form", attachment=True)
    
    tariff_code = fields.Char(string="Tariff Code")
    
    
    @api.depends('currency_id')
    def _compute_is_currency_zar(self):
        for rec in self:
            if rec.currency_id == self.env.ref('base.ZAR'):
                rec.is_currency_zar = True
            else:
                rec.is_currency_zar = False
    
    @api.depends('incoterm_id')
    def _compute_incoterm_selection(self):
        for rec in self:
            incoterm = rec.incoterm_id
            if incoterm:
                if incoterm == self.env.ref('account.incoterm_CFR'):
                    rec.incoterm_selection = 'cfr'
                elif incoterm == self.env.ref('account.incoterm_CIF'):
                    rec.incoterm_selection = 'cif'
                elif incoterm == self.env.ref('account.incoterm_FOB'):
                    rec.incoterm_selection = 'fob'
                elif incoterm == self.env.ref('account.incoterm_DAP'):
                    rec.incoterm_selection = 'dap'
                elif incoterm == self.env.ref('account.incoterm_FCA'):
                    rec.incoterm_selection = 'fca'
                else:
                    raise UserError("This incoterm is not allowed for a deal yet.")
            else:
                rec.incoterm_selection = False
                
    @api.onchange('incoterm_id','insurance_amount')
    def check_incoterm_insurance(self):
        for rec in self:
            if rec.incoterm_id == self.env.ref('account.incoterm_CFR'):
                if rec.insurance_amount > 0:
                    raise UserError("Insurance amount should be 0 for a CFR sale.")
    
    @api.onchange('cost_unit')
    def set_product_cost(self):
        for rec in self:
            for line in rec.order_line:
                line.price_unit = rec.cost_unit
            
    @api.onchange('qty_total')
    def set_product_qty(self):
        for rec in self:
            for line in rec.order_line:
                line.product_uom_qty = rec.qty_total
                
    @api.depends('state')
    def _compute_is_sent(self):
        for rec in self:
            if rec.state == 'sent':
                rec.is_sent = True
            else:
                rec.is_sent = False
                
    @api.depends('invoice_ids')
    def _compute_is_invoice_generated(self):
        for rec in self:
            if rec.invoice_ids:
                rec.is_invoice_generated = True
            else:
                rec.is_invoice_generated = False
                    
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
                
    @api.depends('fca_amount','qty_total')
    def _compute_fca_unit(self):
        for rec in self:
            try:
                rec.fca_unit = rec.fca_amount / rec.qty_total
            except ZeroDivisionError:
                rec.fca_unit = 0
                
    @api.depends('road_transportation_amount','qty_total')
    def _compute_road_transportation_unit(self):
        for rec in self:
            try:
                rec.road_transportation_unit = rec.road_transportation_amount / rec.qty_total
            except ZeroDivisionError:
                rec.road_transportation_unit = 0
                
    @api.depends('logistics_service_amount','qty_total')
    def _compute_logistics_service_unit(self):
        for rec in self:
            try:
                rec.logistics_service_unit = rec.logistics_service_amount / rec.qty_total
            except ZeroDivisionError:
                rec.logistics_service_unit = 0
        
    @api.depends('cost_amount','qty_total')
    def _compute_cost_unit(self):
        for rec in self:
            try:
                rec.cost_unit = rec.cost_amount / rec.qty_total
            except ZeroDivisionError:
                rec.cost_unit = 0
         
    def action_is_sent(self):
        for rec in self:
            rec.state = 'sent'
            rec.is_sent = True
            
    def update_proforma(self):
        self.ensure_one()
        lead = self.lead_id
        if self.invoice_ids:
            for invoice in self.invoice_ids:
                invoice.fob_amount = self.fob_amount
                invoice.freight_amount = self.freight_amount
                invoice.cost_amount = self.cost_amount
                invoice.insurance_amount = self.insurance_amount
                invoice.interest_amount = self.interest_amount
                invoice.procurement_documentation_amount = self.procurement_documentation_amount
                invoice.fob_unit = self.fob_unit
                invoice.freight_unit = self.freight_unit
                invoice.fca_amount = self.fca_amount
                invoice.fca_unit = self.fca_unit
                invoice.road_transportation_amount = self.road_transportation_amount
                invoice.road_transportation_unit = self.road_transportation_unit
                invoice.logistics_service_amount = self.logistics_service_amount
                invoice.logistics_service_unit = self.logistics_service_unit
                invoice.cost_unit = self.cost_unit
        else:
            raise UserError("No invoice found for this sale order.")

    def generate_proforma_wizard(self):
        if self.is_invoice_generated:
            raise UserError("Proforma invoice has already been generated.")

        lead = self.lead_id
        currency = self.currency_id
        exchange_rate = self.exchange_rate or self.indicative_exchange_rate

        # if not exchange_rate or exchange_rate == 0.0:
        #     raise UserError("Exchange rate is missing or zero.")

        is_usd = currency == self.env.ref('base.USD')
        is_zar = currency == self.env.ref('base.ZAR')


        fob = self.fob_amount
        freight = self.freight_amount
        insurance = self.insurance_amount
        interest = self.interest_amount
        fca = self.fca_amount
        road = self.road_transportation_amount
        logistics = self.logistics_service_amount

        if is_usd:

            if lead.is_internal and lead.cover_report_amount:
                roe = lead.exchange_rate or lead.indicative_exchange_rate or exchange_rate
                if not roe or roe == 0:
                    raise UserError("Exchange rate not set or zero.")
                cost_usd = lead.cover_report_amount / roe
                procurement_doc_usd = abs(cost_usd - (fob + freight + insurance + interest))
            else:
                cost_usd = self.cost_amount
                procurement_doc_usd = abs(self.procurement_documentation_amount)


            fob_zar = fob * exchange_rate
            freight_zar = freight * exchange_rate
            insurance_zar = insurance * exchange_rate
            interest_zar = interest * exchange_rate
            fca_zar = fca * exchange_rate
            road_zar = road * exchange_rate
            logistics_zar = logistics * exchange_rate
            cost_zar = cost_usd * exchange_rate
            procurement_doc_zar = procurement_doc_usd * exchange_rate

            context = {
                'default_lead_id': lead.id,
                'default_sale_order_id': self.id,
                'default_incoterm_id': self.incoterm_id.id,
                'default_currency_id': currency.id,
                'default_exchange_rate': exchange_rate,


                'default_fob_amount': fob,
                'default_freight_amount': freight,
                'default_insurance_amount': insurance,
                'default_interest_amount': interest,
                'default_fca_amount': fca,
                'default_road_transportation_amount': road,
                'default_logistics_service_amount': logistics,
                'default_cost_amount': cost_usd,
                'default_procurement_documentation_amount': procurement_doc_usd,


                'default_fob_amount_zar': fob_zar,
                'default_freight_amount_zar': freight_zar,
                'default_insurance_amount_zar': insurance_zar,
                'default_interest_amount_zar': interest_zar,
                'default_fca_amount_zar': fca_zar,
                'default_road_transportation_amount_zar': road_zar,
                'default_logistics_service_amount_zar': logistics_zar,
                'default_cost_amount_zar': cost_zar,
                'default_procurement_documentation_amount_zar': procurement_doc_zar,
            }

        elif is_zar:

            if lead.is_internal and lead.cover_report_amount:
                roe = lead.exchange_rate or lead.indicative_exchange_rate or exchange_rate
                if not roe or roe == 0:
                    raise UserError("Exchange rate not set or zero.")
                cost_zar = lead.cover_report_amount
                procurement_doc_zar = abs(cost_zar - (fob + freight + insurance + interest))
                cost_usd = cost_zar / roe
                procurement_doc_usd = procurement_doc_zar / roe
            else:
                cost_zar = self.cost_amount
                procurement_doc_zar = abs(self.procurement_documentation_amount)
                cost_usd = cost_zar / exchange_rate
                procurement_doc_usd = procurement_doc_zar / exchange_rate


            fob_usd = fob / exchange_rate
            freight_usd = freight / exchange_rate
            insurance_usd = insurance / exchange_rate
            interest_usd = interest / exchange_rate
            fca_usd = fca / exchange_rate
            road_usd = road / exchange_rate
            logistics_usd = logistics / exchange_rate

            context = {
                'default_lead_id': lead.id,
                'default_sale_order_id': self.id,
                'default_incoterm_id': self.incoterm_id.id,
                'default_currency_id': currency.id,
                'default_exchange_rate': exchange_rate,


                'default_fob_amount_zar': fob,
                'default_freight_amount_zar': freight,
                'default_insurance_amount_zar': insurance,
                'default_interest_amount_zar': interest,
                'default_fca_amount_zar': fca,
                'default_road_transportation_amount_zar': road,
                'default_logistics_service_amount_zar': logistics,
                'default_cost_amount_zar': cost_zar,
                'default_procurement_documentation_amount_zar': procurement_doc_zar,


                'default_fob_amount': fob_usd,
                'default_freight_amount': freight_usd,
                'default_insurance_amount': insurance_usd,
                'default_interest_amount': interest_usd,
                'default_fca_amount': fca_usd,
                'default_road_transportation_amount': road_usd,
                'default_logistics_service_amount': logistics_usd,
                'default_cost_amount': cost_usd,
                'default_procurement_documentation_amount': procurement_doc_usd,
            }

        else:
            raise UserError("Only USD and ZAR currencies are supported for proforma generation.")

        return {
            'name': 'Generate Proforma Invoice',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'asc.generate.proforma',
            'target': 'new',
            'context': context,
        }

    # def generate_proforma_wizard(self):
    #     if self.is_invoice_generated:
    #         raise UserError("Proforma invoice has already been generated.")
    #     lead = self.lead_id
    #     if lead.is_internal:
    #         if lead.cover_report_amount:
    #             roe = lead.exchange_rate if lead.exchange_rate else lead.indicative_exchange_rate
    #             if not roe:
    #                 raise UserError("Cover Report Amount is set but the exchange rate is not set.")
    #             try:
    #                 sales_price = lead.cover_report_amount / roe
    #             except ZeroDivisionError:
    #                 sales_price = self.cost_amount
    #             # procurement_documentation_amount = sales_price - (self.fob_amount + self.freight_amount + self.insurance_amount + self.interest_amount)
    #             procurement_documentation_amount = abs(
    #                 sales_price - (
    #                         self.fob_amount +
    #                         self.freight_amount +
    #                         self.insurance_amount +
    #                         self.interest_amount
    #                 )
    #             )
    #         else:
    #             sales_price = self.cost_amount
    #             procurement_documentation_amount = abs(self.procurement_documentation_amount)
    #     else:
    #         sales_price = self.cost_amount
    #         procurement_documentation_amount = abs(self.procurement_documentation_amount)
    #
    #     action = {
    #         'name': 'Generate Proforma Invoice',
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'asc.generate.proforma',
    #         'target': 'new',
    #         'context': {'default_lead_id': self.lead_id.id,
    #                     'default_sale_order_id': self.id,
    #                     'default_incoterm_id': self.incoterm_id.id,
    #                     'default_currency_id': self.currency_id.id,
    #                     'default_exchange_rate': self.exchange_rate or self.indicative_exchange_rate,
    #                     'default_fob_amount': self.fob_amount,
    #                     'default_freight_amount': self.freight_amount,
    #                     'default_insurance_amount': self.insurance_amount,
    #                     'default_interest_amount': self.interest_amount,
    #                     'default_procurement_documentation_amount': procurement_documentation_amount,
    #                     'default_fca_amount': self.fca_amount,
    #                     'default_road_transportation_amount': self.road_transportation_amount,
    #                     'default_logistics_service_amount': self.logistics_service_amount,
    #                     'default_cost_amount': sales_price,}
    #     }
    #     return action
    
    def generate_commercial_invoice(self):
        generated_invoices = self.env['account.move']

        order = self
        downpayment_wizard = self.env['sale.advance.payment.inv'].create({
            'sale_order_ids': order.ids,
            'advance_payment_method': 'delivered',
        })
        generated_invoices |= downpayment_wizard._create_invoices(order)
        
        for invoice in order.invoice_ids:
            # self.lead_id.sale_invoice_id = invoice.id
            return {
                'res_id': invoice.id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'context': {},
                'target': 'new'
            }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'procurement_documentation_amount' in res:
            res['procurement_documentation_amount'] = abs(res['procurement_documentation_amount'])
        return res
    def print_quotation(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_quotation').report_action(self)
    
    def action_open_lead(self):
        self.ensure_one()
        return {
            'res_id': self.lead_id.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
    
    def action_open_profit_estimate(self):
        self.ensure_one()
        return {
            'name': 'Profit Estimate',
            'res_id': self.lead_id.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('afrex_supply_chain.asc_profit_estimate_form_view').id,
            'context': {},
            'target': 'new'
        }
        
    def action_open_purchase_order(self):
        self.ensure_one()
        return {
            'res_id': self.purchase_order_id.id,
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    lead_id = fields.Many2one('crm.lead')
    
    product_combination_id = fields.Many2one('asc.product.combination', related='order_id.product_combination_id')
    
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')