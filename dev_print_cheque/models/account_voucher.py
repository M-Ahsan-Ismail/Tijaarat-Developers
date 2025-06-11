# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields, api
from odoo import tools
from num2words import num2words


class account_voucher(models.Model):
    _inherit = 'account.payment'

    payment_method_name = fields.Char(related='payment_method_line_id.name')
    # cheque_formate_id = fields.Many2one('cheque.setting', 'Cheque Formate')
    cheque_no = fields.Char('Cheque No')
    # text_free = fields.Char('Free Text')
    partner_text = fields.Char('Partner Title')
    is_ac_pay = fields.Boolean('Is A/C Pay')
    custom_partner_title = fields.Boolean('Custom Partner Title')
    journal_id_type = fields.Selection(related='journal_id.type')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(cheque_no)', 'The "Cheque No" must be unique.'),
    ]

    def get_date(self, date):
        date = str(date).split('-')
        return date

    def get_partner_name(self, obj, p_text):
        if p_text and obj.partner_text:
            if p_text == 'prefix':
                return obj.partner_text + ' ' + obj.partner_id.name
            else:
                return obj.partner_id.name + ' ' + obj.partner_text

        return obj.partner_id.name

    def amount_word(self, obj):
        amt_word = num2words(obj.amount)
        return amt_word


class AccountRegisterPayment(models.TransientModel):
    _name = "account.payment.register"
    _inherit = ["account.payment.register", "analytic.mixin"]
    cheque_no = fields.Char('Cheque No')
    journal_id_type = fields.Selection(related='journal_id.type')

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['cheque_no'] = self.cheque_no
        return res
