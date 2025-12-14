from odoo import models, fields, api
import base64
import matplotlib
import ezdxf

matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io
import tempfile


class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
                        points.append((start[0], start[1]))
                        # points.append((end[0], end[1]))

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

                return base64.b64encode(image_data)

        except Exception as e:
            # Log the error but don't raise it to prevent blocking other operations
            print(f"Error converting DXF to image: {str(e)}")
            return False
