from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property\'s tag'

    name = fields.Char('Name', required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'Tag name must be unique.')
    ]
    _order = "name"
