from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RoadInvoiceWizard(models.TransientModel):
    _name = 'asc.road.invoice'
    _description = 'Invoice for Shipment by Road Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id', string="Trade Folder")
    sale_order_id = fields.Many2one('sale.order', related='lead_id.sale_order_id', string="Offer")
    product_combination_id = fields.Many2one('asc.product.combination', string="Product", related='lead_id.product_combination_id')
    
    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method', string="Delivery Method", readonly=False)
    
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", readonly=True, related='purchase_id.container_type_id')
    container_num = fields.Char(string='Container No.', copy=False)
    seal_num = fields.Char(string='Seal No.', copy=False)
    marks_numbers = fields.Char("Marks and Numbers", compute='compute_marks_numbers', copy=False, readonly=False)
    booking_num = fields.Char(string="Booking or BL No.", readonly=False, copy=False)
    
    shipment_ref = fields.Integer(string="Shipment Number")
    invoice_ref = fields.Char("Afrex Invoice Number")
    sad_ref = fields.Char("SAD MRN")
    
    supplier_invoice_ref = fields.Char("Supplier Invoice Number")
    supplier_invoice_qty = fields.Float("Supplier Invoice Qty")
    
    loading_ref = fields.Char("Loading Reference No.")
    payload_qty = fields.Float("Loading Instruction Payload (MT)")
    loading_qty = fields.Float("Weighbridge Weight (Loading Point)")
    offloading_qty = fields.Float("Weighbridge Weight (Offloading Point)")
    
    driver_name = fields.Char("Driver Name", copy=False)
    driver_ref = fields.Char("Driver ID", copy=False)
    horse_reg_num = fields.Char(string="Horse Registration No.", copy=False)
    first_trailer_reg_num = fields.Char(string="Trailer 1 No.", copy=False)
    second_trailer_reg_num = fields.Char(string="Trailer 2 No.", copy=False)
    manifest_num = fields.Char(string="Manifest No.", copy=False)
    
    loading_date = fields.Date(string="Loading Date", copy=False)
    dispatch_date = fields.Date(string="Dispatch Date", copy=False)
    offloading_date = fields.Date(string="Delivery Date", copy=False)
    
    # can_confirm = fields.Boolean(compute='_compute_can_confirm')