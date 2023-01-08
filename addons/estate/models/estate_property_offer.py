from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = "Offer of a Estate Property"

    price = fields.Float()
    status = fields.Selection(
        selection=[('acp', 'Accepted'),
                   ('ref', 'Refused')],
        copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer('Validity (days)', default=7)
    date_deadline = fields.Date('Deadline', compute='_date_deadline', inverse='_inverse_date_deadline')
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _sql_constraints = [
        ('positive_price', 'CHECK(price >= 0)',
         "Offer's Price must be positive."),
    ]
    _order = "price desc"

    @api.depends('validity')
    def _date_deadline(self):
        for record in self:
            try:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            except Exception as ex:
                pass

    def _inverse_date_deadline(self):
        for record in self:
            try:
                record.validity = timedelta(days=record.validity) - record.create_date
            except Exception as ex:
                pass

    def _set_accepted(self):
        self.status = 'acp'

    def _set_refused(self):
        self.status = 'ref'

    @property
    def _has_property_accepted_any_offer(self):
        return self.property_id._has_accepted_any_offer()

    def action_set_accepted(self):
        for record in self:
            if not record._has_property_accepted_any_offer:
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
                record._set_accepted()
            else:
                raise UserError("This property already accepted an offer. So cannot accept any other offer.")
        return True

    def action_set_refused(self):
        for record in self:
            record._set_refused()
        return True

    def _set_property_state_offer_rec(self):
        self.property_id.state = 'offer-rec'

    @api.model
    def create(self, vals):
        property_id = vals['property_id']
        property = self.env['estate.property'].browse(property_id)
        property.state = 'offer-rec'
        if property.mapped('offer_ids.price'):
            max_offer_amount = max(property.mapped('offer_ids.price'))
            if vals['price'] < max_offer_amount:
                raise UserError("You can't create an offer with amount that is lower than existing offers.")
        return super().create(vals)
