from num2words import num2words
from odoo import models, fields, api
import logging
from odoo.tools import float_round

_logger = logging.getLogger(__name__)

#    	_logger.debug("IT IS DEBUG")
#    	_logger.info("IT IS INFO")
#    	_logger.error("IT IS Error")
#    	_logger.warning("IT IS warn")
#    	_logger.critical("IT IS Critical")
        

class StampTaxAccountMove(models.Model):
    _inherit = 'account.move'

#    stamp_tax_sales_account = fields.Integer(compute='stamp_tax_verify',readonly='False')
#    stamp_tax_purchase_account = fields.Integer(compute='stamp_tax_verify',readonly='False')
#    stamp_tax_active = fields.Boolean(compute='stamp_tax_verify',default="False",readonly='False')
#    stamp_tax = fields.Monetary(string='Timbre Fiscal')
    
    stamp_tax_sales_account = fields.Integer()
    stamp_tax_purchase_account = fields.Integer()
    stamp_tax_active = fields.Boolean(default='True')
    stamp_tax = fields.Monetary(string='Timbre Fiscal',readonly='False')
    stamp_tax_signed = fields.Monetary()

                    
    @api.depends('name')
    def stamp_tax_verify(self):
        for rec in self:
            if rec.partner_id.stamp_tax_enable:
                rec.stamp_tax = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_amount')
                rec.stamp_tax_sales_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_sales_account')
                rec.stamp_tax_purchase_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_purchase_account')
                rec.stamp_tax_active = 'True'
            else:
                rec.stamp_tax = 0
                rec.stamp_tax_sales_account = 0
                rec.stamp_tax_purchase_account = 0
                rec.stamp_tax_active = 'False'
        return
    
    
    @api.depends(
        'line_ids.account_id',
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
            rec._recompute_universal_tax_lines()
            # rec.stamp_tax_update_universal()
            
            if rec.move_type in ['in_invoice','out_refund']:
            	sign = -1
            else:
            	sign = 1
            
            rec.stamp_tax_signed = rec.stamp_tax * sign
            rec.amount_total_signed = rec.amount_total * sign
            rec.amount_residual_signed = rec.amount_residual * sign                  
            
        return res

    
    def stamp_tax_calculate(self):

        for rec in self:
            
            stamp_enable = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_enable')
            stamp_amount = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_amount')
            stamp_sales_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_sales_account')
            stamp_purchase_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_purchase_account')
                
            if stamp_enable:
            
                rec.stamp_tax_sales_account = stamp_sales_account
                rec.stamp_tax_purchase_account = stamp_purchase_account
            
                type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
                
                if rec.move_type in type_list and self.partner_id.stamp_tax_enable:
                    rec.stamp_tax_active = 'True'
                    rec.stamp_tax = stamp_amount
                else:
                    rec.stamp_tax = 0.0
                    rec.stamp_tax_active = 'True'
                
                if rec.stamp_tax > 0:
                
                    rec.amount_total = rec.amount_total + rec.stamp_tax
                
                    total_residual = 0.0
                    
                    if rec.move_type == 'entry' or rec.is_outbound():
                        sign = 1
                    else:
                        sign = -1
                    
                    for line in rec.line_ids:
                        if rec.is_invoice(include_receipts=True):
                            if line.account_id.account_type in ('receivable', 'payable'):
                                total_residual += line.amount_residual
                                
                    rec.amount_residual = -sign * total_residual
                                    
            else:
            
                rec.stamp_tax = 0.0
                rec.stamp_tax_active = 'False'
           
    
    def stamp_tax_update_universal(self):

        for rec in self:
            
            already_exists = self.line_ids.filtered(
                lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            terms_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type in ('receivable', 'payable'))
            other_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type not in ('receivable', 'payable'))
            
            if already_exists and rec.stamp_tax > 0:
            
                amount = rec.stamp_tax
                
                if (rec.move_type == "out_invoice" or rec.move_type == "out_refund"):
                                    
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
                
                if (rec.move_type == "in_invoice" or rec.move_type == "in_refund"):
                    
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
                
            else:
                
                rec._recompute_universal_tax_lines()
                
        return 
    
    
    # @api.onchange
    @api.depends('stamp_tax', 'line_ids')
    def _recompute_universal_tax_lines(self):

        for rec in self:
            
            in_draft_mode = self != self._origin
                    
            type_list = ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']
            if rec.move_type in type_list and in_draft_mode:
                
                if rec.stamp_tax > 0:

                    stamp_sales_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_sales_account')
                    stamp_purchase_account = rec.env['ir.config_parameter'].sudo().get_param('stamp_tax_purchase_account')
                    
                    amount = self.stamp_tax
                        
                    line_name = "Timbre Fiscal"
                    line_name = line_name + " @ " + str(self.stamp_tax)
                    
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type in ('receivable', 'payable'))
                    
                    already_exists = self.line_ids.filtered(
                        lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
                    
                    if already_exists:
                        
                        if (self.move_type == "out_invoice" or self.move_type == "out_refund"):

                            if rec.move_type == "out_invoice":
                                already_exists.update({
                                    # 'account_id': stamp_sales_account,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            else:
                                already_exists.update({
                                    # 'account_id': stamp_sales_account,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            
                        if (self.move_type == "in_invoice" or self.move_type == "in_refund"):

                            if rec.move_type == "in_invoice":
                                already_exists.update({
                                    # 'account_id': stamp_purchase_account,
                                    'debit': amount > 0.0 and amount or 0.0,
                                    'credit': amount < 0.0 and -amount or 0.0,
                                })
                            else:
                                already_exists.update({
                                    # 'account_id': stamp_purchase_account,
                                    'debit': amount < 0.0 and -amount or 0.0,
                                    'credit': amount > 0.0 and amount or 0.0,
                                })
                            
                    else:
                        
                        new_tax_line = self.env['account.move.line']
                        create_method = self.env['account.move.line'].new or self.env['account.move.line'].create
                        
                        if (self.move_type == "out_invoice" or self.move_type == "out_refund"):

                            dict = {
                                'move_name': self.name,
                                'name': line_name,
                                'price_unit': self.stamp_tax,
                                'quantity': 1,
                                'debit': amount < 0.0 and -amount or 0.0,
                                'credit': amount > 0.0 and amount or 0.0,
                                'account_id': self.stamp_tax_sales_account,
                                'move_id': self._origin,
                                'date': self.date,
                                'display_type': 'tax',
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
                            
                        else:
                            
                            dict = {
                                'move_name': self.name,
                                'name': line_name,
                                'price_unit': self.stamp_tax,
                                'quantity': 1,
                                'debit': amount > 0.0 and amount or 0.0,
                                'credit': amount < 0.0 and -amount or 0.0,
                                'account_id': self.stamp_tax_purchase_account,
                                'move_id': self._origin,
                                'date': self.date,
                                'display_type': 'tax',
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
                 
                    
                    terms_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type in ('receivable', 'payable'))
                    
                    other_lines = self.line_ids.filtered(
                        lambda line: line.account_id.account_type not in ('receivable', 'payable'))
                        
                    total_balance = sum(other_lines.mapped('balance'))
                    total_amount_currency = sum(other_lines.mapped('amount_currency'))
                        
                    terms_lines.update({
                        'amount_currency': -total_amount_currency,
                        'debit': total_balance < 0.0 and -total_balance or 0.0,
                        'credit': total_balance > 0.0 and total_balance or 0.0,
                    })

                else:

                    already_exists = self.line_ids.filtered(
                        lambda line: line.name and line.name.find('Timbre Fiscal') == 0)
            
                    if already_exists:
                        
                        self.line_ids -= already_exists
                        
                        terms_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type in ('receivable', 'payable'))
                        other_lines = self.line_ids.filtered(
                            lambda line: line.account_id.account_type not in ('receivable', 'payable'))
                        
                        total_balance = sum(other_lines.mapped('balance'))
                        total_amount_currency = sum(other_lines.mapped('amount_currency'))

                        terms_lines.update({
                            'amount_currency': -total_amount_currency,
                            'debit': total_balance < 0.0 and -total_balance or 0.0,
                            'credit': total_balance > 0.0 and total_balance or 0.0,
                        })
        
        return
    
    
    # Convertir d'un montant en chiffres à un montant en lettres
                    
    @api.depends('amount_total')
    def amount_letter(self):

        z1 = int(self.amount_total)
        if self.currency_id.decimal_places==3:
            z2 = ('000'+str(int(self.amount_total*1000)))[-3:]
        else:
            z2 = ('00'+str(int(self.amount_total*100)))[-2:]

        amount = num2words(z1,lang='fr')
        curr_label = self.currency_id.currency_unit_label
        curr_decimals = self.currency_id.currency_subunit_label
        if z1 > 1:
            amount = amount + " "+curr_label+" "+z2+" "+curr_decimals+"."
        else:
            amount = amount + " "+curr_label+" "  +z2+" "+curr_decimals+"."

        return amount.upper()