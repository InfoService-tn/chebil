from odoo import models, fields, api

class ResCompanyl(models.Model):
    _inherit = 'res.company'

    stamp_tax_enable = fields.Boolean (string="Timbre Fiscal")
    stamp_tax_amount = fields.Monetary(string="Montant")
    stamp_tax_sales_account = fields.Many2one('account.account', string="Compte Ventes")
    stamp_tax_purchase_account = fields.Many2one('account.account', string="Compte Achats")