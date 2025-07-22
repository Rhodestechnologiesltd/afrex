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
    incoterm_id = fields.Many2one('account.incoterms', string='Incoterm', related="purchase_order_id.incoterm_id")
    breakbulk_container = fields.Selection(related="purchase_order_id.breakbulk_container", string='Breakbulk or Container')
    incoterm_selection = fields.Selection([('cfr', 'CFR'),
                                           ('cif', 'CIF'),
                                           ('fob', 'FOB'),
                                           ('dap', 'DAP'),
                                           ('fca', 'FCA'),
                                           ('exw', 'EXW')], compute="_compute_incoterm_selection")
    
    ref = fields.Char(string='Invoice Number', required=True)    
    quantity = fields.Float(string='Quantity (MT)')
    date = fields.Date(string='Invoice Date')
    
    vessel = fields.Char("Vessel Name", related="lead_id.vessel", readonly=False)
    voyage = fields.Char("Voyage", related="lead_id.voyage", readonly=False)
    expected_arrival_date = fields.Date("Estimated Arrival Date", related="lead_id.expected_arrival_date", readonly=False)
    sob_date = fields.Date("Shipped on Board Date", related="lead_id.sob_date", readonly=False)
    
    fob_unit = fields.Float("FOB/MT", digits="Prices per Unit", tracking=True)
    freight_unit = fields.Float("Freight/MT", digits="Prices per Unit", tracking=True)
    cost_unit = fields.Float("Cost/MT", digits="Prices per Unit", tracking=True)
    
    fob_amount = fields.Float("FOB", tracking=True)
    freight_amount = fields.Float("Freight", tracking=True)
    cost_amount = fields.Float("Cost", tracking=True)
    
    insurance_amount = fields.Float("Insurance", tracking=True)
    
    can_confirm = fields.Boolean(compute='_compute_can_confirm')

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
    
    @api.onchange('fob_unit','quantity')
    def _compute_fob_amount(self):
        for rec in self:
            rec.fob_amount = rec.fob_unit * rec.quantity
        
    # @api.onchange('freight_unit','freight_unit','quantity')
    def _compute_freight_amount(self):
        for rec in self:
            if rec.breakbulk_container == 'container':
                rec.freight_unit = rec.freight_amount / rec.quantity
            elif rec.breakbulk_container == 'breakbulk':
                rec.freight_amount = rec.freight_unit * rec.quantity
        
    @api.onchange('cost_unit','quantity')
    def _compute_cost_amount(self):
        for rec in self:
            rec.cost_amount = rec.cost_unit * rec.quantity
            
            
    def action_confirm(self):
        if not self.lead_id:
            raise UserError(_("No trade folder found."))
        
        if not self.purchase_order_id:
            raise UserError(_("Please select a purchase order."))
        else:
            purchase = self.purchase_order_id

        self._compute_fob_amount()
        self._compute_freight_amount()
        self._compute_cost_amount()

        invoice_vals = {
            'ref': self.ref,
            'invoice_date': self.date,
            'vessel': self.vessel,
            'voyage': self.voyage,
            'expected_arrival_date': self.expected_arrival_date,
            'sob_date': self.sob_date,
            'fob_unit': self.fob_unit,
            'freight_unit': self.freight_unit,
            'cost_unit': self.cost_unit,
            'fob_amount': self.fob_amount,
            'freight_amount': self.freight_amount,
            'cost_amount': self.cost_amount,
            'insurance_amount': self.insurance_amount,
        }
        
        
        supplier_invoice = purchase.action_create_invoice()
        
        invoice = purchase.invoice_ids.sorted('create_date')[-1]
        invoice.write(invoice_vals)
        for line in invoice.invoice_line_ids:
            line.write({
                'price_unit': self.cost_unit,
            })
        invoice.message_post(body=_("Supplier Commercial Invoice created successfully."))
        # invoice.action_post()
        
        if purchase.invoice_ids:
            total_fob = 0
            total_freight = 0
            total_cost = 0
            for supplier_invoice in purchase.invoice_ids:
                total_fob += supplier_invoice.fob_amount
                total_freight += supplier_invoice.freight_amount
                total_cost += supplier_invoice.cost_amount
            costing_vals = {
                'fob_unit': total_fob / purchase.qty_delivered,
                'freight_unit': total_freight / purchase.qty_delivered,
                'cost_unit': total_cost / purchase.qty_delivered,
                'freight_amount': total_freight,
            }
            purchase.write(costing_vals)
        purchase.set_product_qty()
        purchase.message_post(body=_("Invoice created successfully."))
        # afrex_invoices = self.env['account.move'].search([('lead_id', '=', self.lead_id.id), ('move_type', '=', 'out_invoice')])
        # if len(afrex_invoices) == 1:
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'res_model': 'account.move',
        #         'view_mode': 'form',
        #         'res_id': afrex_invoices.id,
        #         'target': 'current',
        #     }
        # else:
        #     return {
        #         'type': 'ir.actions.act_window',
        #         'res_model': 'account.move',
        #         'view_mode': 'tree,form',
        #         'domain': [('lead_id', '=', self.lead_id.id), ('move_type', '=', 'out_invoice')],
        #         'target': 'current',
        #     }
            