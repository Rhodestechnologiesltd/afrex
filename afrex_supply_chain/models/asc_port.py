from odoo import models, fields, api, _


class Port(models.Model):
    _name = 'asc.port'
    _description = 'Ports'

    name = fields.Char(string='Name')
    type = fields.Selection([('sea', 'Maritime'),
                             ('road', 'Road'),
                             ('air', 'Air')], string='Type', default='sea', required=True)
    city = fields.Char(string='City/Locality')
    country_id = fields.Many2one('res.country', string='Country')
    active = fields.Boolean(string='Active', default=True)
