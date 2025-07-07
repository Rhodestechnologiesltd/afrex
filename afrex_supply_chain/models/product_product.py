# -*- coding:utf-8 -*-

from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'
    
    supplier_ids = fields.Many2many('res.partner', string="Suppliers")