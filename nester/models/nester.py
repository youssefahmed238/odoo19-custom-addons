try:
    from odoo import models, api
    from nest2D import nest, Item, Config, Placer, Selector

    import base64
    import io
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    matplotlib.use('Agg')

except ImportError as e:
    raise ImportError("ImportError occurred in nester model: {}".format(e))


class Nester(models.AbstractModel):
    _name = 'nester'
    _description = 'Nester Mixin Model'
    _inherit = ['convertor', 'sheet']

    def snap_to_grid(self, value, grid_size=1.0, tolerance=0.5):

        """Snap a coordinate to the nearest grid point if within tolerance"""
        rounded = round(value / grid_size) * grid_size
        if abs(value - rounded) < tolerance:
            return rounded
        return value

    def snap_vertices(self, vertices, grid_size=1.0, tolerance=0.5):
        """Snap all vertices in a list to nearest grid points"""
        snapped = []
        for x, y in vertices:
            snapped_x = self.snap_to_grid(x, grid_size, tolerance)
            snapped_y = self.snap_to_grid(y, grid_size, tolerance)
            snapped.append((snapped_x, snapped_y))
        return snapped

    def visualize_nesting_result_bins(self, sheet_name, sheet_width, sheet_height, pgrp):
        """
        Return a LIST of dicts:
          [{ 'base64': ..., 'sheet_name': ..., 'bin_index': 1, 'items_count': ... }, ...]
        One image per bin.
        """

        results = []
        num_bins = len(pgrp or [])
        if num_bins == 0:
            return results

        colors = ['#ADD8E6', '#98FB98', '#FFB6C1', '#DDA0DD', '#F0E68C', '#87CEEB']

        for bin_idx, bin_items in enumerate(pgrp):
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
                vertices = item.get_points()
                points = vertices

                # snap only for visualization
                points = self.snap_vertices(points, grid_size=1.0, tolerance=0.6)

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

    @api.model
    def nest(self, sheets):
        """Perform nesting of shapes onto sheets using nest2D library."""
        self.ensure_one()

        nesting_results = {}

        for sheet_id, sheet_data in sheets.items():
            box = sheet_data['box']
            sheet_shapes = sheet_data['shapes']
            sheet_name = sheet_data['name']
            sheet_count = sheet_data['used_quantity']
            sheet_width = sheet_data['width']
            sheet_height = sheet_data['height']

            # s = [
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #     Item([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
            #
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #     Item([(0, 0), (0, 68), (68, 0), (0, 0)]),
            #
            # ]

            config = Config(Placer.NFP, Selector.FirstFit)

            result = nest(sheet_shapes, box, 0, config)

            nesting_results[sheet_id] = {
                'sheet_name': sheet_name,
                'sheet_width': sheet_width,
                'sheet_height': sheet_height,
                'sheet_count': sheet_count,
                'bins': result.output,
            }

            return self.visualize_nesting_result_bins(sheet_name, sheet_width, sheet_height, result.output)
