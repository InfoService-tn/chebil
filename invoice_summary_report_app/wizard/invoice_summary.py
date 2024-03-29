from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import ValidationError
try:
	import xlsxwriter
except ImportError:
	_logger.debug('Cannot `import xlsxwriter`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.') 


class InvoiceSummary(models.TransientModel):
	_name = 'invoice.summary'
	_description = "Rapport des factures"


	start_date = fields.Date(string="Date de début" ,default=date.today())
	end_date = fields.Date(string="Date de fin" , default=date.today())
	invoice_status = fields.Selection([('posted', 'Comptabilisé'), ('draft', 'Brouillon'), ('cancel', 'Annulé')],
					string='Statut')
	invoice_type = fields.Selection([('customer_invoice', 'Facture client'),
					('credit_note', 'Note de crédit client'),
					('bill', 'Facture fournisseur'),
					('vendor_credit_note', 'Note de crédit fournisseur')], string='Type de facture')
	partner_ids = fields.Many2many('res.partner', string="Partenaires" )
                   # , required=False)
	company_ids = fields.Many2many('res.company', string='Société' , default=lambda self: self.env.user.company_id)
	
	document = fields.Binary('Télécharger le fichier')
	file = fields.Char('Nom du fichier rapport', readonly=1)


	def action_print_report(self):
		self.ensure_one()
		[data] = self.read()
		datas = {
			 'ids': [1],
			 'model': 'invoice.summary',
			 'form': data
		}
		return self.env.ref('invoice_summary_report_app.action_report_invoice_summary').report_action(self, data=datas)


	def _get_invoice_details(self,data,partner):

		lines =[]
		# if partner:

		if True:
			start_date = data.get('start_date')
			end_date = data.get('end_date')
			partner_ids = data.get('partner_ids')
			invoice_type = data.get('invoice_type')
			invoice_status = data.get('invoice_status')
			partner_data=[]
			account_move = self.env['account.move'].search([('invoice_date','>=', start_date),('invoice_date','<=', end_date)])
			account_move = sorted(account_move, key=lambda invoice: invoice.name)

            # account_move = self.env['account.move'].search([('partner_id','=',partner),('invoice_date','>=', start_date),('invoice_date','<=', end_date)])

			if invoice_type == 'customer_invoice':

				for records in account_move:

					value = {}
					if invoice_status == 'draft':
						if records.move_type=='out_invoice' and records.state=='draft':
							value.update({
								'partner_id' : records.partner_id.name,
								'name' : records.name,
								'invoice_date' : records.invoice_date,
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
								'amount_paid' : records.amount_paid,
								'amount_residual' : records.amount_residual,
							})
					elif invoice_status == 'posted':

						if records.move_type=='out_invoice' and records.state=='posted':
							value.update({
								'partner_id' : records.partner_id.name,
								'name' : records.name,
								'invoice_date' : records.invoice_date,
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
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
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
								'amount_paid' : credit_record.amount_paid,
								'amount_residual' : credit_record.amount_residual,
							})
					elif invoice_status == 'posted':

						if credit_record.move_type=='out_refund' and credit_record.state=='posted':
							credit_value.update({
								'partner_id' : credit_record.partner_id.name,
								'name' : credit_record.name,
								'invoice_date' : credit_record.invoice_date,
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
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
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
								'amount_paid' : bill_record.amount_paid,
								'amount_residual' : bill_record.amount_residual,
							})
							# print('bill_note------------------------' ,bill_note)
					elif invoice_status== 'posted':
						if bill_record.move_type=='in_invoice' and bill_record.state=='posted':
							bill_note.update({
								'partner_id' : bill_record.partner_id.name,
								'name' : bill_record.name,
								'invoice_date' : bill_record.invoice_date,
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
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
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
								'amount_paid' :note_record.amount_paid,
								'amount_residual' : note_record.amount_residual,
							})
					elif invoice_status == 'posted':
						if note_record.move_type=='in_refund' and note_record.state=='posted':
							refund_note.update({
								'partner_id' : note_record.partner_id.name,
								'name' : note_record.name,
								'invoice_date' : note_record.invoice_date,
								'amount_untaxed': records.amount_untaxed_signed,
								'amount_tax': records.amount_tax_signed,
								'amount_stamptax': 1,
								'amount_total': records.amount_total_signed,
								'amount_paid' : note_record.amount_paid,
								'amount_residual' : note_record.amount_residual,
							})
					partner_data.append(refund_note)

			lines.append({'partner_data':partner_data})

		return lines



	def action_print_xls(self):

		[data] = self.read()
		file_path = 'Rapport des factures' + '.xlsx'
		workbook = xlsxwriter.Workbook('/tmp/' + file_path)
		worksheet = workbook.add_worksheet('Rapport des factures')

		header_format = workbook.add_format({'bold': True,'valign':'vcenter','font_size':16,'align': 'center','bg_color':'#D8D8D8'})
		title_format = workbook.add_format({'border': 1,'bold': True, 'valign': 'vcenter','align': 'center', 'font_size':14,'bg_color':'#D8D8D8'})
		date_format = workbook.add_format({'border': 2 ,'valign': 'vcenter','align': 'center'})
		cell_wrap_format = workbook.add_format({'border': 1,'valign':'vjustify','valign':'vcenter','align': 'left','font_size':12,}) ##E6E6E6
		cell_num_format = workbook.add_format({'border': 1,'valign':'vjustify','valign':'vcenter','align': 'right','font_size':12,'num_format': '#,###0.000'}) ##E6E6E6

		cell_format=workbook.add_format({
			'bold':1,
			'align':'center',
			'fg_color':'gray',
			})
		worksheet.set_row(1,20)  #Set row height
		partner_ids= data.get('partner_ids')
		invoice_status = data.get('invoice_status')
		invoice_type = data.get('invoice_type')

		data = {
			'invoice_type' : invoice_type,
			'invoice_status' : invoice_status,
			'partner_ids' : partner_ids,
			'start_date': self.start_date,
			'end_date': self.end_date,
		}
		TITLEHEDER = 'Rapport des factures'
		worksheet.merge_range('A1:G1' , TITLEHEDER,header_format)
		rowscol = 1

		# if partner_ids:
			#for partner in partner_ids:
		worksheet.set_row(1,20)
		start_date = datetime.strptime(str(data.get('start_date', False)), '%Y-%m-%d').date()
		from_date = start_date.strftime('%d-%m-%Y')
		end_date = datetime.strptime(str(data.get('end_date', False)), '%Y-%m-%d').date()
		to_date = end_date.strftime('%d-%m-%Y')

		# worksheet.merge_range((rowscol + 2), 0, (rowscol + 2), 1,'Start Date', title_format)
		# worksheet.merge_range((rowscol + 3), 0, (rowscol + 3), 1, str(from_date) , title_format)

		# worksheet.merge_range((rowscol + 2), 4, (rowscol + 2), 5,'End Date', title_format)
		# worksheet.merge_range((rowscol + 3), 4, (rowscol + 3), 5, str(to_date) , title_format)
		# rowscol  = rowscol

		row = 2
		worksheet.write(row, 0,"Facture",cell_format)
		worksheet.write(row, 1,"Date",cell_format)
		worksheet.write(row, 2,"Partnaire", cell_format)
		worksheet.write(row, 3,"Montant HT", cell_format)
		worksheet.write(row, 4,"Taxes", cell_format)
		worksheet.write(row, 5,"Fimbre Fiscal", cell_format)
		worksheet.write(row, 6,"Total", cell_format)

		worksheet.write(row, 7, "Produit", cell_format)
		worksheet.write(row, 8, "Quantité", cell_format)
		worksheet.write(row, 9, "Prix", cell_format)
		worksheet.write(row,10, "Remise %", cell_format)
		worksheet.write(row,11, "Taxe", cell_format)
		worksheet.write(row,12, "Total", cell_format)

		# worksheet.write(row+2,4,"Amount Paid",cell_format)
		# worksheet.write(row+2,5,"Amount Due",cell_format)
		rows = row + 1
		# rowscol1 = rows +1
		# rows = rowscol1
		partner = ''
		# rowscol1 = rows + 2

		# invoices = sorted(self._get_invoice_details(data, partner), key=lambda invoice: invoice.name)

		for records in self._get_invoice_details(data, partner):
			for record in records.get('partner_data'):
				if record.get ('name')!="" and record.get('invoice_date'):
					worksheet.write(rows, 0, record.get('name'), cell_wrap_format)
					worksheet.write(rows, 1, str(record.get('invoice_date')), cell_wrap_format)
					worksheet.write(rows, 2, record.get('partner_id'), cell_wrap_format)
					worksheet.write(rows, 3, record.get('amount_untaxed'), cell_num_format)
					worksheet.write(rows, 4, record.get('amount_tax')-1, cell_num_format)
					worksheet.write(rows, 5, record.get('amount_stamptax'), cell_num_format)
					worksheet.write(rows, 6, record.get('amount_total'), cell_num_format)
					# worksheet.write(rows, 4,  record.get('amount_paid'), cell_wrap_format)
					# worksheet.write(rows, 5,  record.get('amount_residual'), cell_wrap_format)

					# rows = rows + 1

					# invoice_lines = record.get ('invoice_lines')
					invoice_lines = self.env['account.move'].search([('name', '=', record.get('name'))]).invoice_line_ids
					for line in invoice_lines:
						if line.name != '[TF] Timbre fiscal':
							worksheet.write(rows, 7, line.name, cell_wrap_format)
							worksheet.write(rows, 8, line.quantity, cell_wrap_format)
							worksheet.write(rows, 9, line.price_unit, cell_num_format)
							worksheet.write(rows,10, line.discount, cell_wrap_format)
							worksheet.write(rows,11, line.tax_ids.amount, cell_wrap_format)
							worksheet.write(rows,12, line.balance, cell_num_format)
							rows = rows + 1

			# rows = rows
		workbook.close()
		partner_details = base64.b64encode(open('/tmp/' + file_path, 'rb+').read())
		self.document = partner_details
		self.file = 'Invoice Summary Report'+'.xlsx'
		return {
			'res_id': self.id,
			'name': 'Invoice Summary',
			'view_mode' : 'form',
			'view_type': 'form',
			'res_model': 'invoice.summary',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}