from odoo import models, fields, api,_
from datetime import datetime,date,timedelta
from odoo.exceptions import ValidationError
import time


class InvoicesummaryReport(models.AbstractModel):
	_name = 'report.invoice_summary_report_app.summary_invoice_report'
	_description = "Invoice Summary Report"


	def _get_invoice_details(self,data,partner):
		lines =[]
		if partner:
			start_date = data.get('start_date')
			end_date = data.get('end_date')
			partner_ids = data.get('partner_ids')
			invoice_type = data.get('invoice_type')
			invoice_status = data.get('invoice_status')
			partner_data=[]
			account_move = self.env['account.move'].search([('partner_id','=',partner),('invoice_date','>=', start_date),('invoice_date','<=', end_date)])
			if invoice_type == 'customer_invoice':
				for records in account_move:
					value = {}
					if invoice_status == 'draft':
						if records.move_type=='out_invoice' and records.state=='draft':
							value.update({
								'partner_id' : records.partner_id.name,
								'name' : records.name,
								'invoice_date' : records.invoice_date,
								'amount_total': records.amount_total,
								'amount_paid' : records.amount_paid,
								'amount_residual' : records.amount_residual,
							})
					elif invoice_status == 'posted':
						if records.move_type=='out_invoice' and records.state=='posted':
							value.update({
								'partner_id' : records.partner_id.name,
								'name' : records.name,
								'invoice_date' : records.invoice_date,
								'amount_total': records.amount_total,
								'amount_paid' : records.amount_paid,
								'amount_residual' : records.amount_residual,
							})
			
					partner_data.append(value)

			elif invoice_type == 'credit_note':
				for credit_record in account_move:
					credit_value = {}
					if invoice_status == 'draft':
						if credit_record.move_type=='out_refund' and credit_record.state=='draft':
							credit_value.update({
								'partner_id' : credit_record.partner_id.name,
								'name' : credit_record.name,
								'invoice_date' : credit_record.invoice_date,
								'amount_total': credit_record.amount_total,
								'amount_paid' : credit_record.amount_paid,
								'amount_residual' : credit_record.amount_residual,
							})
					elif invoice_status == 'posted':
						if credit_record.move_type=='out_refund' and credit_record.state=='posted':
							credit_value.update({
								'partner_id' : credit_record.partner_id.name,
								'name' : credit_record.name,
								'invoice_date' : credit_record.invoice_date,
								'amount_total': credit_record.amount_total,
								'amount_paid' : credit_record.amount_paid,
								'amount_residual' : credit_record.amount_residual,
							})
					partner_data.append(credit_value)

			elif invoice_type == 'bill':
				for bill_record in account_move:
					bill_note = {}
					if invoice_status == 'draft':
						if bill_record.move_type=='in_invoice' and bill_record.state=='draft':
							bill_note.update({
								'partner_id' : bill_record.partner_id.name,
								'name' : bill_record.name,
								'invoice_date' : bill_record.invoice_date,
								'amount_total': bill_record.amount_total,
								'amount_paid' : bill_record.amount_paid,
								'amount_residual' : bill_record.amount_residual,
							})
					elif invoice_status== 'posted':
						if bill_record.move_type=='in_invoice' and bill_record.state=='posted':
							bill_note.update({
								'partner_id' : bill_record.partner_id.name,
								'name' : bill_record.name,
								'invoice_date' : bill_record.invoice_date,
								'amount_total': bill_record.amount_total,
								'amount_paid' : bill_record.amount_paid,
								'amount_residual' : bill_record.amount_residual,
							})
					partner_data.append(bill_note)

			elif invoice_type == 'vendor_credit_note':
				for note_record in account_move:
					refund_note = {}
					if invoice_status== 'draft':
						if note_record.move_type=='in_refund' and note_record.state=='draft':
							refund_note.update({
								'partner_id' : note_record.partner_id.name,
								'name' : note_record.name,
								'invoice_date' : note_record.invoice_date,
								'amount_total': note_record.amount_total,
								'amount_paid' : note_record.amount_paid,
								'amount_residual' : note_record.amount_residual,
							})
					elif invoice_status == 'posted':
						if note_record.move_type=='in_refund' and note_record.state=='posted':
							refund_note.update({
								'partner_id' : note_record.partner_id.name,
								'name' : note_record.name,
								'invoice_date' : note_record.invoice_date,
								'amount_total': note_record.amount_total,
								'amount_paid' : note_record.amount_paid,
								'amount_residual' : note_record.amount_residual,
							})
					partner_data.append(refund_note)

			lines.append({'partner_data':partner_data})
		return lines


	def _get_report_values(self, docids, data=None):
		start_date = data['form']['start_date']
		start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d-%m-%Y")
		end_date = data['form']['end_date']
		end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%m-%Y")
		invoice_status = data['form']['invoice_status']
		invoice_type = data['form']['invoice_type']
		company_ids = data['form']['company_ids']
		partner_ids= data['form']['partner_ids']
		data  = {
			'start_date'    : start_date,
			'end_date'     : end_date,
			'partner_ids' : partner_ids,
			'company_ids' : company_ids,
			'invoice_status' : invoice_status,
			'invoice_type' : invoice_type,
		}
		return {
			'doc_ids': docids,
			'doc_model': 'invoice.summary',
			'data': data,
			'start_date' : start_date,
			'end_date' : end_date,
			'get_invoice_details': self._get_invoice_details,
		}



