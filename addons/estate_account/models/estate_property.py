from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    customer_invoice = 'out_invoice'

    def _create_an_account_move(self):
        journal = self.env['account.move'].with_context(default_move_type=self.customer_invoice)._get_default_journal()
        account_move_vals = {
            'partner_id': self[0].buyer_id,
            'move_type': self.customer_invoice,
            'journal_id': journal[0].id,
            "invoice_line_ids": [
                Command.create({
                    'name': "6% of the selling price",
                    'quantity': 1,
                    'price_unit': self[0].selling_price * 0.06,
                }),
                Command.create({
                    'name': "administrative fees",
                    'quantity': 1,
                    'price_unit': 100.00
                })
            ]
        }
        account_move = self.env['account.move'].create(account_move_vals)
        return account_move

    def action_set_sold(self):
        self._create_an_account_move()
        return super().action_set_sold()
