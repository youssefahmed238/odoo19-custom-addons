from odoo import models, fields


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    width = fields.Float(string='Width')
    height = fields.Float(string='Height')

    # unit = fields.Selection([
    #     ('mm', 'Millimeter'),
    #     ('cm', 'Centimeter'),
    # ], string='Unit', default='mm')
