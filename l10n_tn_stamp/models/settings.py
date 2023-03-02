from odoo import models, fields, api

class StampCompanyConfigSettings(models.TransientModel):
    _inherit = 'res.company'

    stamp_tax_enable = fields.Boolean (string="Timbre Fiscal")
    stamp_tax_amount = fields.Monetary(string="Montant")
    stamp_tax_sales_account = fields.Many2one('account.account', string="Compte Ventes")
    stamp_tax_purchase_account = fields.Many2one('account.account', string="Compte Achats")
    
    def get_values(self):
        res = super(StampCompanyConfigSettings, self).get_values()
        res.update(
            stamp_tax_enable = self.env['ir.config_parameter'].sudo().get_param('stamp_tax_enable'),
            stamp_tax_amount = float(self.env['ir.config_parameter'].sudo().get_param('stamp_tax_amount')),
            stamp_tax_sales_account = int(self.env['ir.config_parameter'].sudo().get_param('stamp_tax_sales_account')),
            stamp_tax_purchase_account = int(self.env['ir.config_parameter'].sudo().get_param('stamp_tax_purchase_account')),
                    )
        return res

    def set_values(self):
        super(StampCompanyConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('stamp_tax_enable', self.stamp_tax_enable)
        if self.stamp_tax_enable:
            self.env['ir.config_parameter'].set_param('stamp_tax_amount', self.stamp_tax_amount)
            self.env['ir.config_parameter'].set_param('stamp_tax_sales_account', self.stamp_tax_sales_account.id)
            self.env['ir.config_parameter'].set_param('stamp_tax_purchase_account', self.stamp_tax_purchase_account.id)
            