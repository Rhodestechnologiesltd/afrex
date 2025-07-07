from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SetDocumentWizard(models.TransientModel):
    _name = 'asc.set.document'
    _description = 'Set list of documents to be provided'
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)

    purchase_order_id = fields.Many2one('purchase.order')
    sale_invoice_id = fields.Many2one('account.move')
    lead_id = fields.Many2one('crm.lead')
    
    responsible = fields.Selection([('buyer', "Buyer"),
                                    ('supplier', "Supplier")], string="Responsible/Recipient")
    type = fields.Selection([('incoming', "Incoming"),
                            ('outgoing', "Outgoing")], string="Requirement Type")
    doc_type_ids = fields.Many2many('asc.document.type', string="Documents to be provided", domain="[('id', 'not in', existing_doc_type_ids)]", readonly=False)

    # ex_doc_type_ids = fields.Many2many('asc.document.type', string="Default Documents", domain="[('id', 'in', existing_doc_type_ids)]", readonly=False)

    existing_doc_type_ids = fields.Many2many(
        'asc.document.type',
        compute="_compute_existing_doc_type_ids",
        store=False
    )
    
    @api.depends('type','purchase_order_id','sale_invoice_id')
    def _compute_existing_doc_type_ids(self):
        purchase = self.purchase_order_id
        invoice = self.sale_invoice_id
        if purchase:
            if self.type == 'incoming':
                existing_types = purchase.incoming_doc_ids.mapped('type_id').ids
            elif self.type == 'outgoing':
                existing_types = purchase.outgoing_doc_ids.mapped('type_id').ids
            else:
                existing_types = self.env['asc.document.type'].browse([])
            self.existing_doc_type_ids = existing_types
        if invoice:
            if self.type == 'incoming':
                existing_types = invoice.incoming_doc_ids.mapped('type_id').ids
            elif self.type == 'outgoing':
                existing_types = invoice.outgoing_doc_ids.mapped('type_id').ids
            else:
                existing_types = self.env['asc.document.type'].browse([])
            self.existing_doc_type_ids = existing_types
                
    def set_document(self):
        purchase = self.purchase_order_id
        invoice = self.sale_invoice_id
        documents = self.env['asc.document']
        if purchase:
            for doc_type in self.doc_type_ids:
                doc_vals = {
                    'name': doc_type.name,
                    'type_id': doc_type.id,
                    'type': self.type,
                    'responsible': self.responsible,
                    'purchase_order_id': purchase.id,
                    'lead_id': self.lead_id.id,
                }
                documents.create(doc_vals)
        if invoice:
            for doc_type in self.doc_type_ids:
                doc_vals = {
                    'name': doc_type.name,
                    'type_id': doc_type.id,
                    'type': self.type,
                    'responsible': self.responsible,
                    'sale_invoice_id': invoice.id,
                    'lead_id': self.lead_id.id,
                }
                documents.create(doc_vals)
                