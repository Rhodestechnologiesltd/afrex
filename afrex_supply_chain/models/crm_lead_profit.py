# -*- coding:utf-8 -*-
import calendar
from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import math
import logging

_logger = logging.getLogger(__name__)


class Lead(models.Model):
    _inherit = 'crm.lead'

    indicative_exchange_rate = fields.Float(string="Indicative Rate of Exchange (ROE) USDZAR", digits="Prices per Unit")
    exchange_rate = fields.Float(string="Booked Rate of Exchange", digits="Prices per Unit")
    # lead_id = fields.Many2one('crm.lead')
    banking_fee_ids = fields.One2many('asc.banking.fee', 'lead_id', string="Banking Fees")

    afrex_insurance_agent_id = fields.Many2one('res.partner', string="Insurance Agent")

    insurance_premium_amount = fields.Float("Insurance Premium")
    fob_value_sug = fields.Float(compute="validate_cif_amount", store=True)
    insurance_premium_amount_zar = fields.Float("Insurance Premium in ZAR",
                                                compute="compute_insurance_premium_amount_zar", store=True,
                                                digits="Prices per Unit")
    insurance_premium_unit = fields.Float("Insurance Premium per MT", compute="compute_insurance_premium_unit",
                                          store=True)

    afrex_freight_amount = fields.Float("Freight borne by Afrex", compute="compute_afrex_freight_amount",
                                        inverse="inverse_afrex_freight_amount", store=True)
    afrex_freight_rate = fields.Float("Freight Rate / MT")

    procurement_agent_id = fields.Many2one('res.partner', string="Procurement Agent")
    procurement_commission_fob_rate = fields.Float(string="Procurement Commission Rate against FOB")
    procurement_commission_fob_amount = fields.Float(string="Procurement Commission against FOB",
                                                     compute="compute_procurement_commission_fob_amount", store=True)

    procurement_commission_unit = fields.Float(string="Procurement Commission per MT")
    procurement_commission_unit_amount = fields.Float(string="Procurement Commission Total",
                                                      compute='compute_procurement_commission_unit_amount', store=True)

    procurement_fee_rate = fields.Float(string="Procurement Fee Rate against CIF")
    procurement_fee_amount = fields.Float(string="Procurement Fee against CIF Total",
                                          compute='compute_procurement_fee_amount', store=True)

    sales_agent_id = fields.Many2one('res.partner', string="Sales Agent")
    sales_commission_unit = fields.Float(string="Sales Commission per MT")
    sales_commission_amount = fields.Float(string="Sales Commission Total", compute='compute_sales_commission_amount',
                                           store=True)

    switch_bl_provision_amount = fields.Float(string="switch_bl_provision_amount")

    bank_fee_total = fields.Float(string="bank_fee_total", compute='compute_bank_fee_total', store=True)

    sales_cost = fields.Float(string="sales_cost", compute='compute_sales_cost', store=True)
    other_cost = fields.Float(string="other_cost", compute='compute_other_cost', store=True)

    total_cost = fields.Float(string="total_cost", compute='compute_total_cost', store=True)
    total_cost_unit = fields.Float(string="total_cost_unit", compute='compute_total_cost_unit', store=True)

    initial_sales_price_unit = fields.Float(string="initial_sales_price_unit",
                                            compute='compute_initial_sales_price_unit', store=True)
    initial_sales_price_unit_unrounded = fields.Float(string="Unrounded Initial Sales Price per MT")
    sales_price_unit = fields.Float(string="Final calculated Sales Price", compute='compute_sales_price_unit',
                                    store=True)
    sales_price_unit_unrounded = fields.Float(string="Unrounded Final Sales Price per MT")

    initial_sales_price = fields.Float(string="initial_sales_price", compute='compute_initial_sales_price', store=True)
    sales_price = fields.Float(string="sales_price", compute='compute_sales_price', store=True)
    sales_price_unrounded = fields.Float(string="Unrounded Final sales_price")

    is_sales_price_override = fields.Boolean(string="Override Sales Price",
                                             help="Check this box if you want to override the calculated sales price")
    agreed_sales_price_unit = fields.Float(string="Agreed Sales Price per MT")
    agreed_sales_price = fields.Float(string="Agreed Sales Price", compute='compute_agreed_sales_price', store=True)

    gross_profit_amount = fields.Float(string="gross_profit_amount", compute='compute_gross_profit_amount', store=True)
    gross_profit_percentage = fields.Float(string="gross_profit_percentage", compute='compute_gross_profit_percentage',
                                           store=True)

    markup_amount = fields.Float(string="markup_amount", compute='compute_markup_amount', store=True)
    markup_percentage = fields.Float(string="markup_percentage", compute='compute_markup_percentage', store=True)

    markup = fields.Float(string="Markup", help="Theoretical markup for Profit Estimate", default=0.06)

    minimum_gross_profit = fields.Float(string="Minimum Gross Profit", related='company_id.minimum_gross_profit')
    minimum_markup = fields.Float(string="Minimum Markup", related='company_id.minimum_markup')

    cover_report_amount = fields.Float(string="Cover Report Amount")

    purchase_order_freight_amount_zar = fields.Float(compute='compute_purchase_order_freight_amount_zar', store=True,
                                                     digits="Prices per Unit")
    purchase_order_fob_amount_zar = fields.Float(compute='compute_purchase_order_fob_amount_zar', store=True,
                                                 digits="Prices per Unit")
    purchase_order_fca_amount_zar = fields.Float(compute='compute_purchase_order_fca_amount_zar', store=True,
                                                 digits="Prices per Unit")
    purchase_order_insurance_amount_zar = fields.Float(compute='compute_purchase_order_insurance_amount_zar',
                                                       store=True, digits="Prices per Unit")
    afrex_freight_amount_zar = fields.Float(compute='compute_afrex_freight_amount_zar', store=True,
                                            digits="Prices per Unit")
    procurement_fee_amount_zar = fields.Float(compute='compute_procurement_fee_amount_zar', store=True,
                                              digits="Prices per Unit")
    sales_price_zar = fields.Float(compute='compute_sales_price_zar', store=True, digits="Prices per Unit")
    agreed_sales_price_zar = fields.Float(compute='compute_agreed_sales_price_zar', store=True,
                                          digits="Prices per Unit")
    insurance_premium_unit_zar = fields.Float(compute='compute_insurance_premium_unit_zar', store=True,
                                              digits="Prices per Unit")

    dap_amount = fields.Float(string="DAP Amount", compute="_compute_dap_amount", store=True, digits="Prices per Unit",
                              help="The DAP amount is the total cost of the product including all costs up to delivery at the customer's premises.")
    cif_amount = fields.Float(string="CIF Amount", compute="_compute_cif_amount", store=True, digits="Prices per Unit",
                              help="The CIF amount is the total cost of the product including all costs up to the port of discharge.")

    is_cif_override = fields.Boolean(string="Override CIF Price")

    manual_purchase_order_cif_amount = fields.Float(string="CIF Amount")

    # new fields for credit cost

    # credit_cost_trans_terms = fields.Selection([('180_days', "180 Days"),
    #                                             ('120_days', "120 Days"), ], string="Credit Terms")
    credit_days = fields.Integer(string="SGT Credit Days from Statement")

    commission_amount = fields.Float(string="Commission", default=0.0025)
    total_commission_amount = fields.Float(string="Commission", compute="_compute_total_commission_amount", store=True)

    expected_payment_date = fields.Date(string="Expected Payment Date(Supplier)")
    month_end = fields.Date(string="Month End of Payment Date", compute="_compute_month_end", store=True)
    credit_days_eom = fields.Integer(string="Credit Days from Payment Date to EOM", compute="_compute_new_credit_cost",
                                     store=True)

    sofr_rate = fields.Float(string="6 Month SOFR")
    sofr_margin = fields.Float(string="Interest Rate", default=0.0275, digits=(16, 6))
    eff_rate = fields.Float(string="Effective Rate", compute="_compute_new_credit_cost", store=True, digits=(16, 6))
    day_rate = fields.Float(string="Effective Rate", compute="_compute_new_credit_cost", store=True, digits=(16, 6))
    total_sofr = fields.Float(string="Nominal Rate", compute="_compute_total_sofr", store=True, digits=(16, 6))

    bank_charges_amount = fields.Float(string="Bank Charges USD 65 Per Transaction")
    no_of_transaction = fields.Integer(string="Transaction")
    total_bank_charges_amount = fields.Float(string="Total Bank Charges for Credit cost", compute="_compute_total_bc",
                                             store=True)

    credit_cost_to_month_end = fields.Float(string="SGT Credit Cost to Month End", compute="_compute_new_credit_cost",
                                            store=True)

    credit_cost_total = fields.Float(string="SGT Total Credit Cost Amount",
                                     compute="_compute_new_credit_cost", store=True)
    total_credit_cost = fields.Float(string="SGT Credit Cost for 180 days or 120 Days",
                                     compute="_compute_new_credit_cost", store=True)
    capital_at_statement = fields.Float("Capital at Statement", compute="_compute_new_credit_cost", store=True)

    credit_insurance_amount_new = fields.Float(string="credit insurance amount",
                                               compute='compute_credit_insurance_amount_new',
                                               store=True)
    # ZAR New updated field
    credit_cost_amount_zar = fields.Float(compute='compute_credit_cost_amount_zar', store=True,
                                          digits="Prices per Unit")
    credit_cost_amount_month_end_zar = fields.Float(compute='compute_credit_cost_amount_zar', store=True,
                                                    digits="Prices per Unit")
    credit_insurance_amount_zar = fields.Float(compute='compute_credit_insurance_amount_zar', store=True,
                                               digits="Prices per Unit")

    is_change = fields.Boolean(default=False)
    is_click = fields.Boolean(default=False)
    is_done = fields.Boolean(default=False)
    sale_invoice_id_post = fields.Boolean(compute='compute_invoice_status', store=True, )
    is_adjusted = fields.Boolean(default=False)

    credit_cost_text = fields.Selection([('fob', "FOB Price"), ('cif', "CIF Purchase Price")], string="Credit")
    freight_text = fields.Char(string="Freight Text", default="Freight Forwarder")
    ins_text = fields.Char(string="Text", default="Sales Value x 110% x 0.25% + USD 10")
    SGT_text = fields.Char(string="Freight Text")

    @api.depends('insurance_premium_amount', 'purchase_order_fob_amount', 'purchase_order_insurance_amount',
                 'afrex_freight_amount', 'purchase_order_freight_amount')
    def _compute_can_change(self):
        for rec in self:
            rec.is_change = (
                    rec.insurance_premium_amount != rec._origin.insurance_premium_amount or
                    rec.purchase_order_insurance_amount != rec._origin.purchase_order_insurance_amount
                    or rec.purchase_order_fob_amount != rec._origin.purchase_order_fob_amount
                    or rec.purchase_order_freight_amount != rec._origin.purchase_order_freight_amount
                    or rec.afrex_freight_amount != rec._origin.afrex_freight_amount
            )

    @api.onchange('insurance_premium_amount', 'purchase_order_fob_amount', 'purchase_order_insurance_amount',
                  'afrex_freight_amount', 'purchase_order_freight_amount', 'is_cif_override',
                  'manual_purchase_order_cif_amount', 'is_adjusted')
    def _onchange_amounts(self):
        if not self._origin.id:
            return
        for rec in self:

            if (rec.insurance_premium_amount != rec._origin.insurance_premium_amount or
                    rec.purchase_order_insurance_amount != rec._origin.purchase_order_insurance_amount
                    or rec.purchase_order_fob_amount != rec._origin.purchase_order_fob_amount
                    or rec.purchase_order_freight_amount != rec._origin.purchase_order_freight_amount
                    or rec.afrex_freight_amount != rec._origin.afrex_freight_amount or
                    rec.is_cif_override or rec.manual_purchase_order_cif_amount != rec._origin.manual_purchase_order_cif_amount):
                rec.is_change = True
                rec.is_adjusted = True
                if rec.purchase_order_incoterm_selection == 'cif':
                    rec.validate_cif_amount()
                elif rec.purchase_order_incoterm_selection == 'cfr':
                    rec.validate_cfr_amount()
                elif rec.purchase_order_incoterm_selection == 'fob':
                    rec.validate_fob_amount()
                else:
                    pass

            else:
                rec.is_change = False

    def validate_cif_amount(self):
        for rec in self:
            fob = rec.purchase_order_fob_amount or 0
            insurance = rec.purchase_order_insurance_amount or 0
            freight = rec.purchase_order_freight_amount or 0
            # calculated_cif = fob + insurance + freight
            cif_amount = rec.purchase_order_cif_amount or 0
            entered_count = sum([bool(fob), bool(insurance), bool(freight)])
            if freight and insurance:
                rec.is_adjusted = True
                rec.fob_value_sug = cif_amount - (
                        rec.purchase_order_insurance_amount + rec.purchase_order_freight_amount)
            if entered_count > 2:
                calculated_cif = fob + insurance + freight
                cif_amount = rec.purchase_order_cif_amount or 0
                if round(cif_amount, 2) != round(calculated_cif, 2):
                    raise ValidationError(
                        f"CIF amount mismatch: Please check the values.\n"
                        f"Expected: {cif_amount}, Entered: {calculated_cif}"
                    )
        return True

    def validate_cfr_amount(self):
        for rec in self:
            fob = rec.purchase_order_fob_amount or 0
            freight = rec.purchase_order_freight_amount or rec.afrex_freight_amount or 0
            insurance = rec.purchase_order_insurance_amount or rec.insurance_premium_amount or 0
            cost = rec.purchase_order_cost_amount or 0
            cif_amount = rec.purchase_order_cost_amount or 0
            if freight and insurance:
                rec.is_adjusted = True
                rec.fob_value_sug = rec.purchase_order_cost_amount - (
                        rec.purchase_order_insurance_amount + rec.purchase_order_freight_amount)
            entered_count = sum([bool(fob), bool(freight)])
            if entered_count > 1:

                calculated_cif = rec.purchase_order_fob_amount + rec.purchase_order_freight_amount
                if rec.purchase_order_cost_amount != calculated_cif:
                    raise ValidationError(
                        f"CFR amount mismatch: Please Check the Values"
                    )

        return True

    def validate_fob_amount(self):
        for rec in self:
            fob = rec.purchase_order_fob_amount or 0
            freight = rec.purchase_order_freight_amount
            insurance = rec.purchase_order_insurance_amount
            cost = rec.purchase_order_cost_amount or 0
            cif_amount = rec.purchase_order_cost_amount or 0
            rec.fob_value_sug = rec.purchase_order_cost_amount
            if freight or insurance:
                raise ValidationError(
                    "You can only enter the FOB amount. Freight or Insurance values are not allowed."
                )
            if rec.purchase_order_fob_amount == 0:
                continue
            elif rec.purchase_order_cost_amount != rec.purchase_order_fob_amount:
                    raise ValidationError(
                        "FOB amount mismatch: Please check the values."
                    )
        return True

    @api.depends('sale_invoice_id.state')
    def compute_invoice_status(self):
        for rec in self:
            rec.sale_invoice_id_post = rec.sale_invoice_id.state == 'posted'

    def action_mark_done(self):
        for rec in self:
            rec.sale_invoice_id_post = False
            rec.is_done = True

    def action_apply(self):
        self.is_click = True
        self.is_change = False
        self.is_adjusted = False
        self.ensure_one()

        sale_invoice_id = self.sale_invoice_id
        sale_order_id = self.sale_order_id

        if not sale_invoice_id and not sale_order_id:
            raise UserError("No Sale Invoice or Sale Order found for this lead.")

        if sale_invoice_id:
            if sale_invoice_id.state == 'draft':
                self.purchase_order_id.action_apply_proforma()
                self.message_post(
                    body=_("Values updated in the Afrex Proforma."))
            elif sale_invoice_id.state == 'posted':
                self.purchase_order_id.action_apply_commercial()
                self.message_post(
                    body=_("Values updated in the Afrex Commercial."))
            else:
                raise UserError("Invoice must be in Proforma or commercial state to update values.")
        elif sale_order_id:
            self.purchase_order_id.update_sales_order()
            self.message_post(
                body=_("Values updated in the Afrex Offer."))

    # credit insurance amount based on CIF
    @api.depends('credit_insurance_rate', 'manual_purchase_order_cif_amount', 'purchase_order_cif_amount')
    def compute_credit_insurance_amount_new(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                if rec.is_cif_override:
                    rec.credit_insurance_amount_new = rec.credit_insurance_rate * rec.manual_purchase_order_cif_amount
                else:
                    rec.credit_insurance_amount_new = rec.credit_insurance_rate * rec.purchase_order_cif_amount

    # ZAR methods for credit insurance and Credit cost
    @api.depends('credit_insurance_amount_new', 'indicative_exchange_rate', 'exchange_rate')
    def compute_credit_insurance_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.credit_insurance_amount_zar = rec.credit_insurance_amount_new * roe

    @api.depends('credit_cost_to_month_end', 'total_credit_cost', 'indicative_exchange_rate', 'exchange_rate')
    def compute_credit_cost_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.credit_cost_amount_zar = rec.total_credit_cost * roe
            rec.credit_cost_amount_month_end_zar = rec.credit_cost_to_month_end * roe

    # credit cost for Payment date to Month end
    @api.depends('total_sofr', 'credit_cost_text', 'purchase_order_fob_amount', 'purchase_order_cif_amount', 'manual_purchase_order_cif_amount',
                 'total_commission_amount', 'total_bank_charges_amount', 'is_cif_override',
                 'expected_payment_date', 'month_end', 'credit_days', 'credit_days_eom')
    def _compute_new_credit_cost(self):
        for rec in self:
            if rec.credit_cost_text == 'cif':
                if rec.is_cif_override:
                    base_cost = rec.manual_purchase_order_cif_amount + rec.total_commission_amount + rec.total_bank_charges_amount
                else:
                    base_cost = rec.purchase_order_cif_amount + rec.total_commission_amount + rec.total_bank_charges_amount
            else:
                base_cost = rec.purchase_order_fob_amount + rec.total_commission_amount + rec.total_bank_charges_amount

            eff_rate = (1 + rec.total_sofr / 12) ** 12 - 1
            day_rate = eff_rate / 360
            rec.credit_days_eom = 0
            rec.credit_cost_to_month_end = 0.0
            if rec.month_end and rec.expected_payment_date <= rec.month_end:
                rec.credit_days_eom = (rec.month_end - rec.expected_payment_date).days + 1
                rec.credit_cost_to_month_end = base_cost * day_rate * rec.credit_days_eom

            # Capital cost at Statement
            rec.capital_at_statement = base_cost + rec.credit_cost_to_month_end

            # Credit Cost for Remaining Days (from Statement)
            rec.total_credit_cost = rec.capital_at_statement * day_rate * rec.credit_days
            rec.credit_cost_total = rec.credit_cost_to_month_end + rec.total_credit_cost + rec.total_bank_charges_amount + rec.total_commission_amount

            rec.eff_rate = round(eff_rate, 6)
            rec.day_rate = round(day_rate, 6)
            rec.credit_cost_to_month_end = round(rec.credit_cost_to_month_end, 2)
            rec.capital_at_statement = round(rec.capital_at_statement, 2)
            rec.total_credit_cost = round(rec.total_credit_cost, 2)
            rec.credit_cost_total = round(rec.credit_cost_total, 2)

    # month end date calculation for credit cost amount
    @api.depends('expected_payment_date')
    def _compute_month_end(self):
        for record in self:
            if record.expected_payment_date:
                payment_date = record.expected_payment_date
                last_day = calendar.monthrange(payment_date.year, payment_date.month)[1]
                record.month_end = date(payment_date.year, payment_date.month, last_day)
            else:
                record.month_end = False

    # Bank charges amount
    @api.depends('bank_charges_amount', 'no_of_transaction')
    def _compute_total_bc(self):
        for record in self:
            if record.bank_charges_amount and record.no_of_transaction:
                record.total_bank_charges_amount = (
                        (record.bank_charges_amount or 0.0) * (record.no_of_transaction or 0)
                )

    # sofr amount
    @api.depends('sofr_rate', 'sofr_margin')
    def _compute_total_sofr(self):
        for record in self:
            if record.sofr_rate and record.sofr_margin:
                record.total_sofr = record.sofr_rate + record.sofr_margin

    # credit cost commission amount
    @api.depends('commission_amount', 'credit_cost_text', 'purchase_order_fob_amount', 'purchase_order_cif_amount', 'is_cif_override',
                 'manual_purchase_order_cif_amount')
    def _compute_total_commission_amount(self):
        for rec in self:
            if rec.credit_cost_text == 'cif':
                if rec.is_cif_override:
                    rec.total_commission_amount = rec.manual_purchase_order_cif_amount * rec.commission_amount
                else:
                    rec.total_commission_amount = rec.purchase_order_cif_amount * rec.commission_amount
            else:
                rec.total_commission_amount = rec.purchase_order_fob_amount * rec.commission_amount

    @api.depends('purchase_order_freight_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_purchase_order_freight_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_freight_amount_zar = rec.purchase_order_freight_amount * roe

    @api.depends('purchase_order_fob_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_purchase_order_fob_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_fob_amount_zar = rec.purchase_order_fob_amount * roe

    @api.depends('purchase_order_fca_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_purchase_order_fca_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_fca_amount_zar = rec.purchase_order_fca_amount * roe

    @api.depends('purchase_order_insurance_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_purchase_order_insurance_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.purchase_order_insurance_amount_zar = rec.purchase_order_insurance_amount * roe

    @api.depends('afrex_freight_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_afrex_freight_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.afrex_freight_amount_zar = rec.afrex_freight_amount * roe

    @api.depends('insurance_premium_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_insurance_premium_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.insurance_premium_amount_zar = rec.insurance_premium_amount * roe

    @api.depends('procurement_fee_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_procurement_fee_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.procurement_fee_amount_zar = rec.procurement_fee_amount * roe

    @api.depends('sales_price', 'indicative_exchange_rate', 'exchange_rate')
    def compute_sales_price_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.sales_price_zar = rec.sales_price * roe

    @api.depends('agreed_sales_price', 'indicative_exchange_rate', 'exchange_rate')
    def compute_agreed_sales_price_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.agreed_sales_price_zar = rec.agreed_sales_price_zar * roe

    @api.depends('insurance_premium_amount', 'product_qty')
    def compute_insurance_premium_unit(self):
        for rec in self:
            try:
                rec.insurance_premium_unit = rec.insurance_premium_amount / rec.product_qty
            except ZeroDivisionError:
                rec.insurance_premium_unit = 0

    @api.depends('insurance_premium_unit', 'indicative_exchange_rate', 'exchange_rate')
    def compute_insurance_premium_unit_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.insurance_premium_unit_zar = rec.insurance_premium_unit * roe

    @api.depends('afrex_freight_rate', 'product_qty', 'packaging_weight')
    def compute_afrex_freight_amount(self):
        for rec in self:
            rec.afrex_freight_amount = rec.product_qty * (1 + (rec.packaging_weight / 1000)) * rec.afrex_freight_rate

    def inverse_afrex_freight_amount(self):
        for rec in self:
            if rec.product_qty and rec.packaging_weight:
                divisor = rec.product_qty * (1 + (rec.packaging_weight / 1000))
                rec.afrex_freight_rate = rec.afrex_freight_amount / divisor

    @api.depends('purchase_order_fca_amount', 'road_transportation_amount', 'logistics_service_amount')
    def _compute_dap_amount(self):
        for rec in self:
            rec.dap_amount = rec.purchase_order_fca_amount + rec.road_transportation_amount + rec.logistics_service_amount

    @api.depends('purchase_order_fob_amount', 'purchase_order_freight_amount', 'purchase_order_insurance_amount')
    def _compute_cif_amount(self):
        for rec in self:
            rec.cif_amount = rec.purchase_order_fob_amount + rec.purchase_order_freight_amount + rec.purchase_order_insurance_amount

    @api.depends('procurement_commission_fob_rate', 'purchase_order_fob_amount')
    def compute_procurement_commission_fob_amount(self):
        for rec in self:
            rec.procurement_commission_fob_amount = rec.procurement_commission_fob_rate * rec.purchase_order_fob_amount

    @api.depends('procurement_commission_unit', 'product_qty')
    def compute_procurement_commission_unit_amount(self):
        for rec in self:
            rec.procurement_commission_unit_amount = rec.procurement_commission_unit * rec.product_qty

    @api.depends('procurement_fee_rate', 'purchase_order_cif_amount', 'is_cif_override',
                 'manual_purchase_order_cif_amount')
    def compute_procurement_fee_amount(self):
        for rec in self:
            if rec.is_cif_override:
                rec.procurement_fee_amount = rec.procurement_fee_rate * rec.manual_purchase_order_cif_amount
            else:
                rec.procurement_fee_amount = rec.procurement_fee_rate * rec.purchase_order_cif_amount

    @api.depends('sales_commission_unit', 'product_qty')
    def compute_sales_commission_amount(self):
        for rec in self:
            rec.sales_commission_amount = rec.sales_commission_unit * rec.product_qty

    @api.depends('banking_fee_ids', 'banking_fee_ids.amount')
    def compute_bank_fee_total(self):
        for rec in self:
            total = 0
            for fee in rec.banking_fee_ids:
                total += fee.amount
            rec.bank_fee_total = total

    @api.depends('supplier_delivery_method', 'purchase_order_cif_amount', 'procurement_commission_fob_amount',
                 'procurement_commission_unit_amount', 'sales_commission_amount', 'switch_bl_provision_amount',
                 'road_transportation_amount', 'logistics_service_amount', 'is_internal', 'is_cif_override',
                 'manual_purchase_order_cif_amount')
    def compute_sales_cost(self):
        for rec in self:
            if rec.supplier_delivery_method == 'sea':
                if rec.is_cif_override:
                    rec.sales_cost = rec.manual_purchase_order_cif_amount + rec.procurement_commission_fob_amount + rec.procurement_commission_unit_amount + rec.sales_commission_amount + rec.switch_bl_provision_amount
                else:
                    # purchase_order_cif_amount includes 'afrex_freight_amount', 'insurance_premium_amount', 'purchase_order_cost_amount'
                    rec.sales_cost = rec.purchase_order_cif_amount + rec.procurement_commission_fob_amount + rec.procurement_commission_unit_amount + rec.sales_commission_amount + rec.switch_bl_provision_amount
            if rec.supplier_delivery_method == 'road':
                rec.sales_cost = rec.purchase_order_cost_amount + rec.procurement_commission_unit_amount + rec.sales_commission_amount + rec.road_transportation_amount + rec.logistics_service_amount

    @api.depends('bank_fee_total', 'credit_cost_to_month_end', 'credit_insurance_amount_new', 'total_credit_cost',
                 'total_bank_charges_amount', 'total_commission_amount')
    def compute_other_cost(self):
        for rec in self:
            if rec.is_internal:
                rec.other_cost = rec.bank_fee_total + rec.credit_insurance_amount_new + rec.total_bank_charges_amount + rec.total_commission_amount
            else:
                rec.other_cost = rec.bank_fee_total + rec.credit_cost_to_month_end + rec.credit_insurance_amount_new + rec.total_credit_cost + rec.total_bank_charges_amount + rec.total_commission_amount

    @api.depends('sales_cost', 'other_cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.sales_cost + rec.other_cost

    @api.depends('total_cost', 'product_qty')
    def compute_total_cost_unit(self):
        for rec in self:
            if rec.product_qty > 0:
                rec.total_cost_unit = rec.total_cost / rec.product_qty
            else:
                rec.total_cost_unit = 0

    @api.depends('sales_price', 'product_qty', 'total_cost_unit', 'markup')
    def compute_initial_sales_price_unit(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.initial_sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.initial_sales_price_unit = 0
            else:
                temp = rec.total_cost_unit * (1 + rec.markup)
                rec.initial_sales_price_unit_unrounded = temp
                rec.initial_sales_price_unit = math.ceil(temp)

    @api.depends('sales_cost', 'procurement_fee_amount', 'credit_cost_to_month_end', 'total_credit_cost',
                 'initial_sales_price_unit',
                 'product_qty')
    def compute_initial_sales_price(self):
        for rec in self:
            if rec.is_internal:
                credit_cost_amount = rec.credit_cost_to_month_end + rec.total_credit_cost
                rec.initial_sales_price = rec.sales_cost + rec.procurement_fee_amount + credit_cost_amount
            else:
                rec.initial_sales_price = rec.initial_sales_price_unit * rec.product_qty

    @api.depends('sales_cost', 'procurement_fee_amount', 'credit_cost_to_month_end', 'total_credit_cost',
                 'initial_sales_price',
                 )
    def compute_sales_price(self):
        for rec in self:
            if rec.is_internal:
                credit_cost_amount = rec.credit_cost_to_month_end + rec.total_credit_cost
                rec.sales_price = rec.total_cost + rec.procurement_fee_amount + credit_cost_amount
            else:
                temp = rec.initial_sales_price
                rec.sales_price_unrounded = temp
                rec.sales_price = math.ceil(temp)

    @api.depends('sales_price', 'product_qty', 'sales_price_unrounded')
    def compute_sales_price_unit(self):
        for rec in self:
            if rec.is_internal:
                try:
                    rec.sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.sales_price_unit = 0
            else:
                try:
                    rec.sales_price_unit_unrounded = rec.sales_price_unrounded / rec.product_qty
                    rec.sales_price_unit = rec.sales_price / rec.product_qty
                except ZeroDivisionError:
                    rec.sales_price_unit_unrounded = 0
                    rec.sales_price_unit = 0

    @api.depends('is_sales_price_override', 'agreed_sales_price_unit', 'product_qty')
    def compute_agreed_sales_price(self):
        for rec in self:
            rec.agreed_sales_price = rec.agreed_sales_price_unit * rec.product_qty

    @api.depends('sales_price', 'sales_cost', 'is_sales_price_override', 'agreed_sales_price')
    def compute_gross_profit_amount(self):
        for rec in self:
            if rec.is_sales_price_override:
                rec.gross_profit_amount = abs(rec.agreed_sales_price - rec.sales_cost)
            else:
                rec.gross_profit_amount = abs(rec.sales_price - rec.sales_cost)

    @api.depends('gross_profit_amount', 'sales_price', 'is_sales_price_override', 'agreed_sales_price')
    def compute_gross_profit_percentage(self):
        for rec in self:
            try:
                if rec.is_sales_price_override:
                    rec.gross_profit_percentage = rec.gross_profit_amount / rec.agreed_sales_price
                else:
                    rec.gross_profit_percentage = rec.gross_profit_amount / rec.sales_price
            except ZeroDivisionError:
                rec.gross_profit_percentage = 0

    @api.depends('sales_price', 'total_cost', 'credit_cost_to_month_end', 'total_credit_cost',
                 'is_sales_price_override', 'agreed_sales_price')
    def compute_markup_amount(self):
        for rec in self:
            if rec.is_internal:
                if rec.is_sales_price_override:
                    credit_cost_amount = rec.credit_cost_to_month_end + rec.total_credit_cost

                    # rec.markup_amount = rec.agreed_sales_price - (rec.total_cost + rec.credit_cost_amount)
                    rec.markup_amount = rec.agreed_sales_price - (rec.total_cost + credit_cost_amount)
                else:
                    credit_cost_amount = rec.credit_cost_to_month_end + rec.total_credit_cost
                    rec.markup_amount = rec.sales_price - (rec.total_cost + credit_cost_amount)
            else:
                if rec.is_sales_price_override:
                    rec.markup_amount = rec.agreed_sales_price - rec.total_cost
                else:
                    rec.markup_amount = rec.sales_price - rec.total_cost

    @api.depends('markup_amount', 'total_cost', 'is_sales_price_override')
    def compute_markup_percentage(self):
        for rec in self:
            try:
                if rec.is_internal:
                    rec.markup_percentage = rec.markup_amount / rec.total_cost
                else:
                    if rec.is_sales_price_override:
                        rec.markup_percentage = rec.markup_amount / rec.total_cost
                    else:
                        rec.markup_percentage = rec.markup_amount / rec.total_cost
            except ZeroDivisionError:
                rec.markup_percentage = 0

    def print_profit_estimate(self):
        return self.env.ref('afrex_supply_chain.action_report_asc_profit_estimate_new').report_action(self)


    def write(self, vals):
        res = super().write(vals)
        for lead in self:
            if lead.purchase_order_id:
                update_vals = {}

                # FOB
                if 'purchase_order_fob_amount' in vals:
                    update_vals['fob_amount'] = vals['purchase_order_fob_amount']
                    if lead.purchase_order_qty_delivered > 0:
                        update_vals['fob_unit'] = vals['purchase_order_fob_amount'] / lead.purchase_order_qty_delivered
                    elif lead.product_qty > 0:
                        update_vals['fob_unit'] = vals['purchase_order_fob_amount'] / lead.product_qty

                # Insurance
                if 'purchase_order_insurance_amount' in vals:
                    update_vals['insurance_amount'] = vals['purchase_order_insurance_amount']

                # Freight
                if 'purchase_order_freight_amount' in vals:
                    update_vals['freight_amount'] = vals['purchase_order_freight_amount']
                    if lead.purchase_order_qty_delivered > 0:
                        update_vals['freight_unit'] = vals['purchase_order_freight_amount'] / lead.purchase_order_qty_delivered
                    elif lead.product_qty > 0:
                        update_vals['freight_unit'] = vals['purchase_order_freight_amount'] / lead.product_qty

                # Finally, push changes into purchase order
                if update_vals:
                    lead.purchase_order_id.write(update_vals)
                    lead.purchase_order_id._compute_freight_amount()
                    lead.purchase_order_id._compute_freight_unit()

                invoices = lead.purchase_order_id.invoice_ids.filtered(lambda i: i.state != 'cancel')
                if not invoices:
                    continue
                qty_po = 0.0
                fob_unit_po = 0.00
                freight_unit_po = 0.00
                cost_unit_po = 0.00
                fob_unit_po = lead.purchase_order_fob_amount / lead.purchase_order_qty_delivered
                freight_unit_po = lead.purchase_order_freight_amount / lead.purchase_order_qty_delivered
                cost_unit_po = lead.purchase_order_cost_amount / lead.purchase_order_qty_delivered
                insurance_unit_po = lead.purchase_order_insurance_amount / lead.purchase_order_qty_delivered
                for inv in invoices:
                    # Get this invoice’s total quantity (sum of its own line quantities)
                    qty_po = sum(inv.invoice_line_ids.mapped('quantity')) or 0.0

                    # Skip if no quantity
                    if not qty_po:
                        continue

                    invoice_vals = {
                        'fob_unit_po': fob_unit_po,
                        'freight_unit_po': freight_unit_po,
                        'cost_unit_po': cost_unit_po,
                        'insurance_unit_po': insurance_unit_po,
                        'fob_amount_po': fob_unit_po * qty_po,
                        'freight_amount_po': freight_unit_po * qty_po,
                        'cost_amount_po': cost_unit_po * qty_po,
                        'insurance_amount_po': insurance_unit_po * qty_po,
                    }

                    if inv.state in ['draft','posted']:
                        inv.write(invoice_vals)
        return res

    # ********** Need to delete After Testing *************
    # unused fields
    agreed_credit_insurance_amount_zar = fields.Float(compute='compute_agreed_credit_insurance_amount_zar', store=True,
                                                      digits="Prices per Unit")
    other_cost_updated = fields.Float(string="other_cost", compute='compute_other_cost_updated', store=True)
    other_cost_agreed = fields.Float(string="other_cost", compute='compute_other_cost_agreed', store=True)
    total_cost_updated = fields.Float(string="total_cost", compute='compute_total_cost_updated', store=True)
    total_cost_updated_agreed = fields.Float(string="total_cost", compute='compute_total_cost_updated_agreed',
                                             store=True)
    credit_cost_rate = fields.Float(string="credit_cost_rate", default=0.0425)
    credit_cost_month = fields.Integer(string="No of Months for Credit Cost", default=4)
    credit_cost_amount = fields.Float(string="credit_cost_amount", compute='compute_credit_cost_amount', store=True)

    credit_insurance_rate = fields.Float(string="credit_insurance_rate", default=0.006)
    credit_insurance_amount = fields.Float(string="credit_insurance_amount", compute='compute_credit_insurance_amount',
                                           store=True)

    agreed_credit_insurance_rate = fields.Float(string="agreed_credit_insurance_rate", default=0.006)
    agreed_credit_insurance_amount = fields.Float(string="Credit Insurance Cost against Agreed Selling Price",
                                                  compute='compute_agreed_credit_insurance_amount', store=True)

    # unused methods
    @api.depends('other_cost', 'credit_insurance_amount')
    def compute_other_cost_updated(self):
        for rec in self:
            if rec.credit_insurance_amount:
                rec.other_cost_updated = rec.other_cost + rec.credit_insurance_amount
            else:
                rec.other_cost_updated = rec.other_cost

    @api.depends('other_cost', 'agreed_credit_insurance_amount')
    def compute_other_cost_agreed(self):
        for rec in self:
            if rec.agreed_credit_insurance_amount:
                rec.other_cost_agreed = rec.other_cost + rec.agreed_credit_insurance_amount
            else:
                rec.other_cost_agreed = rec.other_cost

    @api.depends('total_cost', 'credit_insurance_amount')
    def compute_total_cost_updated(self):
        for rec in self:
            if rec.credit_insurance_amount:
                rec.total_cost_updated = rec.total_cost + rec.credit_insurance_amount
            else:
                rec.total_cost_updated = rec.total_cost

    @api.depends('total_cost', 'agreed_credit_insurance_amount')
    def compute_total_cost_updated_agreed(self):
        for rec in self:
            if rec.agreed_credit_insurance_amount:
                rec.total_cost_updated_agreed = rec.total_cost + rec.agreed_credit_insurance_amount
            else:
                rec.total_cost_updated_agreed = rec.total_cost

    @api.depends('credit_insurance_rate', 'initial_sales_price')
    def compute_credit_insurance_amount(self):
        for rec in self:
            rec.credit_insurance_amount = rec.credit_insurance_rate * rec.initial_sales_price

    @api.depends('agreed_credit_insurance_rate', 'agreed_sales_price')
    def compute_agreed_credit_insurance_amount(self):
        for rec in self:
            rec.agreed_credit_insurance_amount = (rec.agreed_credit_insurance_rate * rec.agreed_sales_price)

    @api.depends('agreed_credit_insurance_amount', 'indicative_exchange_rate', 'exchange_rate')
    def compute_agreed_credit_insurance_amount_zar(self):
        for rec in self:
            roe = rec.exchange_rate if rec.exchange_rate else rec.indicative_exchange_rate
            rec.agreed_credit_insurance_amount_zar = rec.agreed_credit_insurance_amount * roe

    @api.depends('purchase_order_cif_amount', 'credit_cost_rate', 'credit_cost_month', 'is_cif_override',
                 'manual_purchase_order_cif_amount')
    def compute_credit_cost_amount(self):
        # =(CIF PURCHASE PRICE *(4.25%/12))*4
        for rec in self:
            if rec.credit_cost_rate > 0:
                if rec.is_cif_override:
                    rec.credit_cost_amount = (
                            rec.manual_purchase_order_cif_amount * (rec.credit_cost_rate / 12) * rec.credit_cost_month)
                else:
                    rec.credit_cost_amount = (
                            rec.purchase_order_cif_amount * (rec.credit_cost_rate / 12) * rec.credit_cost_month)
            else:
                rec.credit_cost_amount = 0
