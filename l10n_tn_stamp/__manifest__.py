# -*- coding: utf-8 -*-
{
    'name': "Tunisia Stamp Tax",

    'summary': """
        Activation du droit de timbre fiscal pour les sociétés tunisiennes
        """,

    'description': """
        Ce module permet d'activer la taxe globale (Timbre Fiscal) pour les factures des achats et des ventes...
        """,

    'author': "Info Service (Tunisia)",
    'website': "http://www.infoservice.tn",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': [
        'base',
        'account'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/stamp_settings.xml',
        'views/stamp_partner.xml',
        'views/stamp_account_move.xml',
        # 'report/stamp_invoice_report.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
