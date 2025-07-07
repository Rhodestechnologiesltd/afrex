from odoo import models, fields, api, _


class Cost(models.Model):
    _name = 'asc.cost'
    _description = 'Costs and Charges'

    name = fields.Char(string='Description')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.purchase_order_id.currency_id or self.sale_order_id.currency_id)
    amount = fields.Float(string='Amount')

    lead_id = fields.Many2one('crm.lead')
    purchase_order_id = fields.Many2one('purchase.order')