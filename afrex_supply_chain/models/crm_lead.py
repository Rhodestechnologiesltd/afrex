# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Lead(models.Model):
    _inherit = 'crm.lead'
    
    name = fields.Char(required=False, readonly=True, default='- DRAFT -', copy=False)
    is_internal = fields.Boolean("Internal deal", related='partner_id.is_internal', copy=False)
    
    is_rfq_generated = fields.Boolean("QRs generated", copy=False)
    is_purchase_order_confirmed = fields.Boolean("Afrex PO Confirmed", copy=False)
    is_payment_request_generated = fields.Boolean("Payment Requests Generated", related='purchase_order_id.is_payment_request_generated', copy=False)
    is_purchase_order_invoiced = fields.Boolean("Supplier Commercial Invoice is recorded", related='purchase_order_id.is_invoiced', copy=False)
    is_invoice_generated = fields.Boolean("Afrex Invoice generated", copy=False)
    is_sale_order_generated = fields.Boolean("Afrex Offer Generated", copy=False)
    
    is_profit_estimate_approved = fields.Boolean("Profit Estimate Approved", copy=False)
    
    is_product_locked = fields.Boolean("Product Locked", copy=False)
    is_product_selected = fields.Boolean("Product is selected", copy=False)
    deal_status_logistics = fields.Selection([('active', "Active"),
                                              ('closed', "Closed")],
                                             string="Deal Status: Logistics", tracking=True, copy=False)
    deal_status_accounting = fields.Selection([('active', "Active"),
                                              ('closed', "Closed")],
                                             string="Deal Status: Accounting", tracking=True, copy=False)
    is_eazzy_filed = fields.Boolean(string="Eazzy Filed", copy=False)
    
    incoterm_implementation_year = fields.Char("Last Incoterm implentation", default=lambda self: self.env.company.incoterm_implementation_year, copy=False)
    
    shipment_window_start = fields.Date("Shipment Window Start", copy=False)
    shipment_window_end = fields.Date("Shipment Window End", copy=False)

    supplier_id = fields.Many2one('res.partner', related='purchase_order_id.partner_id', string="Supplier", copy=False)
    origin_country_id = fields.Many2one('res.country', string="Country of Origin", related='purchase_order_id.origin_country_id', store=True)
    
    sale_country_id = fields.Many2one('res.country', related='partner_id.country_id', string="Country of Delivery", store=True, copy=False)
    
    purchase_order_ids = fields.One2many('purchase.order', 'lead_id', string="Purchase Orders")
    purchase_order_count = fields.Integer(string="No. of Purchase Orders",
                                   compute='compute_purchase_order_count',
                                   default=0)

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", copy=False)
    purchase_order_date = fields.Datetime(related='purchase_order_id.date_approve')
    purchase_order_currency_id = fields.Many2one('res.currency', related='purchase_order_id.currency_id')
    purchase_order_terms_id = fields.Many2one('account.payment.term', related="purchase_order_id.payment_term_id", string="PO Payment Terms")
    purchase_order_incoterm_id = fields.Many2one('account.incoterms', related="purchase_order_id.incoterm_id", store=True, copy=False)
    purchase_order_incoterm_selection = fields.Selection(related="purchase_order_id.incoterm_selection")
    purchase_order_fob_amount = fields.Float("Afrex PO FOB", related="purchase_order_id.fob_amount")
    purchase_order_fob_unit = fields.Float("Afrex PO FOB Unit", related="purchase_order_id.fob_unit")
    purchase_order_fca_amount = fields.Float("Afrex PO FCA", related="purchase_order_id.fca_amount")
    purchase_order_fca_unit = fields.Float("Afrex PO FCA Unit", related="purchase_order_id.fca_unit")
    purchase_order_insurance_amount = fields.Float("Afrex PO Insurance", related="purchase_order_id.insurance_amount")
    purchase_order_freight_amount = fields.Float("Afrex PO Freight", related="purchase_order_id.freight_amount")
    purchase_order_cost_amount = fields.Float("Afrex PO Cost", related="purchase_order_id.cost_amount")
    purchase_order_cost_unit = fields.Float("Afrex PO Cost Unit", related="purchase_order_id.cost_unit")
    purchase_order_qty_delivered = fields.Float(string="MT Received", related="purchase_order_id.qty_delivered", tracking=True, digits="Prices per Unit")
    purchase_order_is_invoiced = fields.Boolean("Purchase Order Invoiced", related="purchase_order_id.is_invoiced", copy=False)
    purchase_order_state = fields.Selection(related='purchase_order_id.state', string="Purchase Order Status", copy=False)
    
    purchase_order_cif_amount = fields.Float("CIF Amount", compute="_compute_purchase_order_cif_amount", store=True, copy=False)

    road_transportation_unit = fields.Float(related='purchase_order_id.road_transportation_unit', readonly=False)
    road_transportation_amount = fields.Float(related='purchase_order_id.road_transportation_amount')
        
    logistics_service_unit = fields.Float(related='purchase_order_id.logistics_service_unit', readonly=False)
    logistics_service_amount = fields.Float(related='purchase_order_id.logistics_service_amount')
    
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", default='container', copy=False)
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", copy=False)
    container_stuffing = fields.Integer("Container Stuffing", copy=False)
    container_count = fields.Integer("Container Count", copy=False)
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", copy=False)
    trans_shipment = fields.Selection([('allowed', "Allowed"),
                                       ('not', "Not Allowed")],
                                      string="Trans Shipment", tracking=True, copy=False)
    partial_shipment = fields.Selection([('allowed', "Allowed"),
                                         ('not', "Not Allowed")],
                                        string="Partial Shipment", tracking=True, copy=False)
    
    supplier_proforma_num = fields.Char("Supplier PFI No.", related="purchase_order_id.partner_ref", copy=False)
    supplier_proforma_date = fields.Date("Supplier PFI Date", related="purchase_order_id.supplier_reference_doc_date", copy=False)
    supplier_proforma_currency_id = fields.Many2one('res.currency', string="Supplier PFI Currency")
    supplier_proforma_incoterm_id = fields.Many2one('account.incoterms', string="Supplier PFI Incoterms", copy=False)
    supplier_proforma_fob = fields.Float("Supplier PFI FOB", copy=False)
    supplier_proforma_insurance = fields.Float("Supplier PFI Insurance", copy=False)
    supplier_proforma_freight = fields.Float("Supplier PFI Freight", copy=False)
    supplier_proforma_terms_id = fields.Many2one('account.payment.term', string="Supplier Payment Terms", copy=False)
    
    supplier_invoice_ids = fields.One2many('account.move', 'lead_id', domain=[('move_type','=', 'in_invoice')], string="Supplier Invoices")
    supplier_invoice_list = fields.Text(string="Supplier Invoices", compute="_compute_supplier_invoice_list", store=True)
    
    # supplier_invoice_id = fields.Many2one('account.move', "Supplier Invoice")
    # supplier_invoice_ref = fields.Char(related='supplier_invoice_id.ref', string="Supplier Invoice Num", readonly=False)
    # supplier_invoice_date = fields.Date(related='supplier_invoice_id.invoice_date')
    # supplier_invoice_incoterm_id = fields.Many2one('account.incoterms', related='supplier_invoice_id.invoice_incoterm_id', readonly=False)
    # supplier_invoice_fob = fields.Float("Supplier Invoice FOB")
    # supplier_invoice_insurance = fields.Float("Supplier Invoice Insurance")
    # supplier_invoice_freight = fields.Float("Supplier Invoice Freight")
    
    is_switch = fields.Boolean(string="Subject to Switch", copy=False)
    switch_invoice_num = fields.Char("Switch Invoice No.", copy=False)
    switch_invoice_amount = fields.Float("Switch Invoice Amount", copy=False)
    
    supplier_delivery_method = fields.Selection([('sea', "Sea"),
                                                 ('road', "Road"),
                                                 ('air', "Air")], string="Means of Transport", default='sea', copy=False)
    
    loading_port_id = fields.Many2one('asc.port', "Port/Place of Loading", related="purchase_order_id.loading_port_id", readonly=False, copy=False)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge/Place of Delivery", ondelete='restrict', copy=False)
    loading_place = fields.Char("Place of Loading", copy=False)
    offloading_place = fields.Char("Place of Delivery", copy=False)
    
    vessel = fields.Char("Vessel Name", copy=False)
    voyage = fields.Char("Voyage", copy=False)
    route = fields.Char("Route", compute="compute_route", readonly=False, copy=False)
    seal_num = fields.Char(string="Seal No.", copy=False)

    vessel_voyage_lines = fields.Char(compute='_compute_vessel_voyage_lines', store=True)


    
    receipt_ids = fields.One2many('stock.picking', 'lead_id', string="Receipts")
    stock_move_ids = fields.One2many('stock.move', 'lead_id', domain=[('state','=', ['assigned','done'])], string="Stock Moves")

    container_list = fields.Text("Container List", compute="_compute_container_list", store=True, copy=False)
    seal_list = fields.Text("Seal List", compute="_compute_seal_list", store=True, copy=False)

    booking_num = fields.Char("Booking or BL No.", copy=False)
    booking_list = fields.Text("Booking or BL No.", compute="_compute_booking_list", store=True, copy=False)
    
    driver_name = fields.Char("Driver Name", copy=False)
    driver_num = fields.Char("Driver ID", copy=False)
    
    horse_reg_num = fields.Char(string="Horse Registration No.", copy=False)
    first_trailer_reg_num = fields.Char(string="Trailer 1 No.", copy=False)
    second_trailer_reg_num = fields.Char(string="Trailer 2 No.", copy=False)
    
    road_container_type = fields.Selection([('bag', "Bag"),
                                            ('tanker', "Tanker")], string="Container Type by Road", copy=False)

    bag_size = fields.Float("Bag Size", copy=False)
    bag_count = fields.Integer("Bag Count", copy=False)

    carrier_id = fields.Many2one('asc.shipping.line', string="Carrier / Shipping Line", ondelete='restrict', copy=False)
    forwarder_id = fields.Many2one('res.partner', string="Forwarder", copy=False)
    consignee_id = fields.Many2one('res.partner', string="Consignee", copy=False)
    notify_id = fields.Many2one('res.partner', string="Notify", copy=False)
    
    transporter_id = fields.Many2one('res.partner', related='purchase_order_id.transporter_id', string="Transporter", readonly=False)
    clearing_agent_id = fields.Many2one('res.partner', related='purchase_order_id.clearing_agent_id', string="Clearing Agent", copy=False)
    
    expected_shipment_date = fields.Date("Expected Shipment Date", copy=False)
    actual_shipment_date = fields.Date("Actual Shipment Date", copy=False)
    is_shipment_default = fields.Boolean("Shipment Default", copy=False)
    shipment_delay = fields.Float("Delay in Supplier Shipment", copy=False)
    
    expected_loading_date = fields.Date("Expected Loading Date", copy=False)
    actual_loading_date = fields.Date("Actual Loading Date", copy=False)
    
    loading_time = fields.Float("Loading Time", copy=False)
    offloading_time = fields.Float("Delivery Time", copy=False)
    
    expected_arrival_date = fields.Date("Expected Date of Arrival", copy=False)
    actual_arrival_date = fields.Date("Actual Date of Arrival", copy=False)
    
    expected_sob_date = fields.Date("Expected Shipped on Board Date", copy=False)
    sob_date = fields.Date("Shipped on Board Date", copy=False)
    
    is_shipment_docs = fields.Boolean("Shipment Docs", copy=False)
    shipment_docs_date = fields.Date("Date Shipment Docs received", copy=False)
    
    is_bl_released = fields.Boolean("BL Released", copy=False)
    bl_release_date = fields.Date("BL Release Date", copy=False)
    
    is_export_docs = fields.Boolean("Export Docs", copy=False)
    export_docs_date = fields.Date("Date Export Docs received", copy=False)
    
    is_import_docs = fields.Boolean("Import Docs", copy=False)
    import_docs_date = fields.Date("Date Import Docs received", copy=False)
    
    logistics_state = fields.Selection([('arrived',"Arrived"),
                                        ('awaiting_confirmation',"Awaiting Shipment Confirmation/Loading Instructions"),
                                        ('booked',"Booked"),
                                        ('booking_cancelled',"Booking Cancelled"),
                                        ('deal_cancelled',"Deal Cancelled"),
                                        ('delayed',"Delayed"),
                                        ('pending',"Pending"),
                                        ('sailing',"Sailing/In Transit"),
                                        ('planned',"Planned"),], string="Logistics Status", copy=False)
    
    is_afrex_proforma_raised = fields.Boolean(string="PFI Raised", copy=False)
    afrex_proforma_date = fields.Date(string="PFI Date", copy=False)
    is_afrex_commercial_raised = fields.Boolean(string="CI Raised", copy=False)
    afrex_commercial_date = fields.Date(string="CI Date", copy=False)
    
    sale_invoice_id = fields.Many2one('account.move', "Afrex Invoice", copy=False)
    sale_invoice_date = fields.Date(related='sale_invoice_id.invoice_date')
    sale_invoice_incoterm_id = fields.Many2one('account.incoterms', related="sale_invoice_id.invoice_incoterm_id", readonly=False)
    sale_invoice_fob = fields.Float("Afrex Invoice FOB")
    sale_invoice_insurance = fields.Float("Afrex Invoice Insurance")
    sale_invoice_freight = fields.Float("Afrex Invoice Freight")
    is_sale_invoice_incoterm_selection = fields.Selection(related="sale_invoice_id.incoterm_selection")
    sale_invoice_packing_list_date = fields.Date(related="sale_invoice_id.packing_list_date", string="Packing List Date")
    sale_invoice_origin_certificate_date = fields.Date(related="sale_invoice_id.origin_certificate_date", string="COO Date")
    sale_order_move_type = fields.Selection(related="sale_invoice_id.move_type")

    sale_invoice_state = fields.Selection(related="sale_invoice_id.state")
    
    gross_weight = fields.Float(string="Gross Weight", copy=False)
    net_weight = fields.Float(string="Net Weight (kg)", copy=False)
    package = fields.Float(string="Package", copy=False)
    order_qty = fields.Integer(string="Quantity", copy=False)
    order_value = fields.Float(string="Total Value", copy=False)
    
    sale_purchase_order_num = fields.Char("Buyer PO No.", related="sale_invoice_id.ref", readonly=False)
    sale_purchase_order_date = fields.Date("Buyer PO Date", copy=False)
    
    sale_order_id = fields.Many2one('sale.order', "Offer", copy=False)
    sale_order_date = fields.Datetime(related='sale_order_id.date_order', string="Offer Date")
    sale_order_incoterm_id = fields.Many2one('account.incoterms', related='sale_order_id.incoterm_id', string="Afrex Offer Incoterms", readonly=False, store=True, copy=False)
    sale_order_fob = fields.Float("Afrex Offer FOB")
    sale_order_insurance = fields.Float("Afrex Offer Insurance")
    sale_order_freight = fields.Float("Afrex Offer Freight")
    is_sale_order_incoterm_selection = fields.Selection(related="sale_order_id.incoterm_selection")
    sale_order_terms_id = fields.Many2one('account.payment.term', related='sale_order_id.payment_term_id', readonly=False)
    sale_order_state = fields.Selection(related="sale_order_id.state")

    tentative_sale_order_incoterm_id = fields.Many2one('account.incoterms', string="Afrex Offer Incoterms", readonly=False, copy=False)
    tentative_sale_order_terms_id = fields.Many2one('account.payment.term', readonly=False, copy=False)
    
    product_combination_id = fields.Many2one('asc.product.combination', string="Product", tracking=True)
    product_id = fields.Many2one('product.template', related='product_combination_id.product_id', string="Product")
    product_specification = fields.Char(related='product_combination_id.description', string="Specification")
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id', string="Packaging")
    packaging_weight = fields.Float(string="Packaging Weight (kg)")
    product_supplier_ids = fields.Many2many('res.partner', string="Suppliers", related="product_combination_id.supplier_ids")
    
    product_qty = fields.Float(string="MT Ordered", tracking=True, digits="Prices per Unit", copy=False, readonly=False)
    qty_delivered = fields.Float(string="MT Delivered", tracking=True, digits="Prices per Unit", copy=False)
    
    payment_request_ids = fields.One2many('asc.payment.request', 'lead_id', string="Payment Requests")
    
    outgoing_doc_ids = fields.One2many('asc.document', 'lead_id', domain=[('type','=', 'outgoing')], string="Documents to be provided")
    incoming_doc_ids = fields.One2many('asc.document', 'lead_id', domain=[('type','=', 'incoming')], string="Documents to receive")

    @api.depends('purchase_order_fob_amount', 'purchase_order_freight_amount', 'purchase_order_insurance_amount', 'afrex_freight_amount', 'insurance_premium_amount')
    def _compute_purchase_order_cif_amount(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                # Calculate CIF amount based on FOB, Freight, and Insurance
                if rec.purchase_order_incoterm_selection == 'cif':
                    # fob = rec.purchase_order_fob_amount
                    # freight = rec.purchase_order_freight_amount
                    # insurance = rec.purchase_order_insurance_amount
                    cif = rec.purchase_order_cost_amount
                elif rec.purchase_order_incoterm_selection == 'cfr':
                    # fob = rec.purchase_order_fob_amount
                    # freight = rec.purchase_order_freight_amount
                    cost = rec.purchase_order_cost_amount
                    insurance = rec.insurance_premium_amount
                    cif = cost + insurance
                elif rec.purchase_order_incoterm_selection == 'fob':
                    # fob = rec.purchase_order_fob_amount
                    cost = rec.purchase_order_cost_amount
                    freight = rec.afrex_freight_amount
                    insurance = rec.insurance_premium_amount
                    cif = cost + freight + insurance
                else:
                    fob, freight, insurance, cif = 0.0, 0.0, 0.0
                rec.purchase_order_cif_amount = cif

    def generate_payment_request_wizard(self):
        # if self.state not in ['purchase', 'done']:
        #     raise UserError("PO needs to be confirmed.")
        if not self.sale_order_terms_id:
            raise UserError("Please set the payments terms.")
        action = {
            'name': 'Generate Payment Request',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.generate.payment.request',
            'target': 'new',
            'context': {'default_purchase_order_id': self.id,
                        'default_currency_id': self.env.company.currency_id.id,}
        }
        return action

    def print_quotation(self):
            self.ensure_one()
            if not self.sale_order_id:
                raise UserError("No Quote / Offer generated.")
            return self.sale_order_id.print_quotation()

    def print_purchase_order(self):
            self.ensure_one()
            if not self.purchase_order_id:
                raise UserError("No PO generated.")
            return self.purchase_order_id.print_purchase_order()

    def print_shipping_instructions(self):
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError("No purchase order found for this lead.")
        return self.purchase_order_id.print_shipping_instructions()

    def print_proforma_invoice(self):
            self.ensure_one()
            if not self.sale_invoice_id:
                raise UserError("No Proforma invoice generated.")
            return self.sale_invoice_id.print_proforma_invoice()

    def print_commercial_invoice(self):
            self.ensure_one()
            if not self.sale_invoice_id:
                raise UserError("No commercial invoice generated.")
            return self.sale_invoice_id.print_commercial_invoice()

    def print_packing_list(self):
            self.ensure_one()
            if not self.sale_invoice_id:
                raise UserError("No invoice generated.")
            return self.sale_invoice_id.print_packing_list()

    def print_origin_certificate(self):
            self.ensure_one()
            if not self.sale_invoice_id:
                raise UserError("No invoice generated.")
            return self.sale_invoice_id.print_origin_certificate()

    @api.depends('vessel', 'voyage')
    def _compute_vessel_voyage_lines(self):
        for rec in self:
            vessels = rec.vessel.split(',') if rec.vessel else []
            voyages = rec.voyage.split(',') if rec.voyage else []
            combined = []
            for v, voy in zip(vessels, voyages):
                combined.append(f"{v.strip()} - {voy.strip()}")
            rec.vessel_voyage_lines = ','.join(combined)

    def compute_purchase_order_count(self):
        for record in self:
            record.purchase_order_count = self.env['purchase.order'].search_count([('lead_id', '=', record.id)])
            
    @api.onchange('product_qty', 'shipment_window_start', 'shipment_window_end')
    def check_rfq_sent(self):
        for rec in self:
            rfqs = rec.purchase_order_ids
            for rfq in rfqs:
                if rfq.is_sent:
                    raise ValidationError("RFQs have already been sent to suppliers!")
                   
    @api.onchange('sale_purchase_order_num')
    def update_invoice_ref(self):
        for rec in self:
            if rec.sale_invoice_id:
                rec.sale_invoice_id.ref = rec.sale_purchase_order_num
    
    @api.depends('loading_port_id','discharge_port_id','supplier_delivery_method')
    def compute_route(self):
        for rec in self:
            loading = rec.loading_port_id.name if rec.loading_port_id else "TBC"
            discharge = rec.discharge_port_id.name if rec.discharge_port_id else "TBC"
            rec.route = loading + " to " + discharge + " by " + rec.supplier_delivery_method
   
    @api.depends('stock_move_ids', 'stock_move_ids.container_num')
    def _compute_container_list(self):
        for rec in self:
            txt = ""
            txt_clean = ""
            containers = rec.stock_move_ids
            for cont in containers:
                if cont.container_num:
                    txt += cont.container_num + ", "
            if txt:
                txt_clean = txt.rstrip(', ')
            rec.container_list = txt_clean
            
    @api.depends('stock_move_ids', 'stock_move_ids.booking_num')
    def _compute_booking_list(self):
        for rec in self:
            txt = ""
            txt_clean = ""
            containers = rec.stock_move_ids
            for cont in containers:
                if cont.booking_num:
                    txt += cont.booking_num + ", "
            if txt:
                txt_clean = txt.rstrip(', ')
            rec.booking_list = txt_clean
            
    @api.depends('stock_move_ids', 'stock_move_ids.seal_num')
    def _compute_seal_list(self):
        for rec in self:
            txt = ""
            txt_clean = ""
            containers = rec.stock_move_ids
            for cont in containers:
                if cont.seal_num:
                    txt += cont.seal_num + ", "
            if txt:
                txt_clean = txt.rstrip(', ')
            rec.seal_list = txt_clean
            
    @api.depends('supplier_invoice_ids', 'supplier_invoice_ids.ref')
    def _compute_supplier_invoice_list(self):
        for rec in self:
            txt = ""
            for invoice in rec.supplier_invoice_ids:
                txt += invoice.ref + " "
            rec.supplier_invoice_list = txt
    
    def action_get_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_mode': 'tree,kanban,pivot,graph,form',
            'res_model': 'purchase.order',
            'domain': [('lead_id', '=', self.id)],
            'context': "{'create': False}"
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
    
    def action_open_invoice(self):
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
    
    def action_open_lead(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        record_url = base_url + "/web#id=" + str(self.id) + "&view_type=form&model=crm.lead&menu_id=358"
        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Trade Folder",
            'target': 'new',
            'url': record_url,

        }
        return client_action

    def action_open_lead_form(self):
        self.ensure_one()
        return {
            'res_id': self.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
        
    def product_selection_wizard(self):
        action = {
            'name': 'Select Product',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.product.selection',
            'target': 'new',
            'context': {'default_lead_id': self.id,
                        'default_product_qty': self.product_qty,}
        }
        return action
    
    def generate_purchase_order_wizard(self):
        self.ensure_one()
        if not self.product_combination_id:
            raise UserError("No product selected.")
        if not self.is_product_locked:
            raise UserError("Product must be locked to continue.")
        action = {
            'name': 'Generate RFQs',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.generate.purchase.order',
            'target': 'new',
            'context': {'default_lead_id': self.id}
        }
        return action
    
    def lock_product_selection(self):
        for rec in self:
            if rec.product_combination_id:
                rec.is_product_locked = True
            else:
                raise ValidationError("No product selected.")
    
    def unlock_product_selection(self):
        for rec in self:
            if rec.is_rfq_generated or rec.purchase_order_ids:
                raise UserError("Quote Requests have already been generated. Cannot change product.")
            if rec.purchase_order_id:
                raise UserError("A Quote Request or Purchase Order has already been set. Cannot change product.")
            else:
                rec.is_product_locked = False
    
    def generate_purchase_order(self):
        for rec in self:
            if rec.is_rfq_generated:
                raise UserError("RFQs for this product have already been generated.")
            else:
                if rec.product_supplier_ids:
                    suppliers = rec.product_supplier_ids
                    for supplier in suppliers:
                        origin = rec.name
                        order_vals = {
                            'partner_id': supplier.id,
                            'lead_id': rec.id,
                            'product_combination_id': rec.product_combination_id.id,
                            'origin': origin,
                            'breakbulk_container': rec.breakbulk_container,
                            'container_type_id': rec.container_type_id,
                            'container_count': rec.container_count,
                            'container_stuffing': rec.container_stuffing,
                            'is_palletised': rec.is_palletised,
                            'qty_total': rec.product_qty,
                        }
                        order = rec.env['purchase.order'].sudo().create(order_vals)
                        line_vals = {
                            'name': rec.product_combination_id.name,
                            'product_combination_id': rec.product_combination_id.id,
                            'product_id': rec.product_combination_id.product_id.product_variant_id.id,
                            'product_qty': rec.product_qty,
                            'order_id': order.id
                        }
                        order_line = rec.env['purchase.order.line'].sudo().create(line_vals)
                else:
                    raise ValidationError("No supplier set for %s" % rec.product_combination_id.name)
                rec.is_rfq_generated = True

    def generate_offer(self):
        self.ensure_one()
        lead = self
        if not self.purchase_order_id:
            raise UserError("No Quote Request or Purchase Order selected.")
        return self.purchase_order_id.generate_sale_order_wizard()
        # purchase_order = self.purchase_order_id
        # if not purchase_order.origin_country_id:
        #     raise UserError("Please set the Country of Origin.")
        # if purchase_order.supplier_delivery_method == 'sea' and purchase_order.breakbulk_container == 'container':
        #     if not purchase_order.container_type_id:
        #         raise UserError("Please set the container size.")
        # if self.sale_order_id:
        #     sale_order = self.sale_order_id
        #     if sale_order.state == 'sale':
        #         raise UserError("An offer has already been confirmed for this deal. Refer to %s" % str(self.sale_order_id.name))
        #     elif sale_order.state == 'sent':
        #         raise UserError("An offer has already been sent to the buyer for this deal. Refer to %s" % str(self.sale_order_id.name))
        # self.sudo().compute_sales_price()
        # self.env.cr.commit()
        # insurance = purchase_order.insurance_amount
        # freight = purchase_order.freight_amount
        # fca = purchase_order.fca_amount
        # road_transportation = purchase_order.road_transportation_amount
        # logistics_service = purchase_order.logistics_service_amount
        # interest = lead.credit_cost_amount
        # procurement = lead.procurement_fee_amount
        # sales_price = lead.sales_price
        # incoterm = lead.sale_order_incoterm_id or lead.tentative_sale_order_incoterm_id
        # net_weight = lead.product_qty * 1000  # Assuming 1 MT = 1000 kg
        # action = {
        #     'name': 'Generate Offer',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'asc.generate.sale.order',
        #     'target': 'new',
        #     'context': {'default_purchase_order_id': purchase_order.id,
        #                 'default_loading_port_id': self.loading_port_id.id,
        #                 'default_currency_id': purchase_order.currency_id.id,
        #                 'default_cost_amount': sales_price,
        #                 'default_freight_amount': freight,
        #                 'default_insurance_amount': insurance,
        #                 'default_interest_amount': interest,
        #                 'default_procurement_documentation_amount': procurement,
        #                 'default_fca_amount': fca,
        #                 'default_road_transportation_amount': road_transportation,
        #                 'default_logistics_service_amount': logistics_service,
        #                 'default_net_weight': net_weight,
        #                 'default_payment_term_id': lead.sale_order_terms_id.id or lead.tentative_sale_order_terms_id.id,
        #                 'default_incoterm_id': incoterm.id,}
        # }
        # return action
                    
    def generate_proforma_invoice(self):
        sale = self.sale_order_id
        if sale:
            action = {
                'name': 'Generate Proforma Invoice',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asc.generate.proforma',
                'target': 'new',
                'context': {'default_lead_id': self.id,
                            'default_sale_order_id': sale.id,
                            'default_incoterm_id': sale.incoterm_id.id,
                            'default_fob_amount': sale.fob_amount,
                            'default_freight_amount': sale.freight_amount,
                            'default_insurance_amount': sale.insurance_amount,
                            'default_interest_amount': sale.interest_amount,
                            'default_procurement_documentation_amount': sale.procurement_documentation_amount,
                            'default_cost_amount': sale.cost_amount,}
            }
            return action
        else:
            raise UserError("No confirmed offer found.")
        
    def confirm_invoice(self):
        invoice = self.sale_invoice_id
        if invoice:
            # raise UserError("Calculation in this function is wrong")
            for line in invoice.invoice_line_ids:
                line.quantity = self.purchase_order_qty_delivered
            invoice.fob_amount = invoice.fob_unit * self.purchase_order_qty_delivered                
            invoice.freight_amount = invoice.freight_unit * self.purchase_order_qty_delivered
            invoice.cost_amount = invoice.cost_unit * self.purchase_order_qty_delivered            
            # invoice.action_post()
            # self.is_afrex_commercial_raised = True
            action = {
                'name': 'Commercial Invoice',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asc.confirm.invoice',
                'target': 'new',
                'context': {'default_sale_invoice_id': invoice.id}
            }
            return action
        else:
            raise UserError("No proforma invoice found.")
    
    def generate_commercial_invoice(self):
        generated_invoices = self.env['account.move']

        order = self.sale_order_id
        downpayment_wizard = self.env['sale.advance.payment.inv'].create({
            'sale_order_ids': order.ids,
            'advance_payment_method': 'delivered',
        })
        generated_invoices |= downpayment_wizard._create_invoices(order)
        
        for invoice in order.invoice_ids:
            invoice.ref = self.sale_purchase_order_num
            self.sale_invoice_id = invoice.id
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
            
    def receive_products(self):
        self.ensure_one()
        if not self.purchase_order_id:
            raise UserError("No purchase order found for this lead.")
        if self.purchase_order_id.is_invoiced:
            raise UserError("All commercial invoices for this purchase have been processed. No more receipts can be done.")
        return self.purchase_order_id.action_view_picking()
        

    def action_set_won_rainbowman(self):
        super(Lead, self).action_set_won_rainbowman()
        supplier = self.supplier_id
        if not supplier:
            raise UserError("No supplier set.")
        if not supplier.sequence_id:
            raise UserError("No reference set for supplier.")
        seq_code = supplier.sequence_id.code
        sequence = self.env['ir.sequence'].next_by_code(seq_code)
        self.name = "[" + str(sequence) + "]"
        return
    
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('asc.lead.seq')
        vals['name'] = sequence
        lead = super(Lead, self).create(vals)
        return lead
