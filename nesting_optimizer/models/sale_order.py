from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_dxf_products = fields.Boolean("Has DXF Products", compute='_compute_has_dxf_products', store=False)

    @api.depends('order_line.product_id.product_tmpl_id.dxf_file')
    def _compute_has_dxf_products(self):
        for order in self:
            order.has_dxf_products = any(line.product_id.product_tmpl_id.dxf_file for line in order.order_line)

    def action_calculate(self):
        pass
