from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    has_dxf_shape = fields.Boolean("Has DXF File", compute='_compute_has_dxf_shape', store=False)

    width = fields.Float("Width")
    height = fields.Float("Height")

    @api.depends('product_id.dxf_shape')
    def _compute_has_dxf_shape(self):
        for line in self:
            line.has_dxf_shape = bool(line.product_id.dxf_shape)

    @api.onchange('product_id')
    def _onchange_product_fill_dimensions(self):
        for line in self:
            product = line.product_id
            tmpl = line.product_id.product_tmpl_id

            if product and tmpl:
                if tmpl.dxf_shape:
                    line.width = tmpl.width or 0.0
                    line.height = tmpl.height or 0.0
                else:
                    line.width = 0.0
                    line.height = 0.0
            else:
                line.width = 0.0
                line.height = 0.0
