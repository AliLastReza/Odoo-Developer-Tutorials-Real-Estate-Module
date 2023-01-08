from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char("Title", required=True)
    property_type_id = fields.Many2one("estate.property.type")
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Date availability", copy=False, default=lambda self: fields.Date.today() + timedelta(days=90)
    )
    expected_price = fields.Float("Expected price", required=True)
    selling_price = fields.Float("Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living area")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden area")
    garden_orientation = fields.Selection(
        string="Garden orientation", selection=[("n", "North"), ("s", "South"), ("e", "East"), ("w", "West")]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer-rec", "Offer Received"),
            ("offer-acp", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancel", "Canceled"),
        ],
        string="Status",
        required=True,
        copy=False,
        default="new",
    )
    salesperson_id = fields.Many2one("res.users", string="salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Float(compute="_total_area")
    best_price = fields.Float(compute="_best_price")
    has_accepted_any_offer = fields.Boolean(compute="_has_accepted_any_offer")

    _sql_constraints = [
        ("positive_expected_price", "CHECK(expected_price >= 0)", "Expected price must be positive."),
        ("positive_selling_price", "CHECK(selling_price >= 0)", "Selling price must be positive"),
    ]
    _order = "id desc"

    @api.depends("living_area", "garden_area")
    def _total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _best_price(self):
        for record in self:
            if len(record.offer_ids):
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _on_change_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "n"
        else:
            self.garden_area = None
            self.garden_orientation = None

    @api.depends("offer_ids.status")
    def _has_accepted_any_offer(self):
        for record in self:
            if len(record.offer_ids):
                record.has_accepted_any_offer = bool(any(offer.status == "acp" for offer in record.offer_ids))
            record.has_accepted_any_offer = None

    def _set_canceled(self):
        self.state = "cancel"

    def _set_sold(self):
        self.state = "sold"

    @property
    def _has_sold(self):
        return self.state == "sold"

    @property
    def _has_canceled(self):
        return self.state == "cancel"

    def action_set_canceled(self):
        for record in self:
            if not record._has_sold:
                record._set_canceled()
            else:
                raise UserError("Sold properties cannot be canceled.")
        return True

    def action_set_sold(self):
        for record in self:
            if not record._has_canceled:
                record._set_sold()
            else:
                raise UserError("Canceled properties cannot be sold.")
        return True

    @api.ondelete(at_uninstall=False)
    def _prevent_unlink_in_unauthorized_states(self):
        for record in self:
            if record.state not in ("new", "cancel"):
                raise UserError("You can't delete a Property unless its status is 'New' or 'Canceled'.")
