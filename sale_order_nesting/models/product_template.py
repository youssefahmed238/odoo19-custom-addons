from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = ['product.template', 'nester']

    dxf_shape = fields.Binary("DXF Shape")
    dxf_filename = fields.Char("DXF Filename")

    shape = fields.Json("Shape Data")

    width = fields.Float("Shape Width")
    height = fields.Float("Shape Height")

    @api.onchange('dxf_shape')
    def _onchange_dxf_shape(self):
        if self.dxf_shape:
            shape = self.convert_dxf_to_shape(self.dxf_shape)
            if shape:
                self.shape = shape
                self.image_1920, self.width, self.height = self.convert_shape_to_image1920(self.shape)
                self.name = self.dxf_filename.rsplit('.', 1)[0]

            else:
                self.shape = False
                self.image_1920 = False
                self.width = 0
                self.height = 0
        else:
            self.shape = False
            self.image_1920 = False
            self.width = 0
            self.height = 0
