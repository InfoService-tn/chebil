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

    stamp_tax = fields.Boolean(string='Timbre Fiscal')
   
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
            amount = amount + " "+curr_label+" "+z2+" "+curr_decimals+"."

        return amount.upper()