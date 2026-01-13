try:
    from odoo import models, api
    from odoo.exceptions import UserError

    from nest2D import Item

    from io import BytesIO

    import tempfile
    import base64
    import ezdxf
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use('Agg')

except ImportError as e:
    raise ImportError("Required libraries are not installed: {}".format(e))


class Nester(models.AbstractModel):
    _name = 'nester'
    _description = 'Nester Mixin Model'

    @api.model
    def convert_dxf_to_shape(self, dxf_shape):
        """Convert DXF binary data to shape points and dimensions."""
        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix='.dxf') as temp:
                dxf_bytes = base64.b64decode(dxf_shape)
                temp.write(dxf_bytes)
                temp.flush()
                temp_path = temp.name

                doc = ezdxf.readfile(temp_path)
                msp = doc.modelspace()
                entities = [entity for entity in msp if
                            entity.dxftype() in ['LINE', 'CIRCLE', 'ARC', 'LWPOLYLINE', 'POLYLINE']]

                if not entities:
                    return False

                points = []
                for entity in entities:
                    if entity.dxftype() == 'LINE':
                        end = entity.dxf.end
                        points.append((end[0], end[1]))

                if not points:
                    return False

                points.append(points[0])

                shape_points = '\n'.join([f"{pt[0]},{pt[1]}" for pt in points[::-1]])

                return shape_points

        except Exception as error:
            print(f"Error converting DXF to image: {str(error)}")
            raise UserError("Failed to convert DXF file to shape.")

    @api.model
    def convert_shape_to_image1920(self, shape_points):
        """Convert shape points to PNG image and return image data with dimensions."""
        try:
            points = []
            for line in shape_points.strip().split('\n'):
                x_str, y_str = line.split(',')
                points.append((float(x_str), float(y_str)))

            x_coords, y_coords = zip(*points)

            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
            ax.plot(x_coords, y_coords)
            ax.set_aspect('equal')
            ax.fill(x_coords, y_coords, color='#ADD8E6', alpha=1)
            plt.axis('off')

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight',
                        facecolor='white', edgecolor='none', dpi=150)
            plt.close(fig)

            buf.seek(0)
            image_data = buf.read()
            buf.close()

            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)

            return {
                'image': base64.b64encode(image_data),
                'width': width,
                'height': height
            }

        except Exception as error:
            print(f"Error converting shape to image: {str(error)}")
            raise UserError("Failed to convert shape points to image.")

    @api.model
    def scale_points(self, points, target_width, target_height):
        """Scale points to fit within specified width and height."""
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

        scale_x = target_width / orig_width
        scale_y = target_height / orig_height

        scaled = []
        for x, y in points:
            new_x = (x - min_x) * scale_x
            new_y = (y - min_y) * scale_y
            scaled.append((int(new_x), int(new_y)))

        return scaled

    @api.model
    def get_points(self, shape_points):
        """Extract points from shape points string."""
        points = []
        for line in shape_points.strip().split('\n'):
            x_str, y_str = line.split(',')
            points.append((float(x_str), float(y_str)))
        return points

    @api.model
    def get_shape(self, shape_points, qty, target_width, target_height):
        """Get shape data including scaled points and dimensions."""
        points = self.get_points(shape_points)

        scaled_points = self.scale_points(points, target_width, target_height)

        return [Item([
            (x, y) for x, y in scaled_points
        ])] * int(qty)
