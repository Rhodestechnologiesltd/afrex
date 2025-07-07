# -*- coding: utf-8 -*-
# Part of Rhodes Technologies Ltd.

from odoo import models, fields, api
from odoo.exceptions import UserError


class Approval(models.Model):
    _name = 'asc.approval'
    _description = 'Approval Matrix'
    
    name = fields.Char("Description")
    payment_request_id = fields.Many2one('asc.payment.request', string="Payment Request")
    # profit_estimate_id = fields.Many2one('asc.profit.estimate', string="Profit Estimate")
    lead_id = fields.Many2one('crm.lead', string="Trade Folder")
    user_id = fields.Many2one('res.users', string="Approver", required=True)

    is_approved = fields.Boolean("Approved")
    approve_uid = fields.Many2one('res.users', string="Approved by")
    approve_date = fields.Datetime(string="Approved on")
    
    
    @api.model
    def create(self, vals):
        if 'payment_request_id' in vals:
            obj = "Approval for Payment Request"
        elif 'lead_id' in vals:
            obj = "Approval for Profit Estimate"
        else:
            obj = "Approval"
        vals['name'] = obj
        approval = super(Approval, self).create(vals)
        return approval
    
    def check_approver(self):
        self.ensure_one()
        for rec in self:
            if rec.user_id == self.env.user:
                return True
            else:
                return False
    
    def action_approve(self):
        self.ensure_one()
        check = self.check_approver()
        if not check:
            raise UserError("You are not allowed to approve.")
        self.write({
            'is_approved': True,
            'approve_uid': self.env.user.id,
            'approve_date': fields.Datetime.now(),
        })
        if self.payment_request_id:
            self.payment_request_id.check_approval()
            
    def action_reset(self):
        self.write({
            'is_approved': False,
            'approve_uid': False,
            'approve_date': False,
        })
