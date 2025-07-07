from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductPackaging(models.Model):
    _name = 'asc.product.packaging'
    _description = 'Product Packaging'

    name = fields.Char(string='Packaging')
    active = fields.Boolean(string='Active', default=True)
    
    @api.constrains('name')
    def _check_name_unique_case_insensitive(self):
        for record in self:
            if not record.name:
                continue

            # Perform case-insensitive search, excluding self (for updates)
            duplicate = self.search([
                ('id', '!=', record.id),
                ('name', '=ilike', record.name.strip())
            ], limit=1)

            if duplicate:
                creator = duplicate.create_uid.name if duplicate.create_uid else "Unknown"
                if duplicate.create_date:
                    created_on = duplicate.create_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    created_on = "Unknown time"
                raise ValidationError(
                    f"A packaging with the name '{duplicate.name}' already exists.\n\n"
                    f"🧾 Created by: {creator}\n"
                    f"🕒 On: {created_on}"
                )




