from odoo import fields, models, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Type of Estate Property'

    name = fields.Char('Name', required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties")
    sequence = fields.Integer('Sequence')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string="Offers")
    offer_count = fields.Integer('Offer Count', compute="_offer_count")

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'Type name must be unique.')
    ]
    _order = "sequence, name"

    @api.depends('offer_ids')
    def _offer_count(self):
        for record in self:
            record.offer_count = len(record.mapped('offer_ids'))
