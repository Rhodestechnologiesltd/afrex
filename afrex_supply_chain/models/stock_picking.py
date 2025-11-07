# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    product_combination_id = fields.Many2one('asc.product.combination', string="Product", related='purchase_id.product_combination_id')
    lead_id = fields.Many2one('crm.lead', related='purchase_id.lead_id')
    sale_invoice_id = fields.Many2one('account.move', related='lead_id.sale_invoice_id')
    
    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method', string="Delivery Method", readonly=False)
    
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", readonly=True, related='purchase_id.container_type_id')
    container_num = fields.Char(string='Container No.', copy=False)
    seal_num = fields.Char(string='Seal No.', copy=False)
    marks_numbers = fields.Char("Marks and Numbers", compute='compute_marks_numbers', copy=False, readonly=False)
    booking_num = fields.Char(string="Booking or BL No.", related='lead_id.booking_num', readonly=False, copy=False)
    
    driver_name = fields.Char("Driver Name", copy=False)
    driver_num = fields.Char("Driver ID", copy=False)
    horse_reg_num = fields.Char(string="Horse Registration No.", copy=False)
    first_trailer_reg_num = fields.Char(string="Trailer 1 No.", copy=False)
    second_trailer_reg_num = fields.Char(string="Trailer 2 No.", copy=False)
    manifest_num = fields.Char(string="Manifest No.", copy=False)
    loading_date = fields.Date(string="Loading Date", copy=False)
    dispatch_date = fields.Date(string="Dispatch Date", copy=False)
    offloading_date = fields.Date(string="Delivery Date", copy=False)
    
    transporter_id = fields.Many2one('res.partner', related='purchase_id.transporter_id', string="Transporter", readonly=False)
    clearing_agent_id = fields.Many2one('res.partner', related='purchase_id.clearing_agent_id', string="Clearing Agent", readonly=False)
    
    carrier_id = fields.Many2one('asc.shipping.line', related='lead_id.carrier_id', readonly=False)
    forwarder_id = fields.Many2one('res.partner', related='lead_id.forwarder_id', readonly=False)
    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    route = fields.Char("Route", related="lead_id.route", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date", readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)

    done_qty_rec = fields.Float(
        string='Received Quantity',
        compute='_compute_rec_qty',
        store=True
    )

    # @api.depends('move_line_ids.qty_done')
    def _compute_rec_qty(self):
        for picking in self:
            picking.done_qty_rec = sum(picking.move_line_ids.mapped('qty_done'))
    @api.depends('product_combination_id')
    def compute_marks_numbers(self):
        for rec in self:
            if rec.product_combination_id:
                rec.marks_numbers = rec.product_combination_id.name
            else:
                rec.marks_numbers = False


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    lead_id = fields.Many2one('crm.lead', related='picking_id.lead_id')
    sale_invoice_id = fields.Many2one('account.move', related='picking_id.sale_invoice_id')
    
    container_type_id = fields.Many2one('asc.container.type', related='picking_id.container_type_id')
    container_num = fields.Char(related='picking_id.container_num')
    seal_num = fields.Char(related='picking_id.seal_num')
    marks_numbers = fields.Char(related='picking_id.marks_numbers')
    booking_num = fields.Char(related='picking_id.booking_num')
    
    driver_name = fields.Char(related='picking_id.driver_name')
    driver_num = fields.Char(related='picking_id.driver_num')
    horse_reg_num = fields.Char(related='picking_id.horse_reg_num')
    first_trailer_reg_num = fields.Char(related='picking_id.first_trailer_reg_num')
    second_trailer_reg_num = fields.Char(related='picking_id.second_trailer_reg_num')
    manifest_num = fields.Char(related='picking_id.manifest_num')
    loading_date = fields.Date(related='picking_id.loading_date')
    dispatch_date = fields.Date(related='picking_id.dispatch_date')
    offloading_date = fields.Date(related='picking_id.offloading_date')
    # rec_qty = fields.Float(related='move_line_ids.quantity')


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    lead_id = fields.Many2one('crm.lead', related='picking_id.lead_id')
    sale_invoice_id = fields.Many2one('account.move', related='picking_id.sale_invoice_id')
    
    container_type_id = fields.Many2one('asc.container.type', related='picking_id.container_type_id')
    container_num = fields.Char(related='picking_id.container_num')
    seal_num = fields.Char(related='picking_id.seal_num')
    marks_numbers = fields.Char(related='picking_id.marks_numbers')
    booking_num = fields.Char(related='picking_id.booking_num')
    
    driver_name = fields.Char(related='picking_id.driver_name')
    driver_num = fields.Char(related='picking_id.driver_num')
    horse_reg_num = fields.Char(related='picking_id.horse_reg_num')
    first_trailer_reg_num = fields.Char(related='picking_id.first_trailer_reg_num')
    second_trailer_reg_num = fields.Char(related='picking_id.second_trailer_reg_num')
    manifest_num = fields.Char(related='picking_id.manifest_num')
    loading_date = fields.Date(related='picking_id.loading_date')
    dispatch_date = fields.Date(related='picking_id.dispatch_date')
    offloading_date = fields.Date(related='picking_id.offloading_date')
