# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class Bank(models.Model):
    _inherit = 'res.bank'
    
    address_text = fields.Text("Address to display")
    fedwire = fields.Char("Fedwire ABA No.")