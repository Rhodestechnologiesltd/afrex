from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import base64

_logger = logging.getLogger(__name__)


class SupplierInvoiceWizard(models.TransientModel):
    _name = 'asc.supplier.invoice'
    _description = 'Supplier Commercial Invoice Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    lead_id = fields.Many2one('crm.lead', related='purchase_order_id.lead_id', string='Trade Folder')
    sale_invoice_id = fields.Many2one(related="lead_id.sale_invoice_id")
    sale_order_id = fields.Many2one(related="lead_id.sale_order_id")
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm', related="purchase_order_id.incoterm_id")
    breakbulk_container = fields.Selection(related="purchase_order_id.breakbulk_container",
                                           string='Breakbulk or Container')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")

    ref = fields.Char(string='Invoice Number', required=True)
    quantity = fields.Float(string='Quantity (MT)', digits="Product Unit of Measure")
    date = fields.Date(string='Invoice Date')

    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date",
                                        readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)

    fob_unit = fields.Float("FOB/MT", tracking=True)
    freight_unit = fields.Float("Freight/MT", tracking=True)
    cost_unit = fields.Float("Cost/MT", digits="Prices per Unit", tracking=True)

    fob_amount = fields.Float("FOB", tracking=True)
    freight_amount = fields.Float("Freight", tracking=True)
    cost_amount = fields.Float("Cost", tracking=True)

    insurance_amount = fields.Float("Insurance", tracking=True)

    old_fob_unit = fields.Float("FOB/MT", digits="Prices per Unit")
    old_freight_unit = fields.Float("Freight/MT", digits="Prices per Unit")
    old_cost_unit = fields.Float("Cost/MT", digits="Prices per Unit")

    old_fob_amount = fields.Float("FOB", )
    old_freight_amount = fields.Float("Freight")
    old_cost_amount = fields.Float("Cost")

    old_insurance_amount = fields.Float("Insurance")

    currency_id = fields.Many2one('res.currency', string='Currency')
    exchange_rate = fields.Float('Exchange Rate')

    fob_unit_zar_zar = fields.Float("FOB/MT", digits="Prices per Unit")
    freight_unit_zar = fields.Float("Freight/MT", digits="Prices per Unit")
    cost_unit_zar = fields.Float("Cost/MT", digits="Prices per Unit")

    fob_amount_zar = fields.Float("FOB", )
    freight_amount_zar = fields.Float("Freight")
    cost_amount_zar = fields.Float("Cost")

    insurance_amount_zar = fields.Float("Insurance")

    can_confirm = fields.Boolean(compute='_compute_can_confirm')
    is_change = fields.Boolean(compute='_compute_can_change')
    is_click = fields.Boolean(default=False)
    is_adjusted = fields.Boolean(default=False)

    # @api.onchange('fob_unit', 'quantity')
    def _compute_fob_amount(self):
        for rec in self:
            if rec.quantity:
                rec.fob_amount = rec.fob_unit * rec.quantity

    @api.onchange('fob_amount', 'freight_amount', 'insurance_amount', 'is_adjusted', 'cost_amount')
    def auto_update_fob(self):
        for rec in self:
            # rec.freight_unit = rec.freight_amount / rec.quantity if rec.freight_amount else rec.freight_unit
            # insurance_unit = rec.insurance_amount / rec.quantity
            # rec.fob_unit = rec.fob_amount / rec.quantity if rec.fob_amount else rec.fob_unit
            calculated_cif_amount = rec.fob_amount + rec.freight_amount + rec.insurance_amount
            if rec.is_adjusted and rec.cost_amount != calculated_cif_amount:

                new_fob = rec.cost_amount - (rec.freight_amount + rec.insurance_amount)
                if new_fob >= 0:
                    rec.fob_amount = max(new_fob, 0.0)
                    rec.freight_amount = rec.freight_amount
                    rec.insurance_amount = rec.insurance_amount
                    rec.cost_amount = rec.cost_amount
                else:
                    rec.fob_amount = rec.fob_unit * rec.quantity
                    rec.insurance_amount = rec.insurance_amount
                    rec.freight_amount = rec.freight_unit * rec.quantity
                    rec.cost_amount = rec.cost_unit * rec.quantity
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


    @api.depends('ref', 'quantity', 'date', 'vessel', 'voyage', 'expected_arrival_date', 'sob_date')
    def _compute_can_confirm(self):
        for rec in self:
            rec.can_confirm = all([
                rec.ref,
                rec.quantity,
                rec.date,
                rec.vessel,
                rec.voyage,
                rec.expected_arrival_date,
                rec.sob_date,
            ])


    @api.depends('insurance_amount', 'fob_amount', 'freight_amount')
    def _compute_can_change(self):
        for rec in self:
            rec.is_change = (
                    rec.insurance_amount != rec.old_insurance_amount
                    or rec.fob_amount != rec.old_fob_amount
                    or rec.freight_amount != rec.old_freight_amount
            )

    # @api.onchange('freight_unit', 'quantity')
    def _compute_freight_amount(self):
        for rec in self:
            rec.freight_amount = rec.freight_unit * rec.quantity


    @api.onchange('cost_unit', 'quantity')
    def _compute_cost_amount(self):
        for rec in self:
            rec.cost_amount = rec.cost_unit * rec.quantity


    def action_apply(self):
        self.ensure_one()
        self.is_click = True
        sale_invoice_id = self.sale_invoice_id
        sale_order_id = self.sale_order_id
        lead = self.lead_id

        if not sale_invoice_id and sale_order_id:
            raise UserError("No Saleorder/invoice found for this sale order.")

        if sale_invoice_id.state not in ['draft', 'posted']:
            raise UserError("Invoice must be in draft or posted state to update values.")

        # Get currencies
        currency_usd = self.env.ref('base.USD')
        currency_zar = self.env.ref('base.ZAR')

        # Update qty
        sale_invoice_id.qty_delivered = self.quantity
        lead.sudo().compute_sales_price()
        self.env.cr.commit()

        # Common values
        if self.quantity > 0:
            sales_price_unit = self.sale_invoice_id.cost_unit
        else:
            sales_price_unit = lead.agreed_sales_price_unit if lead.is_sales_price_override else lead.sales_price_unit
        # sales_price_unit = lead.agreed_sales_price_unit if lead.is_sales_price_override else lead.sales_price_unit
        sales_price = sales_price_unit * self.quantity
        exchange_rate = lead.indicative_exchange_rate or 1.0

        insurance_amount = self.insurance_amount
        interest_amount = lead.credit_cost_total
        freight_amount = self.freight_amount

        # Calculate FOB and procurement documentation
        if not lead.is_internal:
            pro_doc_amount = lead.sale_order_id.procurement_documentation_amount
            fob = sales_price - (insurance_amount + freight_amount)
        else:
            fob = self.fob_amount
            pro_doc_amount = sales_price - (
                    insurance_amount + freight_amount + interest_amount + sale_invoice_id.procurement_documentation_amount)
        # If invoice currency is ZAR → convert values
        if sale_invoice_id.currency_id == currency_zar:
            insurance_amount *= exchange_rate
            interest_amount *= exchange_rate
            freight_amount *= exchange_rate
            pro_doc_amount *= exchange_rate
            fob *= exchange_rate
            sales_price *= exchange_rate
            sales_price_unit *= exchange_rate

        # Set invoice values
        sale_invoice_id.insurance_amount = insurance_amount
        sale_invoice_id.interest_amount = interest_amount
        sale_invoice_id.freight_amount = freight_amount
        sale_invoice_id.cost_amount = sales_price_unit * self.quantity
        sale_invoice_id.cost_unit = sales_price_unit
        sale_invoice_id.fob_amount = fob
        sale_invoice_id.procurement_documentation_amount = pro_doc_amount

        # sale_order.write(new_vals)
        for line in sale_invoice_id.invoice_line_ids:
            line.quantity = self.quantity
            line.price_unit = sales_price_unit
        sale_invoice_id.message_post(
            body=_("Insurance, Freight and Fob values are updated from Supplier Commercial invoice."))


    def action_confirm(self):
        sale_invoice_id = self.sale_invoice_id
        if not self.lead_id:
            raise UserError(_("No trade folder found."))

        if not self.purchase_order_id:
            raise UserError(_("Please select a purchase order."))
        else:
            purchase = self.purchase_order_id

        _logger.info("=== Supplier Invoice Confirm Start ===")
        _logger.info("PO: %s | Existing Invoices: %s", purchase.name, len(purchase.invoice_ids))
        _logger.info("Ordered Qty: %s | Delivered Qty: %s", purchase.qty_total, purchase.qty_delivered)
        _logger.info("PO Units (FOB/MT: %s | Freight/MT: %s | Cost/MT: %s)",
                     purchase.fob_unit, purchase.freight_unit, purchase.cost_unit)
        _logger.info("Wizard Input → Qty: %s | FOB Unit: %s | Freight Unit: %s | Cost Unit: %s",
                     self.quantity, self.fob_unit, self.freight_unit, self.cost_unit)
        # Compute individual invoice amounts
        # self._compute_fob_amount()
        # self._compute_cost_amount()
        self.auto_update_fob()
        self._compute_freight_amount()
        _logger.info("Computed Amounts → FOB: %s | Freight: %s | Cost: %s",
                     self.fob_amount, self.freight_amount, self.cost_amount)
        # Prepare invoice values
        invoice_vals = {
            'ref': self.ref,
            'invoice_date': self.date,
            'vessel': self.vessel,
            'voyage': self.voyage,
            'expected_arrival_date': self.expected_arrival_date,
            'sob_date': self.sob_date,
            'fob_unit_po': self.fob_unit,
            'freight_unit_po': self.freight_unit,
            'cost_unit_po': self.cost_unit,
            'fob_amount_po': self.fob_unit * self.quantity,
            'freight_amount_po': self.freight_unit * self.quantity,
            'cost_amount_po': self.cost_unit * self.quantity,
            'insurance_amount_po': self.insurance_amount,
            # 'incoterm_id': purchase.incoterm_id.id,
        }

        # Create supplier invoice
        supplier_invoice = purchase.action_create_invoice()
        invoice = purchase.invoice_ids.sorted('create_date')[-1]
        _logger.info("Created Supplier Invoice: %s", invoice.name)
        _logger.info("Writing invoice values: %s", invoice_vals)
        invoice.write(invoice_vals)
        invoice.action_post()

        if len(invoice.invoice_line_ids) == 1:
            invoice.invoice_line_ids.price_unit = self.cost_unit
        _logger.info("Invoice Lines Updated: Quantity = %s, Unit Price = %s",
                     self.quantity, self.cost_unit)

        invoice.message_post(body=_("Supplier Commercial Invoice created successfully."))

        if purchase.invoice_ids:
            po_vals = {'fob_amount': self.fob_unit * purchase.qty_delivered,
                       'freight_amount': self.freight_unit * purchase.qty_delivered,
                       'cost_amount': self.cost_unit * purchase.qty_delivered,
                       'insurance_amount': self.insurance_amount,
                        }
            purchase.write(po_vals)

        _logger.info(
            "PO VALues%s",
            po_vals
        )
        # Update quantities and lock the purchase order
        purchase.set_product_qty()
        purchase._compute_freight_amount()
        purchase.is_close_readonly = True
        purchase.message_post(body=_("Supplier Commercial Invoice confirmed and totals updated successfully."))

