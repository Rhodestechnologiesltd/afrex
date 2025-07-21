from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class GenerateSaleOrderWizard(models.TransientModel):
    _name = 'asc.generate.sale.order'
    _description = 'Generate Sale Order Wizard'

    purchase_order_id = fields.Many2one('purchase.order')
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id', string="Trade Folder")
    is_internal = fields.Boolean("Trademaw", related='lead_id.is_internal')
    
    is_indicative = fields.Boolean(string="Quote is indicative", default=True)
    validity_date = fields.Date("Validity")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms")
    
    product_combination_id = fields.Many2one('asc.product.combination', string="Product", related='purchase_order_id.product_combination_id')
    product_id = fields.Many2one('product.template', related='product_combination_id.product_id', string="Product")
    product_specification = fields.Char(related='product_combination_id.description', string="Specification")
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id', string="Packaging")

    qty_total = fields.Float(string="MT Ordered", related='purchase_order_id.qty_total')
    
    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method')

    loading_port_id = fields.Many2one('asc.port', "Port of Loading", related='purchase_order_id.loading_port_id', store=True, readonly=False)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related='purchase_order_id.discharge_port_id', readonly=False)
    
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms", required=True)
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    currency_id = fields.Many2one('res.currency')
    is_currency_zar = fields.Boolean("Currency is ZAR")
    exchange_rate = fields.Float(related="lead_id.indicative_exchange_rate", string="Indicative Rate of Exchange (ROE) USDZAR", digits="Prices per Unit")
    
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", related='purchase_order_id.breakbulk_container')
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", related='purchase_order_id.container_type_id')
    container_stuffing = fields.Integer("Container Stuffing", related='purchase_order_id.container_stuffing')
    container_count = fields.Integer("Container Count", related='purchase_order_id.container_count')
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", related='purchase_order_id.is_palletised')
    
    net_weight = fields.Float(string="Net Weight (kg)", related="lead_id.net_weight", readonly=False)
    
    
    fob_amount = fields.Float("FOB", compute="_compute_fob_amount", store=True)
    freight_amount = fields.Float("Freight")
    cost_amount = fields.Float("Cost")
    insurance_amount = fields.Float("Insurance")
    interest_amount = fields.Float("Interest")
    procurement_documentation_amount = fields.Float("Procurement & Documentation")
    
    fca_amount = fields.Float("FCA", compute="_compute_fca_amount", store=True, readonly=False)
    road_transportation_amount = fields.Float("Road Transportation")
    logistics_service_amount = fields.Float("Logistics Service")
    
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit")
    
    fob_amount_zar = fields.Float("FOB in ZAR")
    freight_amount_zar = fields.Float("Freight in ZAR")
    cost_amount_zar = fields.Float("Cost in ZAR")
    insurance_amount_zar = fields.Float("Insurance in ZAR")
    interest_amount_zar = fields.Float("Interest in ZAR")
    procurement_documentation_amount_zar = fields.Float("Procurement & Documentation in ZAR")
    
    fca_amount_zar = fields.Float("FCA in ZAR")
    road_transportation_amount_zar = fields.Float("Road Transportation in ZAR")
    logistics_service_amount_zar = fields.Float("Logistics Service in ZAR")
    
    fob_unit = fields.Float("FOB/MT", compute="_compute_fob_unit", store=True, digits="Prices per Unit")
    freight_unit = fields.Float("Freight/MT", compute="_compute_freight_unit", store=True, digits="Prices per Unit")
    cost_unit = fields.Float("Cost/MT", compute="_compute_cost_unit", store=True, digits="Prices per Unit")
    
    fca_unit = fields.Float("FCA/MT", compute="_compute_fca_unit", store=True, digits="Prices per Unit")
    road_transportation_unit = fields.Float("Road Transportation/MT", compute="_compute_road_transportation_unit", store=True, digits="Prices per Unit")
    logistics_service_unit = fields.Float("Logistics Service/MT", compute="_compute_logistics_service_unit", store=True, digits="Prices per Unit")
    
    fob_unit_zar = fields.Float("FOB/MT in ZAR", compute="_compute_fob_unit_zar", store=True, digits="Prices per Unit")
    freight_unit_zar = fields.Float("Freight/MT in ZAR", compute="_compute_freight_unit_zar", store=True, digits="Prices per Unit")
    cost_unit_zar = fields.Float("Cost/MT in ZAR", compute="_compute_cost_unit_zar", store=True, digits="Prices per Unit")
    
    fca_unit_zar = fields.Float("FCA/MT in ZAR", compute="_compute_fca_unit_zar", store=True, digits="Prices per Unit")
    road_transportation_unit_zar = fields.Float("Road Transportation/MT in ZAR", compute="_compute_road_transportation_unit_zar", store=True, digits="Prices per Unit")
    logistics_service_unit_zar = fields.Float("Logistics Service/MT in ZAR", compute="_compute_logistics_service_unit_zar", store=True, digits="Prices per Unit")
   
   
    @api.onchange('qty_total')
    def compute_net_weight(self):
       for rec in self:
           rec.net_weight = rec.qty_total * 1000
    
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
                    rec.fca_amount = rec.purchase_order_id.fca_amount
                    rec.fca_amount_zar = rec.purchase_order_id.fca_amount * rec.exchange_rate
                    rec.road_transportation_amount = rec.purchase_order_id.road_transportation_amount
                    rec.road_transportation_amount_zar = rec.purchase_order_id.road_transportation_amount * rec.exchange_rate
                elif incoterm == self.env.ref('account.incoterm_FCA'):
                    rec.incoterm_selection = 'fca'
                    rec.fob_amount = 0.0
                    rec.fob_amount_zar = 0.0
                    rec.insurance_amount = 0.0
                    rec.insurance_amount_zar = 0.0
                    rec.freight_amount = 0.0
                    rec.freight_amount_zar = 0.0
                    rec.fca_amount = rec.purchase_order_id.cost_amount
                    rec.fca_amount_zar = rec.purchase_order_id.cost_amount * rec.exchange_rate
                    rec.road_transportation_amount = 0.0
                    rec.road_transportation_amount_zar = 0.0
                else:
                    raise UserError("This incoterm is not allowed for a deal yet.")
            else:
                rec.incoterm_selection = False
                
                
    @api.onchange('currency_id')
    def _compute_is_currency_zar(self):
        for rec in self:
            if rec.currency_id == self.env.ref('base.ZAR'):
                rec.is_currency_zar = True
            else:
                rec.is_currency_zar = False
    
    @api.onchange('exchange_rate')
    def compute_zar_amount(self):
        for rec in self:
            rec.fob_amount_zar = rec.fob_amount * rec.exchange_rate
            rec.freight_amount_zar = rec.freight_amount * rec.exchange_rate
            rec.cost_amount_zar = rec.cost_amount * rec.exchange_rate
            rec.insurance_amount_zar = rec.insurance_amount * rec.exchange_rate
            rec.interest_amount_zar = rec.interest_amount * rec.exchange_rate
            rec.procurement_documentation_amount_zar = rec.procurement_documentation_amount * rec.exchange_rate
            rec.fca_amount_zar = rec.fca_amount * rec.exchange_rate
            rec.road_transportation_amount_zar = rec.road_transportation_amount * rec.exchange_rate
            rec.logistics_service_amount_zar = rec.logistics_service_amount * rec.exchange_rate
            rec.fob_unit_zar = rec.fob_unit * rec.exchange_rate
            rec.freight_unit_zar = rec.freight_unit * rec.exchange_rate
            rec.cost_unit_zar = rec.cost_unit * rec.exchange_rate
            rec.fca_unit_zar = rec.fca_unit * rec.exchange_rate
            rec.road_transportation_unit_zar = rec.road_transportation_unit * rec.exchange_rate
            rec.logistics_service_unit_zar = rec.logistics_service_unit * rec.exchange_rate
                
    @api.depends('cost_amount','freight_amount','insurance_amount','interest_amount','procurement_documentation_amount')
    def _compute_fob_amount(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                if rec.is_internal:
                    rec.fob_amount = rec.cost_amount - (rec.freight_amount +  rec.insurance_amount + rec.interest_amount + rec.procurement_documentation_amount)
                    rec.fob_amount_zar = (rec.cost_amount - (rec.freight_amount +  rec.insurance_amount + rec.interest_amount + rec.procurement_documentation_amount)) * self.exchange_rate
                else:
                    rec.fob_amount = rec.cost_amount - (rec.freight_amount +  rec.insurance_amount)
                    rec.fob_amount_zar = (rec.cost_amount - (rec.freight_amount +  rec.insurance_amount)) * self.exchange_rate
            else:
                rec.fob_amount = 0.0
                rec.fob_amount_zar = 0.0
    
    @api.depends('cost_amount','road_transportation_amount','logistics_service_amount','interest_amount','procurement_documentation_amount')
    def _compute_fca_amount(self):
        for rec in self:
            if rec.supplier_delivery_method == 'road':
                if rec.is_internal:
                    rec.fca_amount = rec.cost_amount - (rec.road_transportation_amount + rec.logistics_service_amount + rec.interest_amount + rec.procurement_documentation_amount)
                    rec.fca_amount_zar = (rec.cost_amount - (rec.road_transportation_amount + rec.logistics_service_amount + rec.interest_amount + rec.procurement_documentation_amount)) * self.exchange_rate
                else:
                    rec.fca_amount = rec.cost_amount - rec.road_transportation_amount - rec.logistics_service_amount
                    rec.fca_amount_zar = (rec.cost_amount - rec.road_transportation_amount - rec.logistics_service_amount) * self.exchange_rate
            else:
                rec.fca_amount = 0.0
                rec.fca_amount_zar = 0.0
            
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
    
    @api.depends('fca_amount_zar','qty_total')
    def _compute_fca_unit_zar(self):
        for rec in self:
            try:
                rec.fca_unit_zar = rec.fca_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.fca_unit_zar = 0
    
    @api.depends('road_transportation_amount_zar','qty_total')
    def _compute_road_transportation_unit_zar(self):
        for rec in self:
            try:
                rec.road_transportation_unit_zar = rec.road_transportation_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.road_transportation_unit_zar = 0
                
    @api.depends('logistics_service_amount_zar','qty_total')
    def _compute_logistics_service_unit_zar(self):
        for rec in self:
            try:
                rec.logistics_service_unit_zar = rec.logistics_service_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.logistics_service_unit_zar = 0
    
    @api.depends('cost_amount_zar','qty_total')
    def _compute_cost_unit_zar(self):
        for rec in self:
            try:
                rec.cost_unit_zar = rec.cost_amount_zar / rec.qty_total
            except ZeroDivisionError:
                rec.cost_unit_zar = 0
    
    def generate_sale_order(self):
        order = self.purchase_order_id
        lead = self.lead_id
        
        sale_order = self.env['sale.order'].sudo().search([('lead_id', '=', lead.id), ('state', '=', 'sale')])
        if sale_order:
            raise UserError("An offer has already been confirmed for this deal.")
        
        orders = self.env['sale.order'].sudo().search([('lead_id', '=', lead.id), ('state', 'not in', ['sale', 'cancel'])])
        if orders:
            orders.action_cancel()
            lead.sale_order_id = False
        
        pricelist = self.env['product.pricelist'].search([('currency_id', '=', self.currency_id.id)], limit=1)
        
        if self.currency_id == self.env.ref('base.ZAR'):
            fob_amount = self.fob_amount_zar
            freight_amount = self.freight_amount_zar
            cost_amount = self.cost_amount_zar
            insurance_amount = self.insurance_amount_zar
            interest_amount = self.interest_amount_zar
            procurement_documentation_amount = self.procurement_documentation_amount_zar
            fca_amount = self.fca_amount_zar
            road_transportation_amount = self.road_transportation_amount_zar
            logistics_service_amount = self.logistics_service_amount_zar
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
            fca_amount = self.fca_amount
            road_transportation_amount = self.road_transportation_amount
            logistics_service_amount = self.logistics_service_amount
            fob_unit = self.fob_unit
            freight_unit = self.freight_unit
            cost_unit = self.cost_unit
            
        if self.supplier_delivery_method != 'sea':
            fob_amount = 0.0
            freight_amount = 0.0
            insurance_amount = 0.0
            fob_unit = 0.0
            freight_unit = 0.0
            
        if self.supplier_delivery_method != 'road':
            fca_amount = 0.0
            road_transportation_amount = 0.0
            logistics_service_amount = 0.0
            fca_unit = 0.0
            road_transportation_unit = 0.0
            logistics_service_unit = 0.0
            
        if not self.is_internal:
            interest_amount = 0.0
            procurement_documentation_amount = 0.0
            logistics_service_amount = 0.0
        
        order_vals = {
            'lead_id': lead.id,
            'purchase_order_id': order.id,
            'partner_id': lead.partner_id.id,
            'product_combination_id': order.product_combination_id.id,
            'origin': lead.name,
            'loading_port_id': self.loading_port_id.id,
            'discharge_port_id': self.discharge_port_id.id,
            'pricelist_id': pricelist.id or False,
            'incoterm_id': self.incoterm_id.id,
            'is_indicative': self.is_indicative,
            'validity_date': self.validity_date,
            'payment_term_id': self.payment_term_id.id,
            'breakbulk_container': self.breakbulk_container,
            'container_type_id': self.container_type_id.id,
            'container_count': self.container_count,
            'container_stuffing': self.container_stuffing,
            'is_palletised': self.is_palletised,
            'qty_total': self.qty_total,
            'fob_amount': fob_amount,
            'freight_amount': freight_amount,
            'cost_amount': cost_amount,
            'insurance_amount': insurance_amount,
            'fca_amount': fca_amount,
            'road_transportation_amount': road_transportation_amount,
            'logistics_service_amount': logistics_service_amount,
            'interest_amount': interest_amount,
            'procurement_documentation_amount': procurement_documentation_amount,
        }
        order = order.env['sale.order'].sudo().create(order_vals)
        lead.sale_order_id = order.id
        lead.is_sale_order_generated = True
        line_vals = {
            'name': order.product_combination_id.name,
            'product_combination_id': order.product_combination_id.id,
            'product_id': order.product_combination_id.product_id.product_variant_id.id,
            'product_uom_qty': self.qty_total,
            'price_unit': self.cost_unit,
            'tax_id': False,
            'order_id': order.id,
            'lead_id': lead.id
        }
        order_line = order.env['sale.order.line'].sudo().create(line_vals)
        return {
            'res_id': order.id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }