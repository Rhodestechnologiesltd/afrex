# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    incoterm_implementation_date = fields.Date("Last Incoterm implentation")
    incoterm_implementation_year = fields.Char("Last Incoterm implentation", compute="_compute_incoterm_implementation_year", store=True, default="2020")
    header_text = fields.Text("Text in header")
    seal = fields.Binary("Company Seal")
        
    credit_cost_rate = fields.Float(string="Credit Cost Rate", default=0.0425, digits="Prices per Unit")
    credit_insurance_rate = fields.Float(string="Credit Insurance Rate", default=0.006, digits="Prices per Unit")
    
    minimum_gross_profit = fields.Float(string="Minimum Gross Profit", default=0.03, digits="Percentage Analytic")
    minimum_markup = fields.Float(string="Minimum Markup", default=0.03, digits="Percentage Analytic")
    
    logistics_service_unit = fields.Float(string="Logistics Service per MT")
    
    payment_request_approver_ids = fields.Many2many('res.users', 'rel_company_payment_request_approver', string="Can approve Payment Requests")
    profit_estimate_approver_ids = fields.Many2many('res.users', 'rel_company_profit_estimate_approver', string="Can approve Profit Estimates")
    
    sea_purchase_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_incoming_doc_sea', string="Default Documents to provided by Supplier for Maritime Shipment")
    sea_purchase_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_outgoing_doc_sea', string="Default Documents to be submitted by Afrex to Supplier for Maritime Shipment")
    
    road_purchase_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_incoming_doc_road', string="Default Documents to provided by Supplier for Road Transportation")
    road_purchase_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_outgoing_doc_road', string="Default Documents to be submitted by Afrex to Supplier for Road Transportation")
    
    sea_sale_invoice_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_incoming_doc_sea', string="Default Documents to be provided by Buyer for Maritime Shipment")
    sea_sale_invoice_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_outgoing_doc_sea', string="Default Documents to be submitted by Afrex to Buyer for Maritime Shipment")
    
    road_sale_invoice_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_incoming_doc_road', string="Default Documents to be provided by Buyer for Maritime Shipment for Road Transportation")
    road_sale_invoice_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_outgoing_doc_road', string="Default Documents to be submitted by Afrex to Buyer for Maritime Shipment for Road Transportation")
    
    # display_partner_child = fields.Boolean("Display Contact Persons", help="If enabled, the contact persons of partners will be displayed in the PDFs as defined in the Contacts database. To be used after cleaning up the address text of all contacts.")
    # x_display_partner_child = fields.Boolean("Display Contact Persons", help="If enabled, the contact persons of partners will be displayed in the PDFs as defined in the Contacts database. To be used after cleaning up the address text of all contacts.")

    @api.depends('incoterm_implementation_date')
    def _compute_incoterm_implementation_year(self):
        if self.incoterm_implementation_date:
            self.incoterm_implementation_year = str(self.incoterm_implementation_date.year)