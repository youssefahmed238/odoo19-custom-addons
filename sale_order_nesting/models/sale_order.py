from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'nester']

    has_dxf_products = fields.Boolean("Has DXF Products", compute='_compute_has_dxf_products', store=False)

    # Attachment field for nesting images
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'sale.order')],
                                     string='Attachments')

    # Field for nesting image viewer widget
    nesting_images = fields.Char("Nesting Images", compute='_compute_nesting_images', store=False)

    stock_sheet = fields.Many2one('product.product', string='Stock Sheet')

    @api.depends('order_line.product_id.product_tmpl_id.dxf_shape')
    def _compute_has_dxf_products(self):
        for order in self:
            order.has_dxf_products = any(line.product_id.product_tmpl_id.dxf_shape for line in order.order_line)

    @api.depends('attachment_ids')
    def _compute_nesting_images(self):
        """Computed field to trigger the nesting image viewer widget"""
        for order in self:
            # Count nesting result attachments
            nesting_count = len([att for att in order.attachment_ids
                                 if att.name and 'Nesting Result:' in att.name])
            order.nesting_images = f"nesting_images_{order.id}_{nesting_count}"

    def _get_shapes(self):
        """Extract shapes from order lines with DXF products."""
        self.ensure_one()

        shapes = []
        for line in self.order_line:
            if line.has_dxf_shape:
                product = line.product_id
                tmpl = product.product_tmpl_id

                if not (line.width or line.height) or line.width <= 0 or line.height <= 0:
                    raise ValueError("Width and Height must be positive values for product '{}'.".format(product.name))

                product_name = product.name or tmpl.name or "Unnamed Product"
                shape = self.get_shape(tmpl.shape, line.product_uom_qty, line.width, line.height)
                shape['name'] = product_name

                shapes.append(shape)

        if not shapes:
            raise UserError("No valid shapes found in the order lines.")

        return shapes

    def _get_sheets(self, shapes):
        self.ensure_one()

        stock_sheets = self.env['product.product'].search([
            ('width', '>=', 0),
            ('height', '>=', 0),
            ('qty_available', '>', 0),
        ])

        return self.get_sheets(stock_sheets, shapes)

    def action_calculate(self):
        """Calculate nesting and create attachments with results."""
        self.ensure_one()

        # Get shapes from order lines
        shapes = self._get_shapes()

        # Get available stock sheets
        sheets = self._get_sheets(shapes)
        for s_id, s_data in sheets.items():
            print("Sheet name:", s_data['name'], "Used qty:", s_data['used_quantity'], "width:", s_data['width'],
                  "height:", s_data['height'])
            for shape in s_data['shapes']:
                print(" - Shape:", shape)

        created_attachments = []

        # Clear previous nesting result attachments
        old_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('name', 'ilike', 'Nesting Result:%')
        ])
        old_attachments.unlink()

        viz_bins = self.nest(sheets)

        for v in viz_bins:
            attachment = self.env['ir.attachment'].create({
                # Sheet + Bin number in the name (VERY IMPORTANT for grouping in JS)
                'name': f'Nesting Result: {v["sheet_name"]} - Bin {v["bin_index"]}',
                'type': 'binary',
                'datas': v['base64'],
                'res_model': 'sale.order',
                'res_id': self.id,
                'mimetype': 'image/png',
                'description': f'Sheet:{v["sheet_name"]}|Bin:{v["bin_index"]}|Items:{v["items_count"]}',
            })
            created_attachments.append(attachment)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
