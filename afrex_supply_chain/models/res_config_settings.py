# -*- coding: utf-8 -*-
# Part of Rhodes Technologies Ltd.

from odoo import models, fields, api


class ASCSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    credit_cost_rate = fields.Float(string="Credit Cost Rate", related='company_id.credit_cost_rate', readonly=False, digits="Prices per Unit")
    credit_insurance_rate = fields.Float(string="Credit Insurance Rate", related='company_id.credit_insurance_rate', readonly=False, digits="Prices per Unit")
    
    minimum_gross_profit = fields.Float(string="Minimum Gross Profit", related='company_id.minimum_gross_profit', readonly=False, digits="Percentage Analytic")
    minimum_markup = fields.Float(string="Minimum Markup", related='company_id.minimum_markup', readonly=False, digits="Percentage Analytic")
    
    logistics_service_unit = fields.Float(string="Logistics Service per MT", related='company_id.logistics_service_unit', readonly=False)
    
    payment_request_approver_ids = fields.Many2many('res.users', 'rel_company_payment_request_approver', string="Can approve Payment Requests", related='company_id.payment_request_approver_ids', readonly=False)
    profit_estimate_approver_ids = fields.Many2many('res.users', 'rel_company_profit_estimate_approver', string="Can approve Profit Estimates", related='company_id.profit_estimate_approver_ids', readonly=False)
    
    sea_purchase_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_incoming_doc_sea', string="Default Documents to provided by Supplier for Maritime Shipment", related='company_id.sea_purchase_incoming_doc_ids', readonly=False)
    sea_purchase_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_outgoing_doc_sea', string="Default Documents to be submitted by Afrex to Supplier for Maritime Shipment", related='company_id.sea_purchase_outgoing_doc_ids', readonly=False)
    
    sea_sale_invoice_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_incoming_doc_sea', string="Default Documents to be provided by Buyer for Maritime Shipment", related='company_id.sea_sale_invoice_incoming_doc_ids', readonly=False)
    sea_sale_invoice_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_outgoing_doc_sea', string="Default Documents to be submitted by Afrex to Buyer for Maritime Shipment", related='company_id.sea_sale_invoice_outgoing_doc_ids', readonly=False)
    
    road_purchase_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_incoming_doc_road', string="Default Documents to provided by Supplier for Road Transportation", related='company_id.road_purchase_incoming_doc_ids', readonly=False)
    road_purchase_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_purchase_outgoing_doc_road', string="Default Documents to be submitted by Afrex to Supplier for Road Transportation", related='company_id.road_purchase_outgoing_doc_ids', readonly=False)
    
    road_sale_invoice_incoming_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_incoming_doc_road', string="Default Documents to be provided by Buyer for Road Transportation", related='company_id.road_sale_invoice_incoming_doc_ids', readonly=False)
    road_sale_invoice_outgoing_doc_ids = fields.Many2many('asc.document.type', 'rel_company_sale_invoice_outgoing_doc_road', string="Default Documents to be submitted by Afrex to Buyer for Road Transportation", related='company_id.road_sale_invoice_outgoing_doc_ids', readonly=False)
    
    display_partner_child = fields.Boolean("Display Contact Persons", related='company_id.display_partner_child', help="If enabled, the contact persons of partners will be displayed in the PDFs as defined in the Contacts database. To be used after cleaning up the address text of all contacts.")
    # x_display_partner_child = fields.Boolean("Display Contact Persons", related='company_id.x_display_partner_child', help="If enabled, the contact persons of partners will be displayed in the PDFs as defined in the Contacts database. To be used after cleaning up the address text of all contacts.")