from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class GenerateProformaWizard(models.TransientModel):
    _name = 'asc.generate.proforma'
    _description = 'Generate Proforma Invoice Wizard'

    lead_id = fields.Many2one('crm.lead')
    sale_order_id = fields.Many2one('sale.order')
    company_id = fields.Many2one('res.company', related='sale_order_id.company_id')
    company_partner_id = fields.Many2one('res.partner', related='company_id.partner_id')
    is_internal = fields.Boolean("Internal deal", related='lead_id.is_internal')
    
    company_id = fields.Many2one('res.company', related='sale_order_id.company_id')
    
    consignee_id = fields.Many2one('res.partner', string="Consignee", default=lambda self: self.sale_order_id.partner_id.id)
    
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms")
    
    bank_account_id = fields.Many2one('res.partner.bank', string="Afrex Bank Account")
    
    product_combination_id = fields.Many2one('asc.product.combination', string="Product", related='sale_order_id.product_combination_id')
    product_id = fields.Many2one('product.template', related='product_combination_id.product_id', string="Product")
    product_specification = fields.Char(related='product_combination_id.description', string="Specification")
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id', string="Packaging")

    qty_total = fields.Float(string="MT Ordered", related='sale_order_id.qty_total')

    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method')
    
    loading_port_id = fields.Many2one('asc.port', "Port of Loading", related='sale_order_id.loading_port_id', store=True, readonly=False)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related='sale_order_id.discharge_port_id', readonly=False)
    
    currency_id = fields.Many2one('res.currency')
    is_currency_zar = fields.Boolean("Currency is ZAR")
    exchange_rate = fields.Float(string="Booked Rate of Exchange", digits="Prices per Unit")
    
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms", related='sale_order_id.incoterm_id')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", related='sale_order_id.breakbulk_container')
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", related='sale_order_id.container_type_id')
    container_stuffing = fields.Integer("Container Stuffing", related='sale_order_id.container_stuffing')
    container_count = fields.Integer("Container Count", related='sale_order_id.container_count')
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", related='sale_order_id.is_palletised')
    sale_purchase_order_num = fields.Char(related='sale_order_id.client_order_ref', string="Buyer PO Reference", readonly=False)
    
    cover_report_amount = fields.Float("Cover Report Amount", related='lead_id.cover_report_amount')

    fob_amount = fields.Float("FOB")
    freight_amount = fields.Float("Freight")
    cost_amount = fields.Float("Cost")
    insurance_amount = fields.Float("Insurance")
    interest_amount = fields.Float("Interest")
    procurement_documentation_amount = fields.Float("Procurement & Documentation")
    
    fca_amount = fields.Float("FCA")
    road_transportation_amount = fields.Float("Road Transportation")
    logistics_service_amount = fields.Float("Logistics Service")
    
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
    
    fob_unit_zar = fields.Float("FOB/MT in ZAR", compute="_compute_fob_unit_zar", store=True, digits="Prices per Unit")
    freight_unit_zar = fields.Float("Freight/MT in ZAR", compute="_compute_freight_unit_zar", store=True, digits="Prices per Unit")
    cost_unit_zar = fields.Float("Cost/MT in ZAR", compute="_compute_cost_unit_zar", store=True, digits="Prices per Unit")
    
    fca_unit = fields.Float("FCA/MT", compute="_compute_fca_unit", store=True, digits="Prices per Unit")
    road_transportation_unit = fields.Float("Road Transportation/MT", compute="_compute_road_transportation_unit", store=True, digits="Prices per Unit")
    logistics_service_unit = fields.Float("Logistics Service/MT", compute="_compute_logistics_service_unit", store=True, digits="Prices per Unit")
    
    fca_unit_zar = fields.Float("FCA/MT in ZAR", compute="_compute_fca_unit_zar", store=True, digits="Prices per Unit")
    road_transportation_unit_zar = fields.Float("Road Transportation/MT in ZAR", compute="_compute_road_transportation_unit_zar", store=True, digits="Prices per Unit")
    logistics_service_unit_zar = fields.Float("Logistics Service/MT in ZAR", compute="_compute_logistics_service_unit_zar", store=True, digits="Prices per Unit")
   
    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date", readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)
    gross_weight = fields.Float(string="Gross Weight (kg)", related="lead_id.gross_weight", readonly=False)
    net_weight = fields.Float(string="Net Weight (kg)", related="lead_id.net_weight", readonly=False)
    
    responsible = fields.Selection([('buyer', "Buyer"),
                                    ('supplier', "Supplier")], string="Responsible/Recipient")
    type = fields.Selection([('incoming', "Incoming"),
                            ('outgoing', "Outgoing")], string="Requirement Type")
    doc_type_ids = fields.Many2many('asc.document.type', string="Documents to be provided", domain="[('id', 'not in', sea_default_doc_type_ids),('id', 'not in', road_default_doc_type_ids)]", readonly=False)
    sea_default_doc_type_ids = fields.Many2many('asc.document.type', related='company_id.sea_sale_invoice_outgoing_doc_ids', string="Default Documents to be provided")
    road_default_doc_type_ids = fields.Many2many('asc.document.type', related='company_id.road_sale_invoice_outgoing_doc_ids', string="Default Documents to be provided")
    
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
                
    @api.onchange('currency_id')
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
    
    @api.onchange('cost_amount','freight_amount','insurance_amount','interest_amount')
    def _compute_sale_values(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                if rec.is_internal:
                    procurement = rec.cost_amount - (rec.fob_amount + rec.freight_amount +  rec.insurance_amount + rec.interest_amount)
                    rec.procurement_documentation_amount = procurement
                    rec.procurement_documentation_amount_zar = procurement * self.exchange_rate
                else:
                    fob = rec.cost_amount - (rec.freight_amount + rec.insurance_amount)
                    rec.fob_amount = fob
                    rec.fob_amount_zar = fob * self.exchange_rate
            else:
                rec.fob_amount = 0.0
                rec.fob_amount_zar = 0.0

    @api.onchange('qty_total')
    def _compute_net_weight(self):
        for rec in self:
            rec.net_weight = rec.qty_total * 1000
            
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
    
    def generate_proforma(self):
        order = self.sale_order_id
        lead = self.lead_id
        documents = self.env['asc.document']
        self._compute_sale_values()
        order.action_confirm()
        
        generated_invoices = self.env['account.move']
        downpayment_wizard = self.env['sale.advance.payment.inv'].create({
            'sale_order_ids': order.ids,
            'advance_payment_method': 'delivered',
        })
        generated_invoices |= downpayment_wizard._create_invoices(order)
        if order.invoice_ids:
            for invoice in order.invoice_ids:
                
                invoice.action_post()
                invoice.button_draft()
                invoice.name = self.env['ir.sequence'].next_by_code('asc.invoice.seq')
                invoice.check_docs = True
                
                if self.currency_id == self.env.ref('base.ZAR'):
                    fob_amount = self.fob_amount_zar
                    freight_amount = self.freight_amount_zar
                    cost_amount = self.cost_amount_zar
                    insurance_amount = self.insurance_amount_zar
                    interest_amount = self.interest_amount_zar
                    procurement_documentation_amount = self.procurement_documentation_amount_zar
                    fob_unit = self.fob_unit_zar
                    freight_unit = self.freight_unit_zar
                    fca_amount = self.fca_amount_zar
                    road_transportation_amount = self.road_transportation_amount_zar
                    logistics_service_amount = self.logistics_service_amount_zar
                    fca_unit = self.fca_unit_zar
                    road_transportation_unit = self.road_transportation_unit_zar
                    logistics_service_unit = self.logistics_service_unit_zar
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
                    fca_amount = self.fca_amount
                    road_transportation_amount = self.road_transportation_amount
                    logistics_service_amount = self.logistics_service_amount
                    fca_unit = self.fca_unit
                    road_transportation_unit = self.road_transportation_unit
                    logistics_service_unit = self.logistics_service_unit
                    cost_unit = self.cost_unit
                    
                if not self.is_internal:
                    interest_amount = 0.0
                    procurement_documentation_amount = 0.0
                    logistics_service_amount = 0.0
                
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
                    
                invoice_vals = {
                    'lead_id': lead.id,
                    'sale_order_id': self.sale_order_id.id,
                    'consignee_id': self.consignee_id.id,
                    'partner_bank_id': self.bank_account_id.id,
                    'invoice_date_due': False,
                    'product_combination_id': order.product_combination_id.id,
                    'invoice_origin': lead.name,
                    'loading_port_id': self.loading_port_id.id,
                    'discharge_port_id': self.discharge_port_id.id,
                    'invoice_incoterm_id': self.incoterm_id.id,
                    'currency_id': self.currency_id.id,
                    'breakbulk_container': self.breakbulk_container,
                    'container_type_id': self.container_type_id.id,
                    'container_count': self.container_count,
                    'container_stuffing': self.container_stuffing,
                    'is_palletised': self.is_palletised,
                    'qty_total': self.qty_total,
                    'fob_amount': fob_amount,
                    'freight_amount': freight_amount,
                    'cost_amount': cost_amount,
                    'fob_unit': fob_unit,
                    'freight_unit': freight_unit,
                    'fca_unit': fca_unit,
                    'road_transportation_unit': road_transportation_unit,
                    'logistics_service_unit': logistics_service_unit,
                    'cost_unit': cost_unit,
                    'insurance_amount': insurance_amount,
                    'interest_amount': interest_amount,
                    'procurement_documentation_amount': procurement_documentation_amount,
                    'fca_amount': fca_amount,
                    'road_transportation_amount': road_transportation_amount,
                    'logistics_service_amount': logistics_service_amount,
                    'vessel': self.vessel,
                    'voyage': self.voyage,
                    'expected_arrival_date': self.expected_arrival_date,
                    'sob_date': self.sob_date,
                    'net_weight': self.net_weight,
                    'ref': self.sale_purchase_order_num,
                }
                invoice.sudo().write(invoice_vals)
                for line in invoice.invoice_line_ids:
                    line.name = order.product_combination_id.name
                    line.product_combination_id = order.product_combination_id.id
                    line.tax_ids = False
                    line.price_unit = cost_unit
                    line.quantity = self.qty_total
                    
                    
                if invoice:
                    if self.supplier_delivery_method == 'sea':
                        incoming_doc_types = invoice.company_id.sea_sale_invoice_incoming_doc_ids
                    elif self.supplier_delivery_method == 'road':
                        incoming_doc_types = invoice.company_id.road_sale_invoice_incoming_doc_ids
                    for in_doc_type in incoming_doc_types:
                        in_doc_vals = {
                            'name': in_doc_type.name,
                            'responsible': 'buyer',
                            'type_id': in_doc_type.id,
                            'lead_id': lead.id,
                            'sale_invoice_id': invoice.id,
                            'type': 'incoming',
                        }
                        documents.sudo().create(in_doc_vals)
                    if self.supplier_delivery_method == 'sea':
                        outgoing_doc_types = invoice.company_id.sea_sale_invoice_outgoing_doc_ids
                    elif self.supplier_delivery_method == 'road':
                        outgoing_doc_types = invoice.company_id.road_sale_invoice_outgoing_doc_ids
                    for out_doc_type in outgoing_doc_types:
                        out_doc_vals = {
                            'name': out_doc_type.name,
                            'responsible': 'buyer',
                            'type': 'outgoing',
                            'type_id': out_doc_type.id,
                            'lead_id': lead.id,
                            'sale_invoice_id': invoice.id,
                        }
                        documents.sudo().create(out_doc_vals)
                    for doc_type in self.doc_type_ids:
                        doc_vals = {
                            'name': doc_type.name,
                            'type_id': doc_type.id,
                            'type': 'outgoing',
                            'responsible': 'buyer',
                            'sale_invoice_id': invoice.id,
                            'lead_id': lead.id,
                        }
                        documents.create(doc_vals)

                invoice.invoice_date_due = False
                
                lead.sale_invoice_id = invoice.id
                lead.is_afrex_proforma_raised = True

            
            return {
                'res_id': invoice.id,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'context': {},
                'target': 'current'
            }