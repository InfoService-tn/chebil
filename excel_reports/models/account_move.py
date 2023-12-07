# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import io
import json
import xlsxwriter
from odoo import models
from odoo.tools import date_utils

class AccountMove(models.Model):
    """ Added function for printing excel report
            which is coming from a server action """
    _inherit = "account.move"

    def print_excel_report(self):
        """ Function is used to print the Excel report
            It will pass the invoice data through js file to
            print Excel file"""
        # Take the ids of the selected invoices
        data = self._context['active_ids']
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'data': {'model': 'account.move',
                     'output_format': 'xlsx',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'report_name': 'Invoice Excel Report', }, }

    def get_xlsx_report(self, datas, response):
        """ From this function we can create and design the Excel file template
         and the map the values in the corresponding cells
         :param datas: Selected record ids
         :param response: Response after creating excel
         """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(
                'Rapport des ventes' )  # Set sheet name as Invoice/Bill name
        
        # workbook = xlwt.Workbook()
        amount_tot = 0
        column_heading_style = easyxf('font:height 200;font:bold True;')
        worksheet = workbook.add_sheet('Invoice Summary')
        worksheet.write(2, 3, self.env.user.company_id.name, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 2, new_from_date, easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 3, 'To',easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(4, 4, new_to_date,easyxf('font:height 200;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, _('Invoice Number'), column_heading_style) 
        worksheet.write(6, 1, _('Customer'), column_heading_style)
        worksheet.write(6, 2, _('Invoice Date'), column_heading_style)
        worksheet.write(6, 3, _('Invoice Amount'), column_heading_style)
        worksheet.write(6, 4, _('Invoice Currency'), column_heading_style)
        worksheet.write(6, 5, _('Amount in Company Currency (' + str(self.env.user.company_id.currency_id.name) + ')'), column_heading_style)
        
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 8000
        
        worksheet2 = workbook.add_sheet('Customer wise Invoice Summary')
        worksheet2.write(1, 0, _('Customer'), column_heading_style)
        worksheet2.write(1, 1, _('Paid Amount'), column_heading_style)
        worksheet2.write(1, 2, _('Invoice Currency'), easyxf('font:height 200;font:bold True;align: horiz left;'))
        worksheet2.write(1, 3, _('Amount in Company Currency (' + str(self.env.user.company_id.currency_id.name) + ')'), easyxf('font:height 200;font:bold True;align: horiz left;'))
        worksheet2.col(0).width = 5000
        worksheet2.col(1).width = 5000
        worksheet2.col(2).width = 4000
        worksheet2.col(3).width = 8000
        
        row = 7
        customer_row = 2
        for wizard in self:
            customer_payment_data = {}
            heading =  'Invoice Summary Report'
            worksheet.write_merge(0, 0, 0, 5, heading, easyxf('font:height 210; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            heading =  'Customer wise Invoice Summary'
            worksheet2.write_merge(0, 0, 0, 3, heading, easyxf('font:height 200; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            if wizard.invoice_status == 'all':
                invoice_objs = self.env['account.invoice'].search([('date_invoice','>=',wizard.from_date),
                                                               ('date_invoice','<=',wizard.to_date),
                                                               ('type','=','out_invoice'),
                                                               ('state','not in',['draft','cancel'])])
            elif wizard.invoice_status == 'paid':
                invoice_objs = self.env['account.invoice'].search([('date_invoice','>=',wizard.from_date),
                                                               ('date_invoice','<=',wizard.to_date),
                                                               ('state','=','paid'),('type','=','out_invoice')])
            else:
                invoice_objs = self.env['account.invoice'].search([('date_invoice','>=',wizard.from_date),
                                                               ('date_invoice','<=',wizard.to_date),
                                                               ('state','=','open'),('type','=','out_invoice')])
            for invoice in invoice_objs:
                invoice_date = invoice.date_invoice.strftime('%Y-%m-%d')
                amount = 0
                for journal_item in invoice.move_id.line_ids: 
                    amount += journal_item.debit
                worksheet.write(row, 0, invoice.number)
                worksheet.write(row, 1, invoice.partner_id.name)
                worksheet.write(row, 2, invoice_date)
                worksheet.write(row, 3, invoice.amount_total)
                worksheet.write(row, 4, invoice.currency_id.symbol)
                worksheet.write(row, 5, amount)
                amount_tot += amount
                row += 1
                key = u'_'.join((invoice.partner_id.name, invoice.currency_id.name)).encode('utf-8')
                key =  str(key,'utf-8')
                if key not in customer_payment_data:
                    customer_payment_data.update({key: {'amount_total': invoice.amount_total, 'amount_company_currency': amount}})
                else:
                    paid_amount_data = customer_payment_data[key]['amount_total'] + invoice.amount_total
                    amount_currency = customer_payment_data[key]['amount_company_currency'] + amount
                    customer_payment_data.update({key: {'amount_total': paid_amount_data, 'amount_company_currency': amount_currency}})
            worksheet.write(row+2, 5, amount_tot, column_heading_style)
              
            for customer in customer_payment_data:
                worksheet2.write(customer_row, 0, customer.split('_')[0])
                worksheet2.write(customer_row, 1, customer_payment_data[customer]['amount_total'])
                worksheet2.write(customer_row, 2, customer.split('_')[1])
                worksheet2.write(customer_row, 3, customer_payment_data[customer]['amount_company_currency'])
                customer_row += 1  



        
            # self._add_invoice_line_to_excel(sheet, account_move, row, border, txt_border,
            #                    currency_symbol)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def _add_invoice_line_to_excel(self, sheet, account_move, row, border, txt_border,
                      currency_symbol):
        """
        Function to add invoice line values to the Excel file
        :param sheet: Current Excel sheet where data to be added
        :param account_move : Object of invoice in which data adding
        :param row:Excel row value of next data to be added
        :param border :Excel styling for adding border for each cell
        :param txt_border : Excel styling for adding data in each cell
        :param currency_symbol : Currency symbol of current record
        """
        for line in account_move.invoice_line_ids:
            # For adding value of the invoice lines
            tax = str(
                line.tax_ids.name) if line.tax_ids.name \
                                      is not False else ''
            sheet.write(row, 0, line.product_id.name, border)
            sheet.write(row, 1, line.name, border)
            sheet.write(row, 2, line.quantity, border)
            sheet.write(row, 3, line.account_id.display_name, border)
            sheet.write(row, 4, line.discount, border)
            sheet.write(row, 5, line.price_unit, border)
            sheet.write(row, 6, tax, border)
            sheet.write(row, 7,
                        str(currency_symbol) + str(line.price_subtotal),
                        border)
            row += 1

#        row += 1
#        sheet.write(row, 6, 'Total Amount', txt_border)
#        sheet.write(row, 7,
#                    str(currency_symbol) + str(account_move.amount_total),
#                    border)
