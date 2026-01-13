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
            if line.product_id and line.product_id.product_tmpl_id:
                tmpl = line.product_id.product_tmpl_id
                if tmpl.dxf_shape:
                    # Ensure dimensions are calculated if not already done
                    tmpl.ensure_dimensions_calculated()
                    print(f"Template ID: {tmpl.id}, Width: {tmpl.width}, Height: {tmpl.height}")
                    line.width = tmpl.width or 0.0
                    line.height = tmpl.height or 0.0
                else:
                    print(f"Template ID: {tmpl.id} has no DXF shape")
                    line.width = 0.0
                    line.height = 0.0
            else:
                print("No product or template found")
                line.width = 0.0
                line.height = 0.0
