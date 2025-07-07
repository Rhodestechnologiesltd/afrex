from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError


class GeneratePurchaseOrderWizard(models.TransientModel):
    _name = 'asc.generate.purchase.order'
    _description = 'Generate Purchase Order Wizard'

    lead_id = fields.Many2one('crm.lead')
    is_switch = fields.Boolean(string="Subject to Switch", related='lead_id.is_switch', readonly=False)

    product_combination_id = fields.Many2one('asc.product.combination', string="Product", related='lead_id.product_combination_id', readonly=False)
    product_id = fields.Many2one('product.template', related='product_combination_id.product_id', string="Product")
    product_specification = fields.Char(related='product_combination_id.description', string="Specification")
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id', string="Packaging")

    product_qty = fields.Float(string="MT Ordered", related='lead_id.product_qty', readonly=False)
    
    supplier_delivery_method = fields.Selection([('sea', "Sea"),
                                                 ('road', "Road"),
                                                 ('air', "Air")], related='lead_id.supplier_delivery_method', readonly=False)

    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related='lead_id.discharge_port_id', readonly=False)
    
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.ref('base.USD'), required=True)
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterms", default=lambda self: self.env.ref('account.incoterm_CIF'), required=True)
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')],)
    
    shipment_window_start = fields.Date("Shipment Window Start", related='lead_id.shipment_window_start', readonly=False)
    shipment_window_end = fields.Date("Shipment Window End", related='lead_id.shipment_window_end', readonly=False)
    
    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"),],
                                           string="Breakbulk or Container", default='container', related='lead_id.breakbulk_container', readonly=False)
    container_type_id = fields.Many2one('asc.container.type', string="Container Size", related='lead_id.container_type_id', readonly=False)
    container_stuffing = fields.Integer("Container Stuffing", related='lead_id.container_stuffing', readonly=False)
    container_count = fields.Integer("Container Count", related='lead_id.container_count', readonly=False)
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"),],
                                     string="Palletised or Loose", related='lead_id.is_palletised', readonly=False)
    
    trans_shipment = fields.Selection([('allowed', "Allowed"),
                                       ('not', "Not Allowed")],
                                      string="Trans Shipment", default='allowed')
    partial_shipment = fields.Selection([('allowed', "Allowed"),
                                         ('not', "Not Allowed")],
                                        string="Partial Shipment", default='not')
    
    transporter_id = fields.Many2one('res.partner', string="Transporter", copy=False)
    
    
    @api.onchange('incoterm_id')
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
    
    def generate_purchase_order(self):
        lead = self.lead_id
        if lead.is_rfq_generated:
            raise UserError("RFQs for this product have already been generated.")
        elif not lead.product_supplier_ids:
            raise ValidationError("No supplier set for %s" % lead.product_combination_id.name)
        else:
            suppliers = lead.product_supplier_ids
            if self.breakbulk_container == 'breakbulk':
                self.container_type_id = False
                self.container_count = 0
                self.container_stuffing = 0
                self.is_palletised = None
            if lead.is_internal:
                first_consignee = self.env.ref('afrex_supply_chain.asc_trademaw')
                second_consignee = self.env.ref('base.main_partner')
            else:
                first_consignee = self.env.ref('base.main_partner')
                second_consignee = self.env.ref('base.main_partner')
            for supplier in suppliers:
                origin = lead.name
                order_vals = {
                    'partner_id': supplier.id,
                    'lead_id': lead.id,
                    'first_consignee_id': first_consignee.id,
                    'second_consignee_id': second_consignee.id,
                    'product_combination_id': lead.product_combination_id.id,
                    'origin': origin,
                    'discharge_port_id': self.discharge_port_id.id,
                    'origin_country_id': supplier.country_id.id,
                    'currency_id': self.currency_id.id,
                    'incoterm_id': self.incoterm_id.id,
                    'shipment_window_start': self.shipment_window_start,
                    'shipment_window_end': self.shipment_window_end,
                    'breakbulk_container': self.breakbulk_container,
                    'container_type_id': self.container_type_id.id,
                    'container_count': self.container_count,
                    'container_stuffing': self.container_stuffing,
                    'is_palletised': self.is_palletised,
                    'qty_total': self.product_qty,
                    'trans_shipment': self.trans_shipment,
                    'partial_shipment': self.partial_shipment,
                    'transporter_id': self.transporter_id.id,
                }
                order = lead.env['purchase.order'].sudo().create(order_vals)
                order._compute_incoterm_selection()
                line_vals = {
                    'name': lead.product_combination_id.name,
                    'product_combination_id': lead.product_combination_id.id,
                    'product_id': lead.product_combination_id.product_id.product_variant_id.id,
                    'product_qty': self.product_qty,
                    'taxes_id': False,
                    'price_unit': 0,
                    'order_id': order.id
                }
                order_line = lead.env['purchase.order.line'].sudo().create(line_vals)
                if self.supplier_delivery_method == 'sea':
                    incoming_doc_types = order.company_id.sea_purchase_incoming_doc_ids
                elif self.supplier_delivery_method == 'road':
                    incoming_doc_types = order.company_id.road_purchase_incoming_doc_ids
                for in_doc_type in incoming_doc_types:
                    in_doc_vals = {
                        'name': in_doc_type.name,
                        'responsible': 'supplier',
                        'type_id': in_doc_type.id,
                        'lead_id': lead.id,
                        'purchase_order_id': order.id,
                        'type': 'incoming',
                    }
                    documents = lead.env['asc.document'].sudo().create(in_doc_vals)
                if self.supplier_delivery_method == 'sea':
                    outgoing_doc_types = order.company_id.sea_purchase_outgoing_doc_ids
                elif self.supplier_delivery_method == 'road':
                    outgoing_doc_types = order.company_id.road_purchase_outgoing_doc_ids
                for out_doc_type in outgoing_doc_types:
                    out_doc_vals = {
                        'name': out_doc_type.name,
                        'responsible': 'supplier',
                        'type_id': out_doc_type.id,
                        'lead_id': lead.id,
                        'purchase_order_id': order.id,
                        'type': 'outgoing',
                    }
                    documents = lead.env['asc.document'].sudo().create(out_doc_vals)
            lead.is_rfq_generated = True
            
            
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quote Requests and Purchase Orders',
                'view_mode': 'tree,kanban,pivot,graph,form',
                'res_model': 'purchase.order',
                'domain': [('lead_id', '=', lead.id)],
                'context': "{'create': False}"
            }