from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UpdatePackagingWizard(models.TransientModel):
    _name = 'asc.update.packaging'
    _description = 'Update Packaging Wizard'

    purchase_order_id = fields.Many2one('purchase.order')
    lead_id = fields.Many2one('crm.lead')

    product_id = fields.Many2one('product.template', string="Product", required=True)
    product_variant_id = fields.Many2one('product.product', related='product_id.product_variant_id', string="Product Variant")
    
    first_spec_id = fields.Many2one('asc.product.specification', "Specification 1", required=True)
    second_spec_id = fields.Many2one('asc.product.specification', "Specification 2", required=True)
    third_spec_id = fields.Many2one('asc.product.specification', "Specification 3", required=True)
    
    packaging_id = fields.Many2one('asc.product.packaging', string="Packaging", required=True)
    
    can_confirm = fields.Boolean(compute='_compute_can_confirm')
    
    @api.depends('product_id', 'first_spec_id', 'second_spec_id', 'third_spec_id', 'packaging_id')
    def _compute_can_confirm(self):
        for rec in self:
            rec.can_confirm = all([
                rec.product_id,
                rec.first_spec_id,
                rec.second_spec_id,
                rec.third_spec_id,
                rec.packaging_id,
            ])
    
    def action_confirm(self):
        order = self.purchase_order_id
        lead = self.lead_id
        if not order or not lead:
            raise UserError("No purchase order or trade folder found!")
        combinations = self.env['asc.product.combination']
        combination = combinations.search([('product_id', '=', self.product_id.id), ('first_spec_id', '=', self.first_spec_id.id), ('second_spec_id', '=', self.second_spec_id.id), ('third_spec_id', '=', self.third_spec_id.id), ('packaging_id', '=', self.packaging_id.id)], limit=1)
        if not combination:
            combination_vals = {
                'product_id': self.product_id.id,
                'first_spec_id': self.first_spec_id.id,
                'second_spec_id': self.second_spec_id.id,
                'third_spec_id': self.third_spec_id.id,
                'packaging_id': self.packaging_id.id,
            }
            combination = combinations.create(combination_vals)
        if combination:
            order.product_combination_id = combination.id
            lead.product_combination_id = combination.id
            for line in order.order_line:
                line.product_combination_id = combination.id
                line.product_id = combination.product_id.product_variant_id.id