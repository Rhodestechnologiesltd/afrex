from odoo import models, fields, api, _


class ShippingLine(models.Model):
    _name = 'asc.shipping.line'
    _description = 'Shipping Line'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)




