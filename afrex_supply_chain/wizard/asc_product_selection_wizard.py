from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductSelectionWizard(models.TransientModel):
    _name = 'asc.product.selection'
    _description = 'Product Selection Wizard'

    lead_id = fields.Many2one('crm.lead')
    can_confirm = fields.Boolean(compute='_compute_can_confirm')

    product_id = fields.Many2one('product.template', string="Product")
    product_variant_id = fields.Many2one('product.product', related='product_id.product_variant_id', string="Product Variant")
    
    first_spec_id = fields.Many2one('asc.product.specification', "Specification 1")
    second_spec_id = fields.Many2one('asc.product.specification', "Specification 2")
    third_spec_id = fields.Many2one('asc.product.specification', "Specification 3")
    
    packaging_id = fields.Many2one('asc.product.packaging', string="Packaging")
    
    product_qty = fields.Float(string="Quantity (MT)")
    
    product_combination_ids = fields.Many2many('asc.product.combination', string="Available Product Combinations", store=False)
    product_combination_id = fields.Many2one('asc.product.combination', string="Select Product", store=False)

    @api.onchange('product_combination_id')
    def action_use_selected_combination(self):
        for rec in self:
            if rec.product_combination_id:
                combination = rec.product_combination_id
                rec.product_id = combination.product_id.id
                rec.first_spec_id = combination.first_spec_id.id
                rec.second_spec_id = combination.second_spec_id.id
                rec.third_spec_id = combination.third_spec_id.id
                rec.packaging_id = combination.packaging_id.id

    @api.onchange('product_id', 'first_spec_id', 'second_spec_id', 'third_spec_id', 'packaging_id')
    def _onchange_update_combinations(self):
        for rec in self:
            domain = [('product_id', '=', rec.product_id.id)]

            if rec.first_spec_id:
                domain.append(('first_spec_id', '=', rec.first_spec_id.id))
            if rec.second_spec_id:
                domain.append(('second_spec_id', '=', rec.second_spec_id.id))
            if rec.third_spec_id:
                domain.append(('third_spec_id', '=', rec.third_spec_id.id))
            if rec.packaging_id:
                domain.append(('packaging_id', '=', rec.packaging_id.id))

            rec.product_combination_ids = rec.env['asc.product.combination'].search(domain)
                
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
            
    def action_clear(self):
        self.first_spec_id = False
        self.second_spec_id = False
        self.third_spec_id = False
        self.packaging_id = False
        
        combos = self.env['asc.product.combination'].search([
            ('product_id', '=', self.product_id.id)
        ]) if self.product_id else self.env['asc.product.combination']

        default_context = {
            'default_product_id': self.product_id.id if self.product_id else False,
            'default_product_combination_ids': [(6, 0, combos.ids)],
        }
                
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asc.product.selection',
            'res_id': self.id,
            'target': 'new',
            'context': default_context,
        }
    
    def return_product_combination(self):
        combinations = self.env['asc.product.combination']
        combination = combinations.search([('product_id', '=', self.product_id.id), ('first_spec_id', '=', self.first_spec_id.id), ('second_spec_id', '=', self.second_spec_id.id), ('third_spec_id', '=', self.third_spec_id.id), ('packaging_id', '=', self.packaging_id.id)], limit=1)
        if not combination:
            raise UserError("No product with this combination found!")
        else:
            self.lead_id.product_combination_id = combination.id
            self.lead_id.is_product_selected = True
        if self.lead_id:
            self.lead_id.product_qty = self.product_qty
        return {
            'res_id': self.lead_id.id,
            'res_model': 'crm.lead',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {},
            'target': 'current'
        }
        