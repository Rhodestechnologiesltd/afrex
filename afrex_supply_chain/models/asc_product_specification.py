from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductSpecification(models.Model):
    _name = 'asc.product.specification'
    _description = 'Product Specification'

    name = fields.Char(string='Specification')
    level = fields.Selection([('spec1', "Spec 1"),
                              ('spec2', "Spec 2"),
                              ('spec3', "Spec 3")])
    active = fields.Boolean(string='Active', default=True)
    
    # @api.constrains('name')
    # def _check_name_unique_case_insensitive(self):
    #     for record in self:
    #         if not record.name:
    #             continue

    #         # Perform case-insensitive search, excluding self (for updates)
    #         duplicate = self.search([
    #             ('id', '!=', record.id),
    #             ('name', '=ilike', record.name.strip())
    #         ], limit=1)

    #         if duplicate:
    #             creator = duplicate.create_uid.name if duplicate.create_uid else "Unknown"
    #             if duplicate.create_date:
    #                 created_on = duplicate.create_date.strftime('%Y-%m-%d %H:%M:%S')
    #             else:
    #                 created_on = "Unknown time"
    #             raise ValidationError(
    #                 f"A specification with the name '{duplicate.name}' already exists.\n\n"
    #                 f"🧾 Created by: {creator}\n"
    #                 f"🕒 On: {created_on}"
    #             )

