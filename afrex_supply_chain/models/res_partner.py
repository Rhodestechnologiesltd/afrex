# -*- coding:utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_supplier = fields.Boolean("Is a Supplier")
    is_buyer = fields.Boolean("Is a Buyer")
    is_internal = fields.Boolean("Internal")
    address_text = fields.Text(string="Address to display")
    address_payment_request = fields.Text(string="Address on Payment Request")
    
    fax = fields.Char(string="Fax")
    
    sequence_id = fields.Many2one('ir.sequence', string="Trade Sequence")
    trade_count = fields.Integer(string="Trade Count", compute="_compute_trade_count", store=True)
    
    @api.depends('sequence_id.number_next_actual')
    def _compute_trade_count(self):
        for rec in self:
            if rec.sequence_id.number_next_actual > 0:
                rec.trade_count = rec.sequence_id.number_next_actual - 1
 
    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        name = vals['name']
        seq_vals = {
            'name': name + " - Trade Sequence",
            'code': name.lower().replace(" ", "_") + ".trade.sequence",
            'prefix': vals['ref'] if 'ref' in vals else None,
            'padding': 5,
            }
        seq = self.env['ir.sequence'].create(seq_vals)
        res.sequence_id = seq.id
        return res
    
    def write(self, vals):
        res = super().write(vals)
        if 'ref' in vals:
            for partner in self:
                partner.sequence_id.prefix = vals['ref']