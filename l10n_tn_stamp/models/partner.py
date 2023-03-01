from odoo import models, fields, api


class ContactTimbreFiscal(models.Model):
    _inherit = 'res.partner'

    stamp_tax_enable = fields.Boolean (string="Timbre Fiscal")
