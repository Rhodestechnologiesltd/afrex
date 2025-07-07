# -*- coding:utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    tariff_code = fields.Char(string="Tariff Code")
    
    combination_ids = fields.One2many('asc.product.combination', 'product_id')
    supplier_ids = fields.Many2many('res.partner', string="Suppliers")