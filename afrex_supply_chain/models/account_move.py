# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from textwrap import shorten
from odoo.tools import format_date


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection_add=[('draft', 'Proforma'),
                                            ('posted', 'Commercial')])

    lead_id = fields.Many2one('crm.lead', string="Trade Folder")
    purchase_order_id = fields.Many2one('purchase.order', related='lead_id.purchase_order_id')
    supplier_id = fields.Many2one('res.partner', related='purchase_order_id.partner_id', string="Supplier")
    consignee_id = fields.Many2one('res.partner', string="Consignee", related="lead_id.consignee_id")

    is_internal = fields.Boolean("Internal deal", related='lead_id.is_internal')

    product_combination_id = fields.Many2one('asc.product.combination', related="lead_id.product_combination_id")
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')

    is_payment_due_on_weekend = fields.Boolean(string="Is Weekend", compute="_compute_is_payment_due_on_weekend")
    due_date_note = fields.Char("Due Date Notes")
    reversal_reason = fields.Char("Reason for Reversal")

    payment_due_date = fields.Date("Payment Due Date")
    is_date_due_indicative = fields.Boolean("Due Date is indicative")
    due_date_text = fields.Text("Due Date Text", default="Indicative, final payment due date will be confirmed.")

    tariff_code = fields.Char(string="Tariff Code")

    incoterm_implementation_year = fields.Char("Last Incoterm implentation",
                                               related='lead_id.incoterm_implementation_year')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")

    supplier_delivery_method = fields.Selection(related='lead_id.supplier_delivery_method')

    loading_port_id = fields.Many2one('asc.port', "Port of Loading", related="lead_id.loading_port_id", readonly=False,
                                      store=True)
    discharge_port_id = fields.Many2one('asc.port', "Port of Discharge", related="lead_id.discharge_port_id")

    sale_country_id = fields.Many2one('res.country', related='lead_id.sale_country_id', string="Country of Delivery",
                                      store=True, readonly=False)

    shipment_window_start = fields.Date("Shipment Window Start", related='lead_id.shipment_window_start', readonly=False)
    shipment_window_end = fields.Date("Shipment Window End", related='lead_id.shipment_window_end', readonly=False)

    breakbulk_container = fields.Selection([('breakbulk', "Breakbulk"),
                                            ('container', "Container"), ],
                                           string="Breakbulk or Container", default='container', readonly=True,
                                           related='sale_order_id.breakbulk_container')

    container_type_id = fields.Many2one('asc.container.type', string="Container Size", readonly=True,
                                        related='sale_order_id.container_type_id')
    container_stuffing = fields.Integer("Container Stuffing", readonly=True, related='sale_order_id.container_stuffing')
    container_count = fields.Integer("Container Count", readonly=True, related='sale_order_id.container_count')
    is_palletised = fields.Selection([('Palletised', "Palletised"),
                                      ('Loose', "Loose"), ],
                                     string="Palletised or Loose", readonly=True, related='sale_order_id.is_palletised')

    qty_total = fields.Float("MT Ordered", readonly=True, related='sale_order_id.qty_total', digits="Prices per Unit")
    qty_delivered = fields.Float(string="MT Delivered", related="lead_id.purchase_order_qty_delivered", tracking=True,
                                 digits="Prices per Unit")

    origin_country_id = fields.Many2one('res.country', string="Origin", related='sale_order_id.origin_country_id')

    fob_unit = fields.Float("FOB/MT", compute='_compute_fob_unit', store=True, digits="Prices per Unit", tracking=True)
    freight_unit = fields.Float("Freight/MT", compute='_compute_freight_unit', store=True, digits="Prices per Unit",
                                tracking=True)
    cost_unit = fields.Float("Cost/MT", compute='_compute_cost_unit', store=True, digits="Prices per Unit",
                             tracking=True)

    fob_amount = fields.Float("FOB", readonly=False, tracking=True)
    freight_amount = fields.Float("Freight", readonly=False, tracking=True)
    cost_amount = fields.Float("Cost", readonly=False, tracking=True)

    insurance_amount = fields.Float("Insurance", readonly=False, tracking=True)

    interest_amount = fields.Float("Interest", readonly=False, tracking=True)
    procurement_documentation_amount = fields.Float("Procurement & Documentation", readonly=False, tracking=True)

    fca_amount = fields.Float("FCA", tracking=True)
    road_transportation_amount = fields.Float(string="Road Transportation and Clearance", tracking=True)
    logistics_service_amount = fields.Float(string="Logistics Service fee", tracking=True)

    fca_unit = fields.Float("FCA/MT", compute='_compute_fca_unit', digits="Prices per Unit", tracking=True)
    road_transportation_unit = fields.Float(string="Road Transportation and Clearance per MT",
                                            compute='_compute_road_transportation_unit', digits="Prices per Unit",
                                            tracking=True)
    logistics_service_unit = fields.Float(string="Logistics Service fee per MT",
                                          compute='_compute_logistics_service_unit', digits="Prices per Unit",
                                          tracking=True)

    show_transportation = fields.Boolean("Display Transportation", help="Show transportation costs in the quotation")
    show_breakdown = fields.Boolean("Display Breakdown", help="Show breakdown of costs in the quotation")

    sale_order_id = fields.Many2one('sale.order')

    logistics_state = fields.Selection(related='lead_id.logistics_state')

    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    vessel_voyage_lines = fields.Char(
        related='lead_id.vessel_voyage_lines',
        string='Vessel Voyage Lines',
        store=True,
        readonly=False,
    )

    route = fields.Char("Route", related="lead_id.route", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date",
                                        readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)
    gross_weight = fields.Float(string="Gross Weight (kg)", related="lead_id.gross_weight", readonly=False)
    net_weight = fields.Float(string="Net Weight (kg)", related="lead_id.net_weight", readonly=False)
    stock_move_ids = fields.One2many('stock.move', 'sale_invoice_id', domain=[('state', '=', ['assigned', 'done'])],
                                     string="Stock Moves")
    stock_picking_ids = fields.One2many('stock.picking', 'sale_invoice_id', string='Stock Pickings')
    container_list = fields.Text(related="lead_id.container_list")
    seal_list = fields.Text(related="lead_id.seal_list")

    outgoing_doc_ids = fields.One2many('asc.document', 'sale_invoice_id', domain=[('type', '=', 'outgoing')],
                                       string="Documents to be provided")
    incoming_doc_ids = fields.One2many('asc.document', 'sale_invoice_id', domain=[('type', '=', 'incoming')],
                                       string="Documents to receive")

    check_docs = fields.Boolean("Check for completeness of Shipping Documents")

    marks_numbers = fields.Char("Marks and Numbers", compute='_compute_marks_numbers', store=True)
    packing_list_date = fields.Date("Packing List Date")
    origin_certificate_date = fields.Date("Certificate of Origin Date")

    @api.onchange('payment_due_date')
    def _set_invoice_date_due(self):
        for rec in self:
            if rec.payment_due_date:
                rec.invoice_date_due = rec.payment_due_date

    @api.depends('invoice_incoterm_id')
    def _compute_incoterm_selection(self):
        for rec in self:
            incoterm = rec.invoice_incoterm_id
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
            if rec.invoice_incoterm_id == self.env.ref('account.incoterm_CFR'):
                if rec.insurance_amount > 0:
                    raise UserError("Insurance amount should be 0 for a CFR deal.")

    @api.onchange('cost_unit')
    def set_product_cost(self):
        for line in self.invoice_line_ids:
            line.price_unit = self.cost_unit

    @api.onchange('qty_total')
    def set_product_qty(self):
        for line in self.invoice_line_ids:
            line.quantity = self.qty_total

    @api.depends('fob_amount', 'qty_total')
    def _compute_fob_unit(self):
        for rec in self:
            try:
                rec.fob_unit = rec.fob_amount / rec.qty_total
            except ZeroDivisionError:
                rec.fob_unit = 0

    @api.depends('freight_amount', 'qty_total')
    def _compute_freight_unit(self):
        for rec in self:
            try:
                rec.freight_unit = rec.freight_amount / rec.qty_total
            except ZeroDivisionError:
                rec.freight_unit = 0

    @api.depends('fca_amount', 'qty_total')
    def _compute_fca_unit(self):
        for rec in self:
            try:
                rec.fca_unit = rec.fca_amount / rec.qty_total
            except ZeroDivisionError:
                rec.fca_unit = 0

    @api.depends('road_transportation_amount', 'qty_total')
    def _compute_road_transportation_unit(self):
        for rec in self:
            try:
                rec.road_transportation_unit = rec.road_transportation_amount / rec.qty_total
            except ZeroDivisionError:
                rec.road_transportation_unit = 0

    @api.depends('logistics_service_amount', 'qty_total')
    def _compute_logistics_service_unit(self):
        for rec in self:
            try:
                rec.logistics_service_unit = rec.logistics_service_amount / rec.qty_total
            except ZeroDivisionError:
                rec.logistics_service_unit = 0

    @api.depends('cost_amount', 'qty_total')
    def _compute_cost_unit(self):
        for rec in self:
            try:
                rec.cost_unit = rec.cost_amount / rec.qty_total
            except ZeroDivisionError:
                rec.cost_unit = 0

    @api.depends('stock_picking_ids.marks_numbers')
    def _compute_marks_numbers(self):
        for invoice in self:
            if not invoice.stock_picking_ids:
                invoice.marks_numbers = ''
                continue
            temp = {picking.marks_numbers for picking in invoice.stock_picking_ids if picking.marks_numbers}
            invoice.marks_numbers = ', '.join(sorted(temp))

    @api.depends('invoice_date_due')
    def _compute_is_payment_due_on_weekend(self):
        for record in self:
            if record.invoice_date_due:
                weekday = record.invoice_date_due.weekday()
                record.is_payment_due_on_weekend = weekday in (5, 6)  # 5: Saturday, 6: Sunday
            else:
                record.is_payment_due_on_weekend = False

    def asc_confirm_invoice(self):
        for rec in self:
            if rec.move_type == 'out_invoice':
                if rec.purchase_order_id.invoice_status != 'invoiced':
                    raise UserError("Please ensure Supplier CI is recorded first.")
            lead = rec.lead_id
            if not lead.purchase_order_id:
                raise UserError("No Purchase Order or Supplier CI found for this deal.")
            currency = rec.currency_id
            exchange_rate = self.lead_id.exchange_rate or self.lead_id.indicative_exchange_rate
            is_usd = currency == self.env.ref('base.USD')
            is_zar = currency == self.env.ref('base.ZAR')
            insurance = insurance_zar = 0.0
            freight = freight_zar = 0.0
            interest = interest_zar = 0.0
            procurement = procurement_doc_zar = 0.0
            sales_price = sales_price_zar = 0.0
            fob = fob_zar = 0.0
            # fob = self.fob_amount

            # fca = self.fca_amount
            # road = self.road_transportation_amount
            # logistics = self.logistics_service_amount

            if rec.currency_id == self.env.ref('base.ZAR'):
                roe = lead.exchange_rate if lead.exchange_rate else lead.indicative_exchange_rate
                freight_zar = self.freight_amount
                insurance_zar = self.insurance_amount
                interest_zar = self.interest_amount
                procurement_doc_zar = self.procurement_documentation_amount

                if lead.cover_report_amount:
                    sales_price_zar = lead.cover_report_amount
                else:
                    sales_price_zar = rec.cost_amount

                if not lead.is_internal:
                    fob_zar = sales_price_zar - (freight_zar + insurance_zar)
                else:
                    fob_zar = rec.fob_amount
                    procurement_doc_zar = sales_price_zar - (fob_zar + freight_zar + insurance_zar + interest_zar)

                sales_price = sales_price_zar / exchange_rate
                fob = fob_zar / exchange_rate
                freight = freight_zar / exchange_rate
                insurance = insurance_zar / exchange_rate
                interest = interest_zar / exchange_rate
                procurement = procurement_doc_zar / exchange_rate
            if rec.currency_id == self.env.ref('base.USD'):
                freight = self.freight_amount
                insurance = self.insurance_amount
                interest = self.interest_amount
                procurement = self.procurement_documentation_amount
                roe = lead.exchange_rate if lead.exchange_rate else lead.indicative_exchange_rate
                if roe and roe != 0.0:
                    sales_price = rec.cost_amount / roe
                else:
                   if rec.qty_delivered:
                    sales_price = rec.invoice_line_ids.price_unit * rec.qty_delivered
                   else:
                    sales_price = rec.invoice_line_ids.price_unit * rec.qty_total
                # sales_price = rec.cost_amount
                # try:
                #     sales_price = sales_price / roe
                # except ZeroDivisionError:
                #     raise UserError("Exchange rate is zero, cannot convert sales price.")
                # if not lead.is_internal:
                #     fob = sales_price - (freight + insurance)
                if not lead.is_internal:
                    if rec.fob_amount == 0.0:
                        fob = rec.fob_amount
                    else:
                        fob = sales_price - (freight + insurance)
                else:
                    fob = rec.fob_amount
                    procurement = sales_price - (fob + freight + insurance + interest)

                    fob_zar = fob * exchange_rate
                    freight_zar = freight * exchange_rate
                    insurance_zar = insurance * exchange_rate
                    interest_zar = interest * exchange_rate
                    # fca_zar = fca * exchange_rate
                    # road_zar = road * exchange_rate
                    # logistics_zar = logistics * exchange_rate
                    # cost_zar = cost_usd * exchange_rate
                    procurement_doc_zar = procurement * exchange_rate
            action = {
                'name': 'Commercial Invoice',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'asc.confirm.invoice',
                'target': 'new',
                'context': {'default_sale_invoice_id': rec.id,
                            'default_date': rec.invoice_date,
                            'default_currency_id': rec.currency_id.id,
                            'default_insurance_amount': insurance,
                            'default_insurance_amount_zar': insurance_zar,
                            'default_freight_amount': freight,
                            'default_freight_amount_zar': freight_zar,
                            'default_interest_amount': interest,
                            'default_interest_amount_zar': interest_zar,
                            'default_procurement_documentation_amount': procurement,
                            'default_procurement_documentation_amount_zar': procurement_doc_zar,
                            'default_cost_amount': sales_price,
                            'default_cost_amount_zar': sales_price_zar,
                            'default_fob_amount': fob,
                            'default_fob_amount_zar': fob_zar,
                            }
            }
            return action
        else:
            raise UserError("No proforma invoice found.")

    # def asc_confirm_invoice(self):
    #     for rec in self:
    #         if rec.move_type == 'out_invoice':
    #             if rec.purchase_order_id.invoice_status != 'invoiced':
    #                 raise UserError("Please ensure Supplier CI is recorded first.")
    #         lead = rec.lead_id
    #         if not lead.purchase_order_id:
    #             raise UserError("No Purchase Order or Supplier CI found for this deal.")
    #         insurance = rec.insurance_amount
    #         freight = rec.freight_amount
    #         interest = self.interest_amount
    #         procurement = self.procurement_documentation_amount
    #         if lead.cover_report_amount:
    #             sales_price = lead.cover_report_amount
    #         else:
    #             sales_price = rec.cost_amount
    #         if rec.currency_id == self.env.ref('base.ZAR'):
    #             roe = lead.exchange_rate if lead.exchange_rate else lead.indicative_exchange_rate
    #             try:
    #                 sales_price = sales_price / roe
    #             except ZeroDivisionError:
    #                 raise UserError("Exchange rate is zero, cannot convert sales price.")
    #         if not lead.is_internal:
    #             fob = sales_price - (freight + insurance)
    #         else:
    #             fob = rec.fob_amount
    #             procurement = sales_price - (fob + freight + insurance + interest)
    #         action = {
    #             'name': 'Commercial Invoice',
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'asc.confirm.invoice',
    #             'target': 'new',
    #             'context': {'default_sale_invoice_id': rec.id,
    #                         'default_date': rec.invoice_date,
    #                         'default_currency_id': rec.currency_id.id,
    #                         'default_insurance_amount': insurance,
    #                         'default_freight_amount': freight,
    #                         'default_interest_amount': interest,
    #                         'default_procurement_documentation_amount': procurement,
    #                         'default_cost_amount': sales_price,
    #                         'default_fob_amount': fob,}
    #         }
    #         return action
    #     else:
    #         raise UserError("No proforma invoice found.")

    def set_incoming_document_wizard(self):
        action = {
            'name': 'Set list of documents',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'asc.set.document',
            'target': 'new',
            'context': {'default_sale_invoice_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_type': 'incoming',
                        'default_responsible': 'buyer'}
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
            'context': {'default_sale_invoice_id': self.id,
                        'default_lead_id': self.lead_id.id,
                        'default_type': 'outgoing',
                        'default_responsible': 'buyer'}
        }
        return action

    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'out_invoice': _('Proforma Invoice'),
                'out_refund': _('Draft Credit Note'),
                'in_invoice': _('Draft Bill'),
                'in_refund': _('Draft Vendor Credit Note'),
                'out_receipt': _('Draft Sales Receipt'),
                'in_receipt': _('Draft Purchase Receipt'),
                'entry': _('Draft Entry'),
            }[self.move_type]
            name += ' '
        if not self.name or self.name == '/':
            if self.id:
                name += '(* %s)' % str(self.id)
        else:
            name += self.name
            if self.env.context.get('input_full_display_name'):
                if self.partner_id:
                    name += f', {self.partner_id.name}'
                if self.date:
                    name += f', {format_date(self.env, self.date)}'
        return name + (f" ({shorten(self.ref, width=50)})" if show_ref and self.ref else '')

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

    def print_proforma_invoice(self):
        self.ensure_one()
        address = self.partner_id.address_text or ""
        address_length = len(address)

        if address_length <= 250:
            report_id = 'afrex_supply_chain.action_report_asc_proforma_invoice'
        else:
            raise UserError(
                "Address is too long ({} characters). Please reduce display address content to avoid report overlap.".format(
                    address_length))
        return self.env.ref(report_id).report_action(self)

    def print_commercial_invoice(self):
        self.ensure_one()
        address = self.partner_id.address_text or ""
        address_length = len(address)

        if address_length <= 250:
            report_id = 'afrex_supply_chain.action_report_asc_commercial_invoice'
        else:
            raise UserError(
                "Address is too long ({} characters). Please reduce display address content to avoid report overlap.".format(
                    address_length))
        return self.env.ref(report_id).report_action(self)

        # return self.env.ref('afrex_supply_chain.action_report_asc_commercial_invoice').report_action(self)

    def print_credit_note(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_credit_note').report_action(self)

    def print_packing_list(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_packing_list').report_action(self)

    def print_origin_certificate(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_origin_certificate').report_action(self)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    product_combination_id = fields.Many2one('asc.product.combination')
    first_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.first_spec_id')
    second_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.second_spec_id')
    third_spec_id = fields.Many2one('asc.product.specification', related='product_combination_id.third_spec_id')
    packaging_id = fields.Many2one('asc.product.packaging', related='product_combination_id.packaging_id')
    product_description = fields.Char(related='product_combination_id.description')
