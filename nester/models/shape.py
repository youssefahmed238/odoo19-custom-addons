try:
    from odoo import models, api
    from nest2D import Item

    import json

except ImportError as e:
    raise ImportError("ImportError occurred in shape model: {}".format(e))


class Shape(models.AbstractModel):
    _name = 'shape'
    _description = 'Shape Mixin Model'

    @api.model
    def scale_points(self, shape, target_width, target_height):
        """Scale points to fit within specified width and height."""
        points = shape.get('points', [])

        orig_width = shape.get('width', 0)
        orig_height = shape.get('height', 0)

        scale_x = target_width / orig_width
        scale_y = target_height / orig_height

        scaled = []
        for x, y in points:
            new_x = x * scale_x
            new_y = y * scale_y
            scaled.append((new_x, new_y))

        return scaled

    @api.model
    def get_shape(self, json_shape, qty, target_width, target_height):
        """Get shape data including scaled points and dimensions."""
        shape = json.loads(json_shape)

        item = Item(self.scale_points(shape, target_width, target_height))

        shape.update({
            "item": item,
            "width": target_width,
            "height": target_height,
            "area": item.area(),
            "qty": qty,
            "used_qty": 0,  # Initialize used quantity to 0
            "remaining_qty": qty,  # Initialize remaining quantity to requested quantity
        })

        return shape

    @api.model
    def sort_shapes_by_area(self, shapes):
        """Sort shapes by area in descending order (largest first)."""
        return sorted(shapes, key=lambda shape: shape['area'], reverse=True)

    @api.model
    def print_shapes(self, shapes):
        """Print shape details for debugging."""
        for shape in shapes:
            print(f"Shape: {shape.get('name', 'Unnamed')}")
            print(f" ==== Width: {shape.get('width', 0)}")
            print(f" ==== Height: {shape.get('height', 0)}")
            print(f" ==== Area: {shape.get('area', 0)}")
            print(f" ==== Quantity: {shape.get('qty', 0)}")
            print(f" ==== Used Quantity: {shape.get('used_qty', 0)}")
            print(f" ==== Remaining Quantity: {shape.get('remaining_qty', 0)}")
            print("#" * 50)

        print("\n")
