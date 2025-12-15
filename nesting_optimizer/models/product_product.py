from odoo import models, fields


class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    height = fields.Float(string='Height')
    width = fields.Float(string='Width')
