try:
    from odoo import models, api
    from io import BytesIO

    import base64
    import tempfile
    import ezdxf
    import json
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use('Agg')

except ImportError as e:
    raise ImportError("ImportError occurred in convertor model: {}".format(e))


class Convertor(models.AbstractModel):
    _name = 'convertor'
    _description = 'Convertor Mixin Model'

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
                    raise ValueError("Can't read this DXF file.")

                points = [(entity.dxf.start[0], entity.dxf.start[1])
                          for entity in entities if entity.dxftype() == 'LINE']

                if not points:
                    raise ValueError("No Shape found in DXF file.")

                points.append(points[0])

                x, y = zip(*points)

                shape = {
                    'points': points[::-1],
                    'width': max(x) - min(x),
                    'height': max(y) - min(y),
                }

                json_shape = json.dumps(shape)

                return json_shape

        except Exception as error:
            print(f"Error converting DXF to image: {str(error)}")
            raise ValueError("Failed to convert DXF file to shape.")

    @api.model
    def convert_shape_to_image1920(self, json_shape):
        """Convert shape points to PNG image and return image data with dimensions."""
        try:
            shape = json.loads(json_shape)
            points = shape.get('points', [])

            if not points:
                raise ValueError("Shape points are empty.")

            x, y = zip(*points)

            fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
            ax.plot(x, y)
            ax.set_aspect('equal')
            ax.fill(x, y, color='#ADD8E6', alpha=1)
            plt.axis('off')

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight',
                        facecolor='white', edgecolor='none', dpi=150)
            plt.close(fig)

            buf.seek(0)
            image_data = buf.read()
            buf.close()

            image = base64.b64encode(image_data)
            width = shape.get('width', 0)
            height = shape.get('height', 0)

            return image, width, height

        except Exception as error:
            print(f"Error converting shape to image: {str(error)}")
            raise ValueError("Failed to convert shape points to image.")
