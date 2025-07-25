# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import groupby
from odoo.tools.float_utils import float_is_zero

IGNORED_BINARY_FIELDS = ['tax_totals']

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
        
    lead_id = fields.Many2one('crm.lead')
    sale_order_id = fields.Many2one('sale.order', related='lead_id.sale_order_id')
    sale_invoice_id = fields.Many2one('account.move', related='lead_id.sale_invoice_id')
    is_internal = fields.Boolean("Internal deal", related='lead_id.is_internal')
    is_switch = fields.Boolean(string="Subject to Switch", related='lead_id.is_switch', readonly=False)
    is_invoiced = fields.Boolean("Fully Invoiced")

    product_combination_id = fields.Many2one('asc.product.combination')
    product_id = fields.Many2one('product.template', related='product_combination_id.product_id')
    product_variant_id = fields.Many2one('product.product', related='product_combination_id.product_variant_id')
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')
    
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method', string="Supplier Delivery Method", tracking=True)
    
    loading_port_id = fields.Many2one('asc.port', "Port of Loading", ondelete='restrict', tracking=True, readonly=False, store=True)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related="lead_id.discharge_port_id", readonly=False)
    shipment_window_start = fields.Date("Shipment Window Start", related='lead_id.shipment_window_start', readonly=False)
    shipment_window_end = fields.Date("Shipment Window End", related='lead_id.shipment_window_end', readonly=False)
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", tracking=True)
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", tracking=True)
    container_stuffing = fields.Integer("Container Stuffing", tracking=True)
    container_count = fields.Integer("Container Count")
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", tracking=True)
    qty_total = fields.Float("MT Quantity", tracking=True, digits="Prices per Unit")
    qty_delivered = fields.Float(string="MT Delivered", compute="compute_qty_delivered", store=True, tracking=True, digits="Prices per Unit")
    
    origin_country_id = fields.Many2one('res.country', string="Origin", tracking=True)
    
    trans_shipment = fields.Selection([('allowed', "Allowed"),
                                       ('not', "Not Allowed")],
                                      string="Trans Shipment", tracking=True)
    partial_shipment = fields.Selection([('allowed', "Allowed"),
                                         ('not', "Not Allowed")],
                                        string="Partial Shipment", tracking=True)
    
    incoterm_implementation_year = fields.Char("Last Incoterm implentation", related='lead_id.incoterm_implementation_year')
        
    fob_unit = fields.Float("FOB/MT", digits="Prices per Unit", tracking=True)
    freight_unit = fields.Float("Freight/MT", digits="Prices per Unit", tracking=True)
    cost_unit = fields.Float("Cost/MT", digits="Prices per Unit", tracking=True)
    
    fob_amount = fields.Float("FOB", compute="_compute_fob_amount", store=True, readonly=False, digits="Prices per Unit")
    freight_amount = fields.Float("Freight", readonly=False, digits="Prices per Unit")
    cost_amount = fields.Float("Cost", compute="_compute_cost_amount", store=True, readonly=False, digits="Prices per Unit")
    
    insurance_amount = fields.Float("Insurance", tracking=True, compute="_compute_insurance_amount", store=True, readonly=False)
    
    fca_unit = fields.Float("FCA/MT", digits="Prices per Unit", tracking=True)
    fca_amount = fields.Float("FCA", compute="_compute_fca_amount", store=True, readonly=False, digits="Prices per Unit", tracking=True)
    
    road_transportation_unit = fields.Float(string="Road Transportation and Clearance per MT", tracking=True)
    road_transportation_amount = fields.Float(string="Road Transportation and Clearance", compute='compute_road_transportation_amount', store=True, tracking=True)
        
    logistics_service_unit = fields.Float(string="Logistics Service fee per MT", tracking=True)
    logistics_service_amount = fields.Float(string="Logistics Service fee", compute='compute_logistics_service_amount', store=True, tracking=True)
    
    show_breakdown = fields.Boolean("Display Breakdown", help="Show breakdown of costs in the purchase order")

    validity = fields.Date("Validity", tracking=True)
    
    initial_fob_unit = fields.Float("Initial FOB/MT", digits="Prices per Unit", tracking=True)
    initial_freight_unit = fields.Float("Initial Freight/MT", digits="Prices per Unit", tracking=True)
    initial_cost_unit = fields.Float("Initial Cost/MT", digits="Prices per Unit", tracking=True)
    initial_fob_amount = fields.Float("Initial FOB", tracking=True)
    initial_freight_amount = fields.Float("Initial Freight", tracking=True)
    initial_cost_amount = fields.Float("Initial Cost", tracking=True)
    initial_insurance_amount = fields.Float("Initial Insurance", tracking=True)
    initial_fca_unit = fields.Float("Initial FCA/MT", digits="Prices per Unit", tracking=True)
    initial_fca_amount = fields.Float("Initial FCA", tracking=True)
    initial_road_transportation_unit = fields.Float(string="Initial Road Transportation and Clearance per MT", tracking=True)
    initial_road_transportation_amount = fields.Float(string="Initial Road Transportation and Clearance", tracking=True)
    initial_logistics_service_unit = fields.Float(string="Initial Logistics Service fee per MT", tracking=True)
    initial_logistics_service_amount = fields.Float(string="Initial Logistics Service fee", tracking=True)
    
    supplier_reference_doc_date = fields.Date("Vendor Reference Document Date")
    supplier_contract_num = fields.Char("Vendor Sales Contract Ref")
    supplier_contract_date = fields.Date("Vendor Sales Contract Date")
    
    is_sent = fields.Boolean("Sent to supplier", compute="_compute_is_sent", store=True)
    is_payment_request_generated = fields.Boolean("Payment Requests Generated")
    
    outgoing_doc_ids = fields.One2many('asc.document', 'purchase_order_id', domain=[('type','=', 'outgoing')], string="Documents to be provided")
    incoming_doc_ids = fields.One2many('asc.document', 'purchase_order_id', domain=[('type','=', 'incoming')], string="Documents to receive")
    
    payment_request_ids = fields.One2many('asc.payment.request', 'purchase_order_id', string="Payment Requests")
    cost_ids = fields.One2many('asc.cost', 'purchase_order_id', string="Additional Costs & Charges")
    cost_total = fields.Float(string="Total Additional Costs/Charges", compute="compute_cost_total")
    
    first_consignee_id = fields.Many2one('res.partner', string="Consignee/Notify 1")
    second_consignee_id = fields.Many2one('res.partner', string="Notify 2")
    
    transporter_id = fields.Many2one('res.partner', string="Transporter", copy=False)
    clearing_agent_id = fields.Many2one('res.partner', string="Clearing Agent", copy=False)
    
    expected_sob_date = fields.Date("Expected Shipped on Board Date", related='lead_id.expected_sob_date', readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related='lead_id.sob_date')
    
    is_selected = fields.Boolean("Selected for deal")
  
  
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
    
    @api.onchange('insurance_amount')
    def check_incoterm_insurance(self):
        for rec in self:
            if rec.incoterm_id == self.env.ref('account.incoterm_CFR'):
                if rec.insurance_amount > 0:
                    raise UserError("Insurance amount should be 0 for a CFR deal.")
    
    @api.onchange('cost_unit')
    def set_product_cost(self):
        for line in self.order_line:
            line.price_unit = self.cost_unit
            
    @api.onchange('qty_total')
    def set_product_qty(self):
        for rec in self:
            for line in rec.order_line:
                line.product_qty = rec.qty_total
                
    @api.depends('road_transportation_unit', 'qty_total')
    def compute_road_transportation_amount(self):
        for rec in self:
            rec.road_transportation_amount = rec.road_transportation_unit * rec.qty_total
                        
    @api.depends('logistics_service_unit', 'qty_total')
    def compute_logistics_service_amount(self):
        for rec in self:
            rec.logistics_service_amount = rec.logistics_service_unit * rec.qty_total
    
    @api.depends('order_line', 'order_line.qty_received')
    def compute_qty_delivered(self):
        for rec in self:
            total = 0
            for line in rec.order_line:
                total += line.qty_received
            rec.qty_delivered = total
                
    @api.depends('state')
    def _compute_is_sent(self):
        for rec in self:
            if rec.state == 'sent':
                rec.is_sent = True
            else:
                rec.is_sent = False
                    
    @api.depends('fob_unit', 'qty_total', 'qty_delivered')
    def _compute_fob_amount(self):
        for rec in self:
            if rec.qty_delivered > 0:
                rec.fob_amount = rec.fob_unit * rec.qty_delivered
            else:
                rec.fob_amount = rec.fob_unit * rec.qty_total
                    
    @api.depends('fca_unit','qty_total', 'qty_delivered')
    def _compute_fca_amount(self):
        for rec in self:
            if rec.incoterm_selection == 'fca':
                if rec.qty_delivered > 0:
                    rec.cost_unit = rec.fca_unit
                    rec.fca_amount = rec.fca_unit * rec.qty_delivered
                else:
                    rec.cost_unit = rec.fca_unit
                    rec.fca_amount = rec.fca_unit * rec.qty_total
            else:
                if rec.qty_delivered > 0:
                    rec.fca_amount = rec.fca_unit * rec.qty_delivered
                else:
                    rec.fca_amount = rec.fca_unit * rec.qty_total
        
    @api.onchange('freight_unit', 'qty_total', 'qty_delivered')
    def _compute_freight_amount(self):
        for rec in self:
            if rec.breakbulk_container == 'breakbulk':
                if rec.qty_delivered > 0:
                    rec.freight_amount = rec.freight_unit * rec.qty_delivered
                else:
                    rec.freight_amount = rec.freight_unit * rec.qty_total
                    
    @api.onchange('freight_amount', 'qty_total', 'qty_delivered')
    def _compute_freight_unit(self):
        for rec in self:
            if rec.breakbulk_container == 'container':
                if rec.qty_delivered > 0:
                    rec.freight_unit = rec.freight_amount / rec.qty_delivered
                else:
                    try:
                        rec.freight_unit = rec.freight_amount / rec.qty_total
                    except ZeroDivisionError:
                        rec.freight_unit = 0.0

    @api.depends('cost_unit', 'qty_total', 'qty_delivered')
    def _compute_cost_amount(self):
        for rec in self:
            if rec.qty_delivered > 0:
                rec.cost_amount = rec.cost_unit * rec.qty_delivered
            else:
                rec.cost_amount = rec.cost_unit * rec.qty_total
            
# NEEDS TO BE REFACTORED
    @api.depends('invoice_ids')
    def _compute_insurance_amount(self):
        for rec in self:
            if rec.invoice_ids:
                insurance = 0
                for invoice in rec.invoice_ids:
                    insurance += invoice.insurance_amount
                rec.insurance_amount = insurance
            
    @api.depends('cost_ids', 'cost_ids.amount')
    def compute_cost_total(self):
        for rec in self:
            total = 0
            for cost in rec.cost_ids:
                total += cost.amount
            rec.cost_total = total
    
    def action_is_sent(self):
        for rec in self:
            rec.state = 'sent'
            rec.is_sent = True
            
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
        
    def action_open_sale_order(self):
        self.ensure_one()
        return {
            'res_id': self.sale_order_id.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
        
    def action_open_sale_invoice(self):
        self.ensure_one()
        return {
            'res_id': self.sale_invoice_id.id,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
                
    def action_mark_invoiced(self):
        for rec in self:
            advance_amount = 0
            qty = rec.qty_delivered
            for line in rec.order_line:
                line.product_qty = qty
            rec.invoice_status = 'invoiced'
            rec.fob_amount = rec.fob_unit * rec.qty_delivered
            rec.fca_amount = rec.fca_unit * rec.qty_delivered
            rec.freight_amount = rec.freight_unit * rec.qty_delivered
            rec.cost_amount = rec.cost_unit * rec.qty_delivered
            advance_payments = self.env['asc.payment.request'].search([('purchase_order_id', '=', rec.id),('type', '=', 'advance')])
            final_payments = self.env['asc.payment.request'].search([('purchase_order_id', '=', rec.id),('type', '=', 'final')], limit=1)
            if final_payments:
                for payment in advance_payments:
                    advance_amount += payment.amount
                pending = rec.amount_total - advance_amount
                if pending > 0:
                    final_payments.amount = pending
            rec.is_invoiced = True
            return {
                'res_id': self.sale_invoice_id.id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {},
                'target': 'current'
            }
                
    def action_set_select(self):
        self.ensure_one()
        lead = self.lead_id
        if not lead:
            raise UserError("No trade folder found.")
        lead.purchase_order_id = self.id
        lead.packaging_id = self.packaging_id.id
        lead.breakbulk_container = self.breakbulk_container
        lead.is_palletised = self.is_palletised
        lead.container_count = self.container_count
        lead.container_type_id = self.container_type_id.id
        lead.container_stuffing = self.container_stuffing
        lead.trans_shipment = self.trans_shipment
        lead.partial_shipment = self.partial_shipment
        lead.product_qty = self.qty_total
        self.is_selected = True
        orders = self.env['purchase.order'].sudo().search([('lead_id', '=', lead.id), ('id', '!=', self.id)])
        for ord in orders:
            ord.is_selected = False
            
    def action_unselect(self):
        for rec in self:
            lead = rec.lead_id
            if not lead:
                raise UserError("No trade folder found.")
            # Unlink PO from lead
            if lead.purchase_order_id == rec:
                lead.purchase_order_id = False
                lead.packaging_id = False
                lead.breakbulk_container = False
                lead.is_palletised = False
                lead.container_count = 0
                lead.container_type_id = False
                lead.container_stuffing = False
                lead.trans_shipment = False
                lead.partial_shipment = False
            rec.is_selected = False
        
    def action_select(self):
        self.ensure_one()
        # if not self.cost_unit:
        #     raise UserError("No cost set.")
        self.action_set_select()
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
            
    def update_sales_order(self):
        self.ensure_one()
        self.action_set_select()
        lead = self.lead_id
        sale_order = lead.sale_order_id
        if not sale_order:
            raise UserError("No offer found.")
        else:
            lead.sudo().compute_sales_price()
            self.env.cr.commit()
            insurance = self.insurance_amount
            freight = self.freight_amount
            fca = self.fca_amount
            interest = lead.credit_cost_amount
            procurement = lead.procurement_fee_amount
            if lead.is_sales_price_override:
                sales_price = lead.agreed_sales_price
            else:
                sales_price = lead.sales_price
            if sale_order.incoterm_selection in ['cfr','fob']:
                insurance = 0.0
            if not lead.is_internal:
                fob = sales_price - (insurance + freight)
            else:
                fob = sales_price - (insurance + freight + interest + procurement)
            if sale_order.is_currency_zar:
                exchange_rate = lead.indicative_exchange_rate
                insurance = insurance * exchange_rate
                freight = freight * exchange_rate
                fob = fob * exchange_rate
                fca = fca * exchange_rate
                interest = interest * exchange_rate
                procurement = procurement * exchange_rate
                sales_price = sales_price * exchange_rate
            freight_unit = freight / self.qty_total
            fca_unit = fca / self.qty_total
            fob_unit = fob / self.qty_total
            cost_unit = sales_price / self.qty_total
            new_vals = {
                'qty_total': self.qty_total,
                'freight_amount': freight,
                'insurance_amount': insurance,
                'fob_amount': fob,
                'cost_amount': sales_price,
                'interest_amount': interest,
                'procurement_documentation_amount': procurement,
                'freight_unit': freight_unit,
                'fob_unit': fob_unit,
                'fca_unit': fca_unit,
                'cost_unit': cost_unit,
            }
            sale_order.write(new_vals)
            for line in sale_order.order_line:
                line.product_uom_qty = self.qty_total
                line.price_unit = cost_unit
    
    def update_sales_order_wizard(self):
        self.ensure_one()
        self.action_set_select()
        lead = self.lead_id
        sale_order = self.sale_order_id
        if not sale_order:
            raise UserError("No offer found.")
        else:
            lead.sudo().compute_sales_price()
            self.env.cr.commit()
            insurance = self.insurance_amount
            freight = self.freight_amount
            fca = self.fca_amount
            interest = lead.credit_cost_amount
            procurement = lead.procurement_fee_amount
            if lead.is_sales_price_override:
                sales_price = lead.agreed_sales_price
            else:
                sales_price = lead.sales_price
            if sale_order.incoterm_selection in ['cfr','fob']:
                insurance = 0.0
            if not lead.is_internal:
                fob = sales_price - (insurance + freight)
            else:
                fob = sales_price - (insurance + freight + interest + procurement)
            if sale_order.is_currency_zar:
                exchange_rate = lead.indicative_exchange_rate
                insurance = insurance * exchange_rate
                freight = freight * exchange_rate
                fob = fob * exchange_rate
                fca = fca * exchange_rate
                interest = interest * exchange_rate
                procurement = procurement * exchange_rate
                sales_price = sales_price * exchange_rate
            freight_unit = freight / self.qty_total
            fob_unit = fob / self.qty_total
            cost_unit = sales_price / self.qty_total
            action = {
            'name': 'Update Offer',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.update.sale.order',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_cost_amount': sales_price,
                        'default_freight_amount': freight,
                        'default_fca_amount': fca,
                        'default_insurance_amount': insurance,
                        'default_interest_amount': interest,
                        'default_procurement_documentation_amount': procurement,
                        'default_fob_zar': fob,
                        'default_cif_zar': fob + insurance + freight,
                        'default_interest_zar': interest,
                        }
        }
        return action
            
            
    def button_confirm(self):
        self.ensure_one()
        if not self.payment_term_id:
            raise UserError("Please set the Payments Terms.")
        if not self.origin_country_id:
            raise UserError("Please set the Country of Origin.")
        if not self.first_consignee_id:
            raise UserError("Please set the Consignee/Notify 1.")
        if not self.second_consignee_id:
            raise UserError("Please set the Notify 2.")
        if not self.sale_order_id:
            raise UserError("No Afrex Offer has been generated yet.")
        # if not self.partner_ref:
        #     raise UserError("Supplier PFI No. is missing.")
        if not self.cost_unit:
            raise UserError("No cost set.")
        # if not self.partner_id.ref:
        #     raise UserError("The reference used as prefix deal/trade folders is not set for the supplier %s." % self.partner_id.name)
        confirm = super(PurchaseOrder, self).button_confirm()
        self.action_set_select()
        lead = self.lead_id
        lead.purchase_order_id = self.id
        lead.product_qty = self.qty_total
        lead.is_purchase_order_confirmed = True
        seq = self.env['ir.sequence'].next_by_code('purchase.order.confirm')
        self.name = seq
        
        if self.incoterm_selection == 'fob':
            self.fob_unit = self.cost_unit
            self.fob_amount = self.cost_amount
            self.freight_unit = 0.0
            self.freight_amount = 0.0
            self.insurance_amount = 0.0
            self.fca_unit = 0.0
            self.fca_amount = 0.0
            self.road_transportation_unit = 0.0
            self.road_transportation_amount = 0.0
            self.logistics_service_unit = 0.0
            self.logistics_service_amount = 0.0
        elif self.incoterm_selection == 'cfr':
            self.insurance_amount = 0.0
            self.fca_unit = 0.0
            self.fca_amount = 0.0
            self.road_transportation_unit = 0.0
            self.road_transportation_amount = 0.0
            self.logistics_service_unit = 0.0
            self.logistics_service_amount = 0.0
        elif self.incoterm_selection == 'cif':
            self.fca_unit = 0.0
            self.fca_amount = 0.0
            self.road_transportation_unit = 0.0
            self.road_transportation_amount = 0.0
            self.logistics_service_unit = 0.0
            self.logistics_service_amount = 0.0
        elif self.incoterm_selection == 'dap':
            self.fob_unit = 0.0
            self.fob_amount = 0.0
            self.freight_unit = 0.0
            self.freight_amount = 0.0
            self.insurance_amount = 0.0
        elif self.incoterm_selection == 'fca':
            self.fob_unit = 0.0
            self.fob_amount = 0.0
            self.freight_unit = 0.0
            self.freight_amount = 0.0
            self.insurance_amount = 0.0
        
        self.initial_fob_unit = self.fob_unit
        self.initial_fca_unit = self.fca_unit
        self.initial_freight_unit = self.freight_unit
        self.initial_cost_unit = self.cost_unit
        self.initial_fob_amount = self.fob_amount
        self.initial_fca_amount = self.fca_amount
        self.initial_freight_amount = self.freight_amount
        self.initial_cost_amount = self.cost_amount
        self.initial_insurance_amount = self.insurance_amount
        self.initial_road_transportation_unit = self.road_transportation_unit
        self.initial_road_transportation_amount = self.road_transportation_amount
        self.initial_logistics_service_unit = self.logistics_service_unit
        self.initial_logistics_service_amount = self.logistics_service_amount
        
        orders = self.env['purchase.order'].sudo().search([('lead_id', '=', lead.id), ('id', '!=', self.id)])
        orders.button_cancel()
        lead.action_set_won_rainbowman()
        combination = self.product_combination_id
        supplier = self.partner_id
        if combination and supplier not in combination.supplier_ids:
            combination.supplier_ids = [(4, supplier.id)]
            product = combination.product_id
            message = (
                f"Supplier <b>{supplier.name}</b> was added to Product Combination "
                f"<b>{combination.name}</b> during PO confirmation "
                f"(PO: <a href='/web#id={self.id}&model=purchase.order'>{self.name}</a>)."
            )
            product.message_post(body=message, subtype_xmlid="mail.mt_note")
        # return {
        #     'res_id': self.sale_order_id.id,
        #     'res_model': 'sale.order',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'view_type': 'form',
        #     'context': {},
        #     'target': 'current'
        # }
        
    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        self.action_unselect()
            
    def update_packaging_wizard(self):
        if self.state in ['purchase', 'done']:
            raise UserError("PO is already confirmed. The packaging cannot be changed.")
        if not self.lead_id:
            raise UserError("No trade folder found.")
        action = {
            'name': 'Update Product Packaging',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.update.packaging',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_product_id': self.product_id.id,
                        'default_first_spec_id': self.first_spec_id.id,
                        'default_second_spec_id': self.second_spec_id.id,
                        'default_third_spec_id': self.third_spec_id.id,
                        'default_packaging_id': self.packaging_id.id,}
        }
        return action
        
    def generate_sale_order_wizard(self):
        if not self.lead_id:
            raise UserError("No lead found.")
        else:
            lead = self.lead_id
        if not self.origin_country_id:
            raise UserError("Please set the Country of Origin.")
        if self.supplier_delivery_method == 'sea' and self.breakbulk_container == 'container':
            if not self.container_type_id:
                raise UserError("Please set the container size.")
            if not self.container_count:
                raise UserError("Please set the number of %s containers." % self.container_type_id.name)
            if not self.container_stuffing:
                raise UserError("Please set the stuffing for %s." % self.packaging_id.name)
        if self.sale_order_id:
            sale_order = self.sale_order_id
            if sale_order.state == 'sale':
                raise UserError("An offer has already been confirmed for this deal. Refer to %s" % str(self.sale_order_id.name))
            elif sale_order.state == 'sent':
                raise UserError("An offer has already been sent to the buyer for this deal. Refer to %s" % str(self.sale_order_id.name))
        self.lead_id.sudo().compute_sales_price()
        self.env.cr.commit()

        if self.supplier_delivery_method == 'sea':
            # Insurance
            if self.incoterm_selection == 'cif':
                insurance = self.insurance_amount
            else:
                insurance = lead.insurance_premium_amount
            # Freight
            if self.incoterm_selection == 'fob':
                freight = lead.afrex_freight_amount
            else:
                freight = self.freight_amount
            fca = 0
            road_transportation = 0
            logistics_service = 0
        
        interest = lead.credit_cost_amount

        if lead.is_sales_price_override:
            sales_price = lead.agreed_sales_price
        else:
            sales_price = lead.sales_price

        if not lead.is_internal:
            procurement = lead.procurement_fee_amount
            fob = sales_price - (insurance + freight)
        else:
            fob = self.fob_amount
            procurement = sales_price - (fob + insurance + freight + interest)

        if self.supplier_delivery_method == 'road':
            fca = self.fca_amount
            road_transportation = self.road_transportation_amount
            logistics_service = self.logistics_service_amount
            fob = 0
            insurance = 0
            freight = 0

        incoterm = lead.sale_order_incoterm_id or lead.tentative_sale_order_incoterm_id
        net_weight = lead.product_qty * 1000  # Assuming 1 MT = 1000 kg
        action = {
            'name': 'Generate Offer',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.generate.sale.order',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_loading_port_id': self.loading_port_id.id,
                        'default_currency_id': self.currency_id.id,
                        'default_cost_amount': sales_price,
                        'default_fob_amount': fob,
                        'default_freight_amount': freight,
                        'default_insurance_amount': insurance,
                        'default_interest_amount': interest,
                        'default_procurement_documentation_amount': procurement,
                        'default_fca_amount': fca,
                        'default_road_transportation_amount': road_transportation,
                        'default_logistics_service_amount': logistics_service,
                        'default_net_weight': net_weight,
                        'default_payment_term_id': lead.sale_order_terms_id.id or lead.tentative_sale_order_terms_id.id,
                        'default_incoterm_id': incoterm.id,}
        }
        return action
    
    def generate_payment_request_wizard(self):
        if self.state not in ['purchase', 'done']:
            raise UserError("PO needs to be confirmed.")
        if not self.payment_term_id:
            raise UserError("Please set the payments terms.")
        action = {
            'name': 'Generate Payment Request',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.generate.payment.request',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_currency_id': self.currency_id.id,}
        }
        return action
    
    def supplier_invoice_wizard(self):
        qty_invoiced = 0
        qty_received = 0
        for line in self.order_line:
            qty_received = line.qty_received
            qty_invoiced = line.qty_invoiced
        qty_to_invoice = qty_received - qty_invoiced
        if qty_to_invoice <= 0:
            raise UserError("No quantity remaining to invoice.")
        initial_insurance = self.initial_insurance_amount
        current_insurance = self.insurance_amount
        if initial_insurance == current_insurance:
            insurance_amount = current_insurance
        else:
            if initial_insurance > 0:
                insurance_amount = initial_insurance - current_insurance
            else:
                insurance_amount = current_insurance
        action = {
            'name': 'Supplier Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.supplier.invoice',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_quantity': qty_to_invoice,
                        'default_date': fields.Date.today(),
                        'default_fob_unit': self.fob_unit,
                        'default_fca_unit': self.fca_unit,
                        'default_freight_unit': self.freight_unit,
                        'default_cost_unit': self.cost_unit,
                        'default_fob_amount': self.fob_amount,
                        'default_freight_amount': self.freight_amount,
                        'default_cost_amount': self.cost_amount,
                        'default_insurance_amount': insurance_amount,
                        }
        }
        return action
    
    def set_incoming_document_wizard(self):
        action = {
            'name': 'Set list of documents',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.set.document',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_type': 'incoming',
                        'default_responsible': 'supplier'}
        }
        return action
    
    def set_outgoing_document_wizard(self):
        action = {
            'name': 'Set list of documents',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.set.document',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_type': 'outgoing',
                        'default_responsible': 'supplier'}
        }
        return action
    
    def action_create_invoice(self):
        res = super().action_create_invoice()
        if self.invoice_ids:
            for invoice in self.invoice_ids:
                invoice.lead_id = self.lead_id.id

    @api.model
    def create(self, vals):
        """Automatically create attachments for all Binary fields, except ignored ones."""
        record = super(PurchaseOrder, self).create(vals)
        binary_fields = [
            field for field in self._fields 
            if self._fields[field].type == 'binary' and field not in IGNORED_BINARY_FIELDS
        ]
        
        for field in binary_fields:
            file_name_field = f"{field}_name"
            file_name = vals.get(file_name_field) or f"{field}.bin"  # Ensure filename exists

            if vals.get(field):  # If a file is uploaded
                self.env['ir.attachment'].create({
                    'name': file_name,  # Always set a valid name
                    'type': 'binary',
                    'datas': vals[field],
                    'res_model': self._name,
                    'res_id': record.id,
                })
        return record
    
    def write(self, vals):
        """Ensure order_line price_unit is updated even if readonly"""
        res = super().write(vals)
        if 'cost_unit' in vals:
            for order in self:
                order.order_line.write({'price_unit': order.cost_unit})
        if 'qty_total' in vals:
            for order in self:
                order.order_line.write({'product_qty': order.qty_total})
        '''To allow receipts beyond order quantity'''
        if 'is_shipped' not in vals:
            for order in self:
                order.is_shipped = False
        
        binary_fields = [
            field for field in self._fields 
            if self._fields[field].type == 'binary' and field not in IGNORED_BINARY_FIELDS
        ]

        for field in binary_fields:
            if field in vals:  # Only process updated fields
                file_name_field = f"{field}_name"
                file_name = vals.get(file_name_field) or self[file_name_field] or f"{field}.bin"

                attachment = self.env['ir.attachment'].search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                ], limit=1)

                if attachment:
                    attachment.write({'datas': vals[field], 'name': file_name})
                else:
                    self.env['ir.attachment'].create({
                        'name': file_name,  # Always provide a valid filename
                        'type': 'binary',
                        'datas': vals[field],
                        'res_model': self._name,
                        'res_id': self.id,
                    })
        return res
    
    def print_quote_request(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_quote_request').report_action(self)
    
    def print_purchase_order(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_purchase_order').report_action(self)
    
    def print_shipping_instructions(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_shipping_instructions').report_action(self)
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    lead_id = fields.Many2one('crm.lead')
    
    product_combination_id = fields.Many2one('asc.product.combination')
    
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')
    