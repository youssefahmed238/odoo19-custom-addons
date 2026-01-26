try:
    from odoo import models, api
    from odoo.exceptions import UserError
    from nest2D import Box

except ImportError as e:
    raise ImportError("ImportError occurred in sheet model: {}".format(e))


class Sheet(models.AbstractModel):
    _name = 'sheet'
    _description = 'Sheet Mixin Model'
    _inherit = ['shape']

    @api.model
    def is_shape_fitting(self, shape, sheet_width, sheet_height):
        """Check if a shape can fit within specified sheet dimensions."""
        sw = shape.get('width', 0)
        sh = shape.get('height', 0)
        return (sw <= sheet_width and sh <= sheet_height) or (sh <= sheet_width and sw <= sheet_height)

    @api.model
    def check_validate_stock_sheets(self, stock_sheets, shapes):
        """Validate stock sheets availability and capacity against shapes."""

        # Validate stock sheets availability
        if not stock_sheets:
            raise UserError("No stock sheets available.")

        shapes_area = sum(shape.get('item').area() * shape.get('qty', 1) for shape in shapes)
        total_sheets_area = sum(sheet.width * sheet.height * sheet.qty_available for sheet in stock_sheets)

        if total_sheets_area < shapes_area:
            raise UserError("Stock sheets not sufficient to cover all of shapes.")

    @api.model
    def sort_sheets_by_area(self, sheets):
        """Sort sheets by area in ascending order (smallest to largest)."""
        return sorted(sheets, key=lambda s: s.width * s.height)

    @api.model
    def get_sheets_with_shapes(self, stock_sheets, shapes):
        """Assign shapes to stock sheets and return the assignment."""
        self.ensure_one()

        # Sort shapes by area (largest first)
        sorted_shapes = self.sort_shapes_by_area(shapes)

        # Sort sheets by area (smallest first)
        sorted_sheets = self.sort_sheets_by_area(stock_sheets)

        sheets = {}

        # Process each sheet type
        for sheet in sorted_sheets:
            if not sorted_shapes:
                break

            sheet_total_area = sheet.width * sheet.height

            # Process each instance of this sheet type
            for sheet_instance in range(int(sheet.qty_available)):
                if not sorted_shapes:
                    break

                # Reset area tracking for each new sheet instance
                area_remaining = sheet_total_area
                shapes_assigned = []

                # Try to assign shapes to this sheet instance
                for shape in sorted_shapes:
                    if shape['qty'] <= 0:
                        continue

                    item = shape['item']
                    shape_area = item.area()

                    # Check if shape fits dimensionally
                    if not self.is_shape_fitting(shape, sheet.width, sheet.height):
                        continue

                    # Assign as many of this shape as possible
                    while shape['qty'] > 0 and shape_area <= area_remaining:
                        shapes_assigned.append(item)
                        shape['qty'] -= 1
                        area_remaining -= shape_area

                # If we assigned any shapes to this sheet instance, record it
                if shapes_assigned:
                    if sheet.id not in sheets:
                        sheets[sheet.id] = {
                            'name': sheet.name,
                            'used_quantity': 0,
                            'box': Box(sheet.width, sheet.height),
                            'shapes': [],
                            'width': sheet.width,
                            'height': sheet.height,
                        }

                    sheets[sheet.id]['used_quantity'] += 1
                    sheets[sheet.id]['shapes'].extend(shapes_assigned)

                # Clean up fully assigned shapes (do this once per sheet instance)
                sorted_shapes = [s for s in sorted_shapes if s['qty'] > 0]

        # Check if any shapes remain unassigned
        if sorted_shapes:
            unassigned_count = sum(s['qty'] for s in sorted_shapes)
            unassigned_details = '\n'.join([f"  - {s['name']}: {s['qty']} piece(s)" for s in sorted_shapes])

            raise UserError(
                f"Unable to assign {unassigned_count} shape(s) to available stock sheets.\n\n"
                f"Unassigned shapes:\n{unassigned_details}\n\n"
                "Please check stock availability or shape dimensions."
            )

        return sheets

    @api.model
    def get_sheets(self, stock_sheets, shapes):
        """Get sheets with assigned shapes."""
        self.ensure_one()

        # Validate stock sheets and shapes
        self.check_validate_stock_sheets(stock_sheets, shapes)

        return self.get_sheets_with_shapes(stock_sheets, shapes)
