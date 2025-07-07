from odoo import models, fields, api, _


class ProductCombination(models.Model):
    _name = 'asc.product.combination'
    _description = 'Product Combination'

    name = fields.Char("Product Description", readonly=True)
    product_id = fields.Many2one('product.template', string="Product", ondelete='restrict', required=True)
    product_variant_id = fields.Many2one('product.product', related='product_id.product_variant_id', string="Product Variant")
    
    first_spec_id = fields.Many2one('asc.product.specification', "Specification 1", ondelete='restrict', required=True)
    second_spec_id = fields.Many2one('asc.product.specification', "Specification 2", ondelete='restrict', required=True)
    third_spec_id = fields.Many2one('asc.product.specification', "Specification 3", ondelete='restrict', required=True)
    
    packaging_id = fields.Many2one('asc.product.packaging', string="Packaging", ondelete='restrict', required=True)
    
    cas_number = fields.Char("CAS")
    
    description = fields.Char("Specification", compute="_compute_description", store=True)
    supplier_ids = fields.Many2many('res.partner', string="Suppliers")
    
    origin = fields.Char("Origin")
        
    @api.depends('product_id', 'first_spec_id', 'first_spec_id.name', 'second_spec_id', 'second_spec_id.name', 'third_spec_id', 'third_spec_id.name', 'packaging_id')
    def _compute_description(self):
        for rec in self:
            temp_name = ""
            if rec.first_spec_id.name != "NA":
                temp_name += str(rec.first_spec_id.name) + " "
            if rec.second_spec_id.name != "NA":
                temp_name += str(rec.second_spec_id.name) + " "
            if rec.third_spec_id.name != "NA":
                temp_name += str(rec.third_spec_id.name)
            temp_name_clean = temp_name.strip()
            rec.description = temp_name_clean
            rec.name = str(rec.product_id.name) + " " + temp_name_clean