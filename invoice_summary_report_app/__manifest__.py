# -*- coding: utf-8 -*-

{
    'name': 'Invoice Summary Reports | Customer Invoice Summary Report | Vendor Bill Summary Report',
    "author": "Edge Technologies",
    'version': '16.0.1.0',
    'live_test_url': "https://youtu.be/QzwIFUz-sI8",
    "images":['static/description/main_screenshot.png'], 
    'summary': 'Print Invoices Summary Report Invoice summary pdf report Invoice summary excel reports Customer Invoice summary excel report vendor bill summary excel report payment summary report invoice payment summary report print invoice excel report bill excel report',
    'description': 'Odoo invoice summary reports app helps to generate and print invoice summary reports of customers in pdf as well as excel format.User can generate report between date range.User can generate pdf reports and xls report as customer invoice,credit note,vendor bill,debit note.',
    'license': "OPL-1",
    'depends': ['base' ,'account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_summary_views.xml',
        'views/reports_menu.xml',
        'reports/reports.xml',
        'reports/invoice_summary_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'price': 10,
    'currency': "EUR",
    'category': 'Invoicing',
}