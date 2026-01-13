from odoo import models, fields, api
import base64
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
import ezdxf
import io
import tempfile


class ProductTemplate(models.Model):
    _inherit = ['product.template', 'nester']

    dxf_shape = fields.Binary("DXF Shape")
    dxf_filename = fields.Char("DXF Filename")

    svg_shape = fields.Binary("SVG Shape")
    svg_filename = fields.Char("SVG Filename")

    shape_points = fields.Text("Shape Points")

    width = fields.Float("Width")
    height = fields.Float("Height")

    # shape = fields.Serialized("Shape Data")

    @api.onchange('dxf_shape')
    def _onchange_dxf_shape(self):
        if self.dxf_shape:
            shape_points = self.convert_dxf_to_shape(self.dxf_shape)
            if shape_points:
                self.shape_points = shape_points
                result = self.convert_shape_to_image1920(self.shape_points)
                if result:
                    self.image_1920 = result['image']
                    self.name = self.dxf_filename.rsplit('.', 1)[0]

                    # Set width and height directly in memory for immediate access
                    self.width = result['width']
                    self.height = result['height']

                    # Print the updated values after they're calculated and set
                    print(f"Updated width: {result['width']}")
                    print(f"Updated height: {result['height']}")

    def ensure_dimensions_calculated(self):
        """Ensure width and height are calculated from DXF if available"""
        self.ensure_one()
        if self.dxf_shape and (not self.width or not self.height):
            shape_points = self.convert_dxf_to_shape(self.dxf_shape)
            if shape_points:
                result = self.convert_shape_to_image1920(shape_points)
                if result:
                    self.width = result['width']
                    self.height = result['height']
                    return True
        return False










    dxf_file = fields.Binary("DXF File", attachment=True)

    def convert_dxf_to_image1920(self, dxf_data):
        """Convert DXF file to PNG image and set as product image"""
        self.ensure_one()

        try:
            with tempfile.NamedTemporaryFile(delete=True, suffix='.dxf') as temp:
                dxf_bytes = base64.b64decode(dxf_data)
                temp.write(dxf_bytes)
                temp.flush()
                temp_path = temp.name

                doc = ezdxf.readfile(temp_path)
                msp = doc.modelspace()
                entities = [e for e in msp if e.dxftype() in ['LINE', 'CIRCLE', 'ARC', 'LWPOLYLINE', 'POLYLINE']]

                if not entities:
                    return False

                points = []
                for entity in entities:
                    if entity.dxftype() == 'LINE':
                        start = entity.dxf.start
                        end = entity.dxf.end
                        # points.append((start[0], start[1]))
                        points.append((end[0], end[1]))

                if not points:
                    return False

                points.append(points[0])

                x, y = zip(*points)

                fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
                ax.plot(x, y)
                ax.set_aspect('equal')
                ax.fill(x, y, color='#ADD8E6', alpha=1)
                ax.axis('off')

                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', bbox_inches='tight',
                            facecolor='white', edgecolor='none', dpi=150)
                plt.close(fig)

                img_buffer.seek(0)
                image_data = img_buffer.read()
                img_buffer.close()

                return {
                    'image': base64.b64encode(image_data),
                    'width': max(x) - min(x),
                    'height': max(y) - min(y),
                    'shape_points': '\n'.join([f"{pt[0]},{pt[1]}" for pt in points[::-1]])
                }

        except Exception as e:
            # Log the error but don't raise it to prevent blocking other operations
            print(f"Error converting DXF to image: {str(e)}")
            return False
