from odoo import models, fields, api, _


class BankingFee(models.Model):
    _name = 'asc.banking.fee'
    _description = 'Banking Fee'

    name = fields.Char(string='Banking Fee', required=True, default="Banking Fee ")
    lead_id = fields.Many2one('crm.lead')
    amount = fields.Float(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)