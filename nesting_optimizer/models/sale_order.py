from odoo import models, fields, api
from odoo.exceptions import UserError

try:
    from nest2D import Point, Box, Item, nest, PlacerType, SelectorType
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    matplotlib.use('TkAgg')

    MM = 1000000  # Conversion factor to micrometers
except ImportError as e:
    print("Error importing required modules.")
    raise e


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    has_dxf_products = fields.Boolean("Has DXF Products", compute='_compute_has_dxf_products', store=False)

    # Nesting calculation fields
    total_used_area = fields.Float("Total Used Area (mm²)", readonly=True)
    total_wasted_area = fields.Float("Total Wasted Area (mm²)", readonly=True)
    cut_blade_kerf_thickness = fields.Float("Cut Blade Kerf Thickness (mm)", readonly=True)
    panels = fields.Integer("Total Shapes Count", readonly=True)
    used_stock_sheets = fields.Many2many('product.product', string="Used Stock Sheets", readonly=True)

    # Attachment field for nesting images
    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', 'sale.order')],
                                     string='Attachments')

    # Field for nesting image viewer widget
    nesting_images = fields.Char("Nesting Images", compute='_compute_nesting_images', store=False)

    stock_sheet = fields.Many2one('product.product', string='Stock Sheet')

    used_area = fields.Float(string='Used Area')

    wasted_area = fields.Float(string='Wasted Area')

    spacing = fields.Float(
        string="Kerf / Spacing (mm)",
        default=0.0,
        help="Cut blade kerf / spacing between shapes in mm",
    )

    @api.depends('order_line.product_id.product_tmpl_id.dxf_file')
    def _compute_has_dxf_products(self):
        for order in self:
            order.has_dxf_products = any(line.product_id.product_tmpl_id.dxf_file for line in order.order_line)

    @api.depends('attachment_ids')
    def _compute_nesting_images(self):
        """Computed field to trigger the nesting image viewer widget"""
        for order in self:
            # Count nesting result attachments
            nesting_count = len([att for att in order.attachment_ids
                                 if att.name and 'Nesting Result:' in att.name])
            order.nesting_images = f"nesting_images_{order.id}_{nesting_count}"

    def _scale_points(self, points, target_width, target_height):
        if not target_width or not target_height:
            return points

        xs = [x for x, y in points]
        ys = [y for x, y in points]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        orig_width = max_x - min_x
        orig_height = max_y - min_y

        if orig_width == 0 or orig_height == 0:
            return points

        scale_x = (target_width * MM) / orig_width
        scale_y = (target_height * MM) / orig_height

        scaled = []
        for x, y in points:
            new_x = (x - min_x) * scale_x
            new_y = (y - min_y) * scale_y
            scaled.append((int(new_x), int(new_y)))

        return scaled

    def _get_points(self, shape_points):
        points = []
        for point_str in shape_points.split('\n'):
            x_str, y_str = point_str.split(',')
            points.append((int(float(x_str) * MM), int(float(y_str) * MM)))
        return points

    def _get_shape(self, shape_points, quantity, width, height):
        points = self._get_points(shape_points)

        scaled_points = self._scale_points(
            points,
            width,
            height
        )

        return [Item([
            Point(x, y) for x, y in scaled_points
        ])] * int(quantity)

    def _get_shape_dimensions(self, shape):
        """Get the bounding box dimensions of a shape"""
        vertices = shape.get_vertices()
        min_x = min([point.x for point in vertices])
        max_x = max([point.x for point in vertices])
        min_y = min([point.y for point in vertices])
        max_y = max([point.y for point in vertices])

        width = (max_x - min_x) / MM
        height = (max_y - min_y) / MM

        return width, height

    def _shape_fits_in_sheet(self, shape, sheet_width, sheet_height):
        """Check if a shape can fit within sheet dimensions (considering rotation)"""
        shape_width, shape_height = self._get_shape_dimensions(shape)

        # Check both orientations
        fits_normal = shape_width <= sheet_width and shape_height <= sheet_height
        fits_rotated = shape_height <= sheet_width and shape_width <= sheet_height

        return fits_normal or fits_rotated

    def _get_shapes(self):
        self.ensure_one()
        shapes = []
        for line in self.order_line:
            if line.has_dxf_file:
                product = line.product_id
                tmpl = product.product_tmpl_id
                shapes += self._get_shape(tmpl.shape_points, line.product_uom_qty, line.width, line.height)

        return shapes

    def _check_validate_stock_sheets(self, stock_sheets, shapes):
        # Validate stock sheets availability
        if not stock_sheets:
            raise UserError("No stock sheets available.")

        # Validate total area
        shapes_area = sum([shape.area() / (MM * MM) for shape in shapes])
        total_sheets_area = sum([sheet.width * sheet.height * sheet.qty_available for sheet in stock_sheets])
        if total_sheets_area < shapes_area:
            raise UserError("Stock sheets not sufficient to cover total shapes area.")

        # Validate max shape dimensions - check if at least one sheet can fit each shape
        for shape in shapes:
            shape_width, shape_height = self._get_shape_dimensions(shape)
            can_fit = False
            for sheet in stock_sheets:
                if self._shape_fits_in_sheet(shape, sheet.width, sheet.height):
                    can_fit = True
                    break

            if not can_fit:
                raise UserError(
                    f"Shape with dimensions {shape_width:.2f}x{shape_height:.2f}mm cannot fit in any available stock sheet.")

    def _estimate_shapes_per_sheet(self, shapes, sheet_width, sheet_height):
        """
        Estimate how many shapes can fit in one sheet based on simple grid packing.
        This is a conservative estimate for initial planning.
        """
        if not shapes:
            return 0

        # Get unique shape dimensions
        shape_dims = {}
        for shape in shapes:
            shape_width, shape_height = self._get_shape_dimensions(shape)
            # Use the smaller dimension arrangement (considering rotation)
            min_dim = min(shape_width, shape_height)
            max_dim = max(shape_width, shape_height)

            # Choose best orientation
            if min_dim <= sheet_width and max_dim <= sheet_height:
                # Normal orientation
                dim_key = (shape_width, shape_height)
            elif max_dim <= sheet_width and min_dim <= sheet_height:
                # Rotated orientation
                dim_key = (shape_height, shape_width)
            else:
                # Try best fit
                if shape_width <= sheet_width and shape_height <= sheet_height:
                    dim_key = (shape_width, shape_height)
                else:
                    dim_key = (shape_height, shape_width)

            if dim_key not in shape_dims:
                shape_dims[dim_key] = 0
            shape_dims[dim_key] += 1

        # Calculate grid-based packing estimate for each shape type
        total_capacity = 0
        for (s_width, s_height), count in shape_dims.items():
            # How many shapes fit in each direction
            shapes_per_row = int(sheet_width / s_width) if s_width > 0 else 0
            shapes_per_col = int(sheet_height / s_height) if s_height > 0 else 0
            capacity_per_sheet = shapes_per_row * shapes_per_col

            if capacity_per_sheet > 0:
                total_capacity += min(count, capacity_per_sheet)

        return max(1, total_capacity)  # At least 1 shape per sheet

    def _get_sheets(self, shapes):
        self.ensure_one()

        stock_sheets = self.env['product.product'].search([
            ('width', '>', 0),
            ('height', '>', 0),
            ('qty_available', '>', 0),
        ])

        self._check_validate_stock_sheets(stock_sheets, shapes)

        sheets = {}
        remaining_shapes = sorted(shapes, key=lambda s: s.area(), reverse=True)

        # Sort sheets by area (smallest first for better utilization)
        sorted_sheets = sorted(stock_sheets, key=lambda s: s.width * s.height)

        for sheet in sorted_sheets:
            if not remaining_shapes:
                break

            sheet_width = sheet.width
            sheet_height = sheet.height
            sheet_area = sheet_width * sheet_height

            # Find all shapes that can fit in this sheet (dimensionally)
            fitting_shapes = []
            for shape in remaining_shapes:
                if self._shape_fits_in_sheet(shape, sheet_width, sheet_height):
                    fitting_shapes.append(shape)

            if not fitting_shapes:
                continue

            # Estimate how many shapes can realistically fit per sheet
            shapes_per_sheet = self._estimate_shapes_per_sheet(fitting_shapes, sheet_width, sheet_height)

            if shapes_per_sheet == 0:
                continue

            # Calculate how many sheets we need
            needed_qty = -(-len(fitting_shapes) // shapes_per_sheet)  # Ceiling division
            available_qty = int(sheet.qty_available)
            use_qty = min(needed_qty, available_qty)

            if use_qty > 0:
                # Calculate how many shapes we can actually assign with available sheets
                max_shapes_to_assign = use_qty * shapes_per_sheet

                # Assign shapes up to the capacity
                assigned_shapes = fitting_shapes[:max_shapes_to_assign]

                if assigned_shapes:
                    sheets[sheet.id] = {
                        'name': sheet.name,
                        'used_quantity': use_qty,
                        'shapes': assigned_shapes,
                        'box': Box(int(sheet_width * MM), int(sheet_height * MM)),
                        'width': sheet_width,
                        'height': sheet_height,
                    }

                    # Remove only assigned shapes from remaining shapes
                    remaining_shapes = [s for s in remaining_shapes if s not in assigned_shapes]

        if remaining_shapes:
            raise UserError(
                f"Unable to assign {len(remaining_shapes)} shape(s) to available stock sheets. Please check stock availability.")

        return sheets

    def _snap_to_grid(self, value, grid_size=1.0, tolerance=0.5):
        """Snap a coordinate to the nearest grid point if within tolerance"""
        rounded = round(value / grid_size) * grid_size
        if abs(value - rounded) < tolerance:
            return rounded
        return value

    def _snap_vertices(self, vertices, grid_size=1.0, tolerance=0.5):
        """Snap all vertices in a list to nearest grid points"""
        snapped = []
        for x, y in vertices:
            snapped_x = self._snap_to_grid(x, grid_size, tolerance)
            snapped_y = self._snap_to_grid(y, grid_size, tolerance)
            snapped.append((snapped_x, snapped_y))
        return snapped

    def visualize_nesting_result_bins(self, sheet_name, sheet_width, sheet_height, pgrp):
        """
        Return a LIST of dicts:
          [{ 'base64': ..., 'sheet_name': ..., 'bin_index': 1, 'items_count': ... }, ...]
        One image per bin.
        """
        import base64
        import io
        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        results = []
        num_bins = len(pgrp or [])
        if num_bins == 0:
            return results

        colors = ['#ADD8E6', '#98FB98', '#FFB6C1', '#DDA0DD', '#F0E68C', '#87CEEB']

        for bin_idx, bin_items in enumerate(pgrp, start=1):
            # Create a fresh figure per bin
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.set_xlim(0, sheet_width)
            ax.set_ylim(0, sheet_height)
            ax.set_aspect('equal')

            # Sheet background
            ax.add_patch(
                patches.Rectangle(
                    (0, 0), sheet_width, sheet_height,
                    linewidth=2, edgecolor='black',
                    facecolor='lightgray', alpha=0.25
                )
            )

            # Draw items
            for idx, item in enumerate(bin_items):
                vertices = item.get_vertices()
                points = [(pt.x / MM, pt.y / MM) for pt in vertices]

                # snap only for visualization
                points = self._snap_vertices(points, grid_size=1.0, tolerance=0.6)

                ax.add_patch(
                    patches.Polygon(
                        points,
                        closed=True,
                        fill=True,
                        facecolor=colors[idx % len(colors)],
                        edgecolor='#4A90E2',
                        alpha=0.75,
                        linewidth=1.2
                    )
                )

            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlabel('Width (mm)')
            ax.set_ylabel('Height (mm)')

            # Save to base64
            buffer = io.BytesIO()
            fig.savefig(buffer, dpi=200, bbox_inches='tight',
                        facecolor='white', edgecolor='none',
                        format='png', pad_inches=0.1)
            buffer.seek(0)
            img_b64 = base64.b64encode(buffer.read()).decode("utf-8")
            buffer.close()
            plt.close(fig)

            results.append({
                "base64": img_b64,
                "sheet_name": sheet_name,
                "bin_index": bin_idx,
                "items_count": len(bin_items),
            })

        return results

    def _calculate_waste_with_holes(self, bin_items, sheet_width, sheet_height):
        """Calculate actual waste area including holes between shapes"""
        if not bin_items:
            return sheet_width * sheet_height

        # Calculate total item area (actual material used)
        total_item_area = sum(item.area() for item in bin_items) / (MM * MM)

        # Calculate bounding box of all items
        all_vertices = []
        for item in bin_items:
            vertices = item.get_vertices()
            for vertex in vertices:
                all_vertices.append((vertex.x / MM, vertex.y / MM))

        if not all_vertices:
            return sheet_width * sheet_height

        # Find actual used rectangular area (bounding box)
        min_x = min(x for x, y in all_vertices)
        max_x = max(x for x, y in all_vertices)
        min_y = min(y for x, y in all_vertices)
        max_y = max(y for x, y in all_vertices)

        used_bounding_area = (max_x - min_x) * (max_y - min_y)
        sheet_area = sheet_width * sheet_height

        # Waste includes:
        # 1. Unused sheet area outside bounding box
        # 2. Holes/gaps inside bounding box between shapes
        unused_area_outside = sheet_area - used_bounding_area
        holes_area_inside = used_bounding_area - total_item_area

        total_waste = holes_area_inside

        return {
            'total_waste': abs(total_waste),
            'unused_outside': abs(unused_area_outside),
            'holes_inside': abs(holes_area_inside),
            'bounding_efficiency': abs((total_item_area / used_bounding_area) * 100 if used_bounding_area > 0 else 0)
        }

    def _print_nesting_statistics(self, nesting_results, spacing):
        print("\n" + "=" * 80)
        print("GLOBAL NESTING STATISTICS")
        print("=" * 80)

        global_sheet_area = 0.0
        global_used_area = 0.0
        global_waste_area = 0.0
        global_holes_area = 0.0
        global_unused_area = 0.0
        used_sheet_ids = []
        total_bins_used = 0

        # -------- GLOBAL CALC --------
        for sheet_id, data in nesting_results.items():
            sheet_area = data['sheet_width'] * data['sheet_height']
            bins = data['bins']
            used_bins = len(bins)

            if used_bins > 0:
                used_sheet_ids.append({
                    'id': sheet_id,
                    'name': data['sheet_name'],
                    'bins': used_bins,
                    'quantity': data['sheet_count']
                })
                total_bins_used += used_bins

            total_used = 0.0
            total_waste = 0.0
            total_holes = 0.0
            total_unused = 0.0

            for bin_items in bins:
                bin_used_area = sum(item.area() for item in bin_items) / (MM * MM)
                waste_info = self._calculate_waste_with_holes(bin_items, data['sheet_width'], data['sheet_height'])

                total_used += bin_used_area
                total_waste += waste_info['total_waste']
                total_holes += waste_info['holes_inside']
                total_unused += waste_info['unused_outside']

            total_sheet = sheet_area * used_bins

            global_sheet_area += total_sheet
            global_used_area += total_used
            global_waste_area += total_waste
            global_holes_area += total_holes
            global_unused_area += total_unused

        # Store calculated values in model fields
        self.write({
            'total_used_area': global_used_area,
            'total_wasted_area': global_waste_area,
            'cut_blade_kerf_thickness': spacing,
            'panels': len(
                [item for data in nesting_results.values() for bin_items in data['bins'] for item in bin_items]),
            'used_stock_sheets': [(6, 0, [info['id'] for info in used_sheet_ids])]
        })

        # Display used sheet IDs
        print("USED SHEET IDs:")
        for sheet_info in used_sheet_ids:
            print(
                f"    Sheet ID {sheet_info['id']}: {sheet_info['name']} - {sheet_info['bins']} bins used (Available: {sheet_info['quantity']})")

        print(f"""
    Total Bins Used      : {total_bins_used}
    Total Sheets Area    : {global_sheet_area:.2f} mm²
    Total Used Area      : {global_used_area:.2f} mm²
    Total Waste Area     : {global_waste_area:.2f} mm²
      - Unused Outside   : {global_unused_area:.2f} mm²
      - Holes Inside     : {global_holes_area:.2f} mm²
    Global Efficiency    : {(global_used_area / global_sheet_area * 100):.2f}% 
    Kerf/Blade Thickness : {spacing} mm
    """)

        print("\n" + "=" * 80)
        print("PER SHEET TYPE STATISTICS")
        print("=" * 80)

        # -------- PER SHEET TYPE --------
        for sheet_id, data in nesting_results.items():
            sheet_area = data['sheet_width'] * data['sheet_height']
            bins = data['bins']
            used_bins = len(bins)

            if used_bins == 0:
                continue

            total_used = 0.0
            total_waste = 0.0
            total_holes = 0.0
            total_unused = 0.0
            avg_bounding_efficiency = 0.0

            for bin_items in bins:
                bin_used_area = sum(item.area() for item in bin_items) / (MM * MM)
                waste_info = self._calculate_waste_with_holes(bin_items, data['sheet_width'], data['sheet_height'])

                total_used += bin_used_area
                total_waste += waste_info['total_waste']
                total_holes += waste_info['holes_inside']
                total_unused += waste_info['unused_outside']
                avg_bounding_efficiency += waste_info['bounding_efficiency']

            total_sheet = sheet_area * used_bins
            sheet_efficiency = (total_used / total_sheet) * 100 if total_sheet > 0 else 0
            avg_bounding_efficiency = avg_bounding_efficiency / used_bins if used_bins > 0 else 0

            print(f"""
    Stock Sheet ID       : {sheet_id}
    Sheet Name           : {data['sheet_name']}
    Sheet Size           : {data['sheet_width']} x {data['sheet_height']} mm
    Available Quantity   : {data['sheet_count']}
    Bins Used            : {used_bins}
    Total Sheet Area     : {total_sheet:.2f} mm²
    Total Used Area      : {total_used:.2f} mm²
    Total Waste Area     : {total_waste:.2f} mm²
      - Unused Outside   : {total_unused:.2f} mm²
      - Holes Inside     : {total_holes:.2f} mm²
    Sheet Efficiency     : {sheet_efficiency:.2f}%
    Avg Bounding Efficiency : {avg_bounding_efficiency:.2f}%
    --------------------------------------------------
    """)

        print("=" * 80 + "\n")
        print(f"RESULTS SAVED TO SALE ORDER FIELDS:")
        print(f"  Total Used Area: {self.total_used_area:.2f} mm²")
        print(f"  Total Wasted Area: {self.total_wasted_area:.2f} mm²")
        print(f"  Cut Blade Kerf Thickness: {self.cut_blade_kerf_thickness} mm")
        print(f"  Total Shapes Count: {self.panels}")
        print(f"  Used Stock Sheets: {len(self.used_stock_sheets)} sheet types")
        print("=" * 80 + "\n")

    def action_calculate(self):
        self.ensure_one()

        shapes = self._get_shapes()

        if not shapes:
            return

        sheets = self._get_sheets(shapes)

        nesting_results = {}
        created_attachments = []

        # Clear previous nesting result attachments
        old_attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('name', 'ilike', 'Nesting Result:%')
        ])
        old_attachments.unlink()

        # Run nesting for each sheet and create attachments
        for sheet_id, sheet_data in sheets.items():
            box = sheet_data['box']
            sheet_shapes = sheet_data['shapes']
            sheet_name = sheet_data['name']
            sheet_count = sheet_data['used_quantity']
            sheet_width = sheet_data['width']
            sheet_height = sheet_data['height']

            print(f"\n\nProcessing sheet: {sheet_name}")
            print(f"Assigned shapes: {len(sheet_shapes)}")
            print(f"Sheet dimensions: {sheet_width} x {sheet_height} mm")

            # Run nesting with NFP algorithm
            pgrp = nest(sheet_shapes, box,
                        placer_type=PlacerType.NFP,
                        selector_type=SelectorType.DJDHeuristic,
                        spacing=self.spacing)

            nesting_results[sheet_id] = {
                'sheet_name': sheet_name,
                'sheet_width': sheet_width,
                'sheet_height': sheet_height,
                'sheet_count': sheet_count,
                'bins': pgrp,
            }

            # Get visualization data and create attachment
            viz_bins = self.visualize_nesting_result_bins(sheet_name, sheet_width, sheet_height, pgrp)

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

        self._print_nesting_statistics(nesting_results, spacing=0)

        # Print attachment summary
        if created_attachments:
            print(f"\n{'=' * 80}")
            print("CREATED NESTING RESULT ATTACHMENTS")
            print("=" * 80)
            for attachment in created_attachments:
                print(f"Attachment ID {attachment.id}: {attachment.name}")
                print(f"  Description: {attachment.description}")
            print("=" * 80)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
