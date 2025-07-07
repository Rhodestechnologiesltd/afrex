from odoo import api, fields, models
from datetime import date


class CrmProductLine(models.Model):
    _name = 'crm.product.line'
    _description = "Lead Product Line"

    lead_id = fields.Many2one('crm.lead')
    product_id = fields.Many2one('product.product', string="Product")
    
    supplier_ids = fields.Many2many('res.partner', string="Suppliers", related="product_id.supplier_ids")
    
    qty = fields.Float(string="Quantity")
    price_unit = fields.Float(string="Unit Price", related="product_id.standard_price")
    
    # product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')  
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    # ,domain="[('category_id', '=', product_uom_category_id)]"
