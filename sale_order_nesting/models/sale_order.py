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

    # ================================================================
    # ====================== Shape ===================================
    # ================================================================

    def _validate_shape_line(self, line):
        """Validate a sale order line before creating a nesting shape."""

        if line.width <= 0 or line.height <= 0:
            raise UserError(
                "Width and Height must be positive values for product '%s'."
                % line.product_id.display_name
            )

    def _build_shape(self, line):
        """Create a nesting shape from a sale order line."""

        product = line.product_id
        template = product.product_tmpl_id

        shape = self.get_shape(
            json_shape=template.shape,
            qty=line.product_uom_qty,
            target_width=line.width,
            target_height=line.height,
        )

        shape["name"] = product.display_name

        return shape

    def _get_shapes(self):
        """
        Build and return all nesting shapes from the sale order,
        sorted from largest to smallest.
        """
        self.ensure_one()

        shapes = []

        for line in self.order_line.filtered("has_dxf_shape"):
            self._validate_shape_line(line)
            shapes.append(self._build_shape(line))

        if not shapes:
            raise UserError("No valid DXF shapes found in the order.")

        return self.sort_shapes_by_area(shapes)

    # ================================================================
    # ==================== Sheets ====================================
    # ================================================================

    def _get_sheets(self):
        """
        Retrieve all available stock sheets with valid dimensions and positive stock
        and sort them by area, width and height from smallest to largest.
        """
        self.ensure_one()

        sheets = self.env['product.product'].search([
            ('width', '>', 0),
            ('height', '>', 0),
            ('qty_available', '>', 0),
        ])

        if not sheets:
            raise UserError("No valid stock sheets found.")

        return self.get_sheets(sheets)

    # ================================================================
    # ================== Calculations ================================
    # ================================================================

    def action_calculate(self):
        """Calculate nesting and create attachments with results."""
        self.ensure_one()

        # Get shapes from order lines
        shapes = self._get_shapes()

        # Get available stock sheets
        sheets = self._get_sheets()

        self.print_shapes(shapes)
        self.print_sheets(sheets)

        result = self.nest(shapes, sheets)

        # created_attachments = []
        #
        # # Clear previous nesting result attachments
        # old_attachments = self.env['ir.attachment'].search([
        #     ('res_model', '=', self._name),
        #     ('res_id', '=', self.id),
        #     ('name', 'ilike', 'Nesting Result:%')
        # ])
        # old_attachments.unlink()
        #
        # viz_bins = self.nest(sheets)
        #
        # for v in viz_bins:
        #     attachment = self.env['ir.attachment'].create({
        #         # Sheet + Bin number in the name (VERY IMPORTANT for grouping in JS)
        #         'name': f'Nesting Result: {v["sheet_name"]} - Bin {v["bin_index"]}',
        #         'type': 'binary',
        #         'datas': v['base64'],
        #         'res_model': 'sale.order',
        #         'res_id': self.id,
        #         'mimetype': 'image/png',
        #         'description': f'Sheet:{v["sheet_name"]}|Bin:{v["bin_index"]}|Items:{v["items_count"]}',
        #     })
        #     created_attachments.append(attachment)
        #
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
