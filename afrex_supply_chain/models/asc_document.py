from odoo import models, fields, api, _


class Document(models.Model):
    _name = 'asc.document'
    _description = 'Shipping Document'

    name = fields.Char(string='Description')
    responsible = fields.Selection([('buyer', "Buyer"),
                                    ('supplier', "Supplier")], string="Responsible/Recipient")
    type_id = fields.Many2one('asc.document.type', string="Document Type", required=True)
    type = fields.Selection([('incoming', "Incoming"),
                            ('outgoing', "Outgoing")], string="Requirement Type")
    sequence = fields.Integer(string='Sequence')
    is_provided = fields.Boolean(string="Provided")
    document = fields.Binary(string="Document/Attachment")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',help="Upload attachments for preview",)

    lead_id = fields.Many2one('crm.lead')
    sale_order_id = fields.Many2one('sale.order')
    purchase_order_id = fields.Many2one('purchase.order')
    sale_invoice_id = fields.Many2one('account.move')
    
    def set_provided(self):
        for rec in self:
            rec.is_provided = True
            
    def set_to_provide(self):
        for rec in self:
            rec.is_provided = False

    def action_view_document(self):
        self.ensure_one()
        return {
            'name': _('Document'),
            'view_mode': 'form',
            'view_id': self.env.ref("afrex_supply_chain.asc_document_form_view").id,
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

class DocumentType(models.Model):
    _name = 'asc.document.type'
    _description = 'Shipping Document Type'
    
    name = fields.Char(string='Description')
    active = fields.Boolean(string='Active', default=True)
    