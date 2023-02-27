from num2words import num2words
from odoo import models, fields, api


class StampTaxAccountMove(models.Model):
    _inherit = 'account.move'

    stamp_tax_sales_account = fields.Integer(compute='stamp_tax_verify')
    stamp_tax_purchase_account = fields.Integer(compute='stamp_tax_verify')
    stamp_tax = fields.Monetary(string='Timbre Fiscal')
                                # , readonly='False',
                                # compute='_compute_amount',
                                # track_visibility='always')
                                # , store=True)

                    
    @api.depends('name')
    def stamp_tax_verify(self):
        for rec in self:
            if rec.partner_id.stamp_tax_enable:
                rec.stamp_tax = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_amount')
                rec.stamp_tax_sales_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_sales_account')
                rec.stamp_tax_purchase_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_purchase_account')
            else:
                rec.stamp_tax = 0
                rec.stamp_tax_sales_account = 0
                rec.stamp_tax_purchase_account = 0
                
                
    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'stamp_tax',
        'partner_id')
    def _compute_amount(self):
        for rec in self:
            res = super(StampTaxAccountMove, rec)._compute_amount()
            rec.stamp_tax_calculate()
            rec.stamp_tax_update_universal()
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_signed = rec.amount_total * sign
        return res

    def stamp_tax_calculate(self):

        for rec in self:

            stamp_enable = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_enable')
            stamp_amount = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_amount')

            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if True:
                if stamp_enable:
                    if self.partner_id.stamp_tax_enable and rec.move_type in type_list:
                        rec.stamp_tax = stamp_amount
                    else:
                        rec.stamp_tax = 0.0
                    rec.amount_total = rec.stamp_tax + rec.amount_total
                else:
                    rec.stamp_tax = 0.0

    def stamp_tax_update_universal(self):
        for rec in self:
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type.type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type.type not in ('receivable', 'payable'))
            if already_exists:
                amount = rec.stamp_tax
                if rec.stamp_tax_sales_account \
                        and (rec.move_type == "out_invoice"
                             or rec.move_type == "out_refund") \
                        and rec.stamp_tax > 0:
                    if rec.move_type == "out_invoice":
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                if rec.stamp_tax_purchase_account \
                        and (rec.move_type == "in_invoice"
                             or rec.move_type == "in_refund") \
                        and rec.stamp_tax > 0:
                    if rec.move_type == "in_invoice":
                        already_exists.update({
                            'debit': amount > 0.0 and amount or 0.0,
                            'credit': amount < 0.0 and -amount or 0.0,
                        })
                    else:
                        already_exists.update({
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        })
                total_balance = sum(other_lines.mapped('balance'))
                total_amount_currency = sum(other_lines.mapped('amount_currency'))
                terms_lines.update({
                    'amount_currency': -total_amount_currency,
                    'debit': total_balance < 0.0 and -total_balance or 0.0,
                    'credit': total_balance > 0.0 and total_balance or 0.0,
                })
            if not already_exists and rec.stamp_tax > 0:
                in_draft_mode = self != self._origin
                if not in_draft_mode:
                    rec._recompute_universal_tax_lines()
                print()

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        res = super(StampTaxAccountMove, self)._prepare_refund(invoice, date_invoice=None, date=None,
                                                               description=None, journal_id=None)
        print(res)
        return res

    @api.onchange('stamp_tax', 'line_ids')
    def _recompute_universal_tax_lines(self):
        for rec in self:
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.stamp_tax > 0 and rec.move_type in type_list:
                if rec.is_invoice(include_receipts=True):
                    in_draft_mode = self != self._origin
                    line_name = "Timbre Fiscal"
                    line_name = line_name + \
                                " @ " + str(self.stamp_tax)
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type.type in ('receivable', 'payable'))
                    already_exists = self.line_ids.filtered(
                        lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                    if already_exists:
                        amount = self.stamp_tax
                        if self.stamp_tax_sales_account \
                                and (self.move_type == "out_invoice"
                                     or self.move_type == "out_refund"):
                            already_exists.update({
                                'name': line_name,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                            })
                        if self.stamp_tax_purchase_account \
                                and (self.move_type == "in_invoice"
                                     or self.move_type == "in_refund"):
                            already_exists.update({
                                'name': line_name,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                            })
                    else:
                        new_tax_line = self.env['account.move.line']
                        create_method = in_draft_mode and \
                                        self.env['account.move.line'].new or \
                                        self.env['account.move.line'].create

                        if self.stamp_tax_sales_account \
                                and (self.move_type == "out_invoice"
                                     or self.move_type == "out_refund"):
                            amount = self.stamp_tax
                            dict = {
                                'move_name': self.name,
                                'name': line_name,
                                'price_unit': self.stamp_tax,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': int(self.stamp_tax_purchase_account),
                                'move_id': self._origin,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }
                            if self.move_type == "out_invoice":
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            if in_draft_mode:
                                self.line_ids += create_method(dict)
                                # Updation of Invoice Line Id
                                duplicate_id = self.invoice_line_ids.filtered(
                                    lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                                self.invoice_line_ids = self.invoice_line_ids - duplicate_id
                            else:
                                dict.update({
                                    'price_unit': 0.0,
                                    'debit': 0.0,
                                    'credit': 0.0,
                                })
                                self.line_ids = [(0, 0, dict)]

                        if self.stamp_tax_purchase_account \
                                and (self.move_type == "in_invoice"
                                     or self.move_type == "in_refund"):
                            amount = self.stamp_tax
                            dict = {
                                'move_name': self.name,
                                'name': line_name,
                                'price_unit': self.stamp_tax,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': int(self.stamp_tax_sales_account),
                                'move_id': self.id,
                                'date': self.date,
                                'exclude_from_invoice_tab': True,
                                'partner_id': terms_lines.partner_id.id,
                                'company_id': terms_lines.company_id.id,
                                'company_currency_id': terms_lines.company_currency_id.id,
                            }

                            if self.move_type == "in_invoice":
                                dict.update({
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                dict.update({
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            self.line_ids += create_method(dict)

                            # updation of invoice line id

                            duplicate_id = self.invoice_line_ids.filtered(
                                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                            self.invoice_line_ids = self.invoice_line_ids - duplicate_id

                    if in_draft_mode:

                        # Update the payement account amount

                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type.type not in ('receivable', 'payable'))
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        terms_lines.update({
                            'amount_currency': -total_amount_currency,
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        })
                    else:
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type.type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type.type not in ('receivable', 'payable'))
                        already_exists = self.line_ids.filtered(
                            lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                        total_balance = sum(other_lines.mapped('balance')) - amount
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        dict1 = {
                            'debit': amount < 0.0 and -amount or 0.0,
                            'credit': amount > 0.0 and amount or 0.0,
                        }
                        dict2 = {
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        }
                        self.line_ids = [(1, already_exists.id, dict1), (1, terms_lines.id, dict2)]
                        print()

            elif self.stamp_tax <= 0:
                already_exists = self.line_ids.filtered(
                    lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                if already_exists:
                    self.line_ids -= already_exists
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type.type in ('receivable', 'payable'))
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type.type not in ('receivable', 'payable'))
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })


                    
    @api.depends('amount_total')
    def amount_letter(self):
        z1 = int(self.amount_total)
        z3 = (self.amount_total - z1) * 1000
        z2 = str(int(z3))
        amount = num2words(z1,lang='fr')
        if z1 > 1:
            amount = amount + " Dinars "
        else:
            amount = amount + " Dinar "
        amount = amount + " " +z2+" Millimes"
        return amount.upper()
