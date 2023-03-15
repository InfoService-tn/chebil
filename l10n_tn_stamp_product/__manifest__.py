# -*- coding: utf-8 -*-
{
    'name': "Chebil customisations - Tunisia",

    'summary': """
        Personnalisation spéciales pour le Timbre Fiscal
        """,

    'description': """
        Ce module permet de personnaliser les factures avec le Timbre Fiscal ...
        """,

    'author': "Info Service (Tunisia)",
    'website': "http://www.infoservice.tn",
    'category': 'Uncategorized',
    'version': '16.0',
    'depends': [
        'base',
        'account'
    ],
    'data': [
        'report/stamp_invoice_report.xml',
        'views/report_invoice.xml',
    ],
}
