# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class BankAccount(models.Model):
    _inherit = 'res.partner.bank'
    
    correspondent_bank_id = fields.Many2one('res.bank', string="Correspondent Bank")
    correspondent_bank_acc_num = fields.Char("Correspondent Bank Account Number")
    branch = fields.Char("Branch")
    ifsc = fields.Char("IFSC")
    chips_aba = fields.Char("CHIPS ABA No.")
    chips_uid = fields.Char("CHIPS UID No.")
    iban = fields.Char("IBAN", default=lambda self: self.acc_number)
    description = fields.Char("Description")