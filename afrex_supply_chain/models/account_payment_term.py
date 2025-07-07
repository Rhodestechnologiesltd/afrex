# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'
    
    breakdown_ids = fields.One2many('asc.payment.term.line', 'payment_id', string="Payment Breakdown")


class PaymentTermLine(models.Model):
    _name = 'asc.payment.term.line'
    _description = 'Payment Terms Breakdown'
    
    name = fields.Char("Description")
    percentage = fields.Float("Percentage")
    payment_type = fields.Selection([('advance', "Advance"),
                              ('final', "Final"),],
                             string="Payment Type")
    payment_id = fields.Many2one('account.payment.term', string="Payment")
    
