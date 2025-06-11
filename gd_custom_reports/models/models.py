# -*- coding: utf-8 -*-

from odoo import models, fields, api
import num2words

from odoo import models




class AccountMove(models.Model):
    _inherit = 'account.move'

    def num2words_function(self, amount):
        return num2words.num2words(amount).capitalize()

    def get_amount_in_words(self, amount):
        for rec in self:
            text = rec.currency_id.amount_to_text(amount)
            return text.title()


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @property
    def print_report_name(self):
        for rec in self:
            if rec.journal_id.type == 'cash' and rec.payment_type == 'outbound':
                return 'Cash Payment Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'bank' and rec.payment_type == 'outbound':
                return 'Bank Payment Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'cash' and rec.payment_type == 'inbound':
                return 'Cash Receipt Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'bank' and rec.payment_type == 'inbound':
                return 'Bank Receipt Voucher - %s' % (rec.name)
            return 'Voucher - %s' % (rec.name)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def compute_analytic_distribution_formatted(self):
        if self.analytic_distribution:
            distribution = []
            for key, value in self.analytic_distribution.items():
                plan = self.env['account.analytic.account'].browse(int(key))
                if plan:
                    distribution.append(f"{plan.name}:{value}%")
            return distribution
        else:
            return ""



