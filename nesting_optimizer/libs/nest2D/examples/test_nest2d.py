import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

matplotlib.use('TkAgg')

try:
    from nest2D import Item
except ImportError as e:
    print("Error importing nest2D module.")
    raise e

MM = 1000000


def snap_to_grid(value, grid_size=1.0, tolerance=0.5):
    """Snap a coordinate to the nearest grid point if within tolerance"""
    rounded = round(value / grid_size) * grid_size
    if abs(value - rounded) < tolerance:
        return rounded
    return value


def snap_vertices(vertices, grid_size=1.0, tolerance=0.5):
    """Snap all vertices in a list to nearest grid points"""
    snapped = []
    for x, y in vertices:
        snapped_x = snap_to_grid(x, grid_size, tolerance)
        snapped_y = snap_to_grid(y, grid_size, tolerance)
        snapped.append((snapped_x, snapped_y))
    return snapped


def add_rect_shape(n, shapes):
    """Add n rectangular shapes (100x100mm)"""
    for i in range(n):
        item = Item([(0.0, 0.0), (0.0, 100.0), (100.0, 100.0), (100.0, 0.0), (0, 0)])
        print(item)
        shapes.append(item)


def add_triangle_shape(n, shapes):
    """Add n right triangle shapes (95x95mm)"""
    for i in range(n):
        item = Item([(0, 0), (0, 68), (68, 0), (0, 0)])
        shapes.append(item)


def test_bottom_left_packing():
    """Test strict bottom-left packing with NFP algorithm"""

    # Set up sheet dimensions
    # sheet_w = 420  # mm
    # sheet_h = 420  # mm
    # box = Box(sheet_w, sheet_h)

    # Create shapes: 1 square + 4 triangles
    shapes = []
    add_rect_shape(1, shapes)  # 1 rectangle (100x100)
    # add_triangle_shape(4, shapes)  # 4 triangles (95x95)

    # print("=" * 60)
    # print("NESTING WITH NFP ALGORITHM - BOTTOM-LEFT PRIORITY")
    # print("=" * 60)
    # print(f"Sheet size: {sheet_w} x {sheet_h} mm")
    # print(f"Shapes: 1 square (100x100) + 4 triangles (95x95)")
    # print()

    # Run nesting with NFP and FirstFit
    # pgrp = nest(shapes, box,
    #             placer_type=PlacerType.NFP,
    #             # selector_type=SelectorType.DJDHeuristic,
    #             selector_type=SelectorType.FirstFit,
    #             spacing=0)
    #
    # # Print results with coordinate snapping
    # print("PLACEMENT RESULTS (after coordinate snapping):")
    # print("-" * 60)
    # print(f"Number of bins used: {len(pgrp)}")
    #
    # shape_idx = 0
    # for bin_idx, bin_items in enumerate(pgrp):
    #     print(f"\nBin {bin_idx + 1}: {len(bin_items)} items")
    #
    #     for item_idx, item in enumerate(bin_items):
    #         vertices = item.get_points()
    #         print(vertices)
    #         points = vertices
    #
    #         # Snap coordinates to clean values
    #         snapped_points = snap_vertices(points, grid_size=1.0, tolerance=0.6)
    #
    #         shape_type = "Square" if shape_idx == 0 else f"Triangle {shape_idx}"
    #         print(f"  Item {item_idx + 1}: {snapped_points}")
    #         shape_idx += 1
    #
    # # Visualize the result - handle multiple bins
    # num_bins = len(pgrp)
    # if num_bins > 1:
    #     # Multiple bins - show side by side
    #     fig, axes = plt.subplots(1, num_bins, figsize=(num_bins * 6, 6))
    #     if num_bins == 1:
    #         axes = [axes]  # Make it a list for consistency
    # else:
    #     # Single bin
    #     fig, ax = plt.subplots(figsize=(8, 8))
    #     axes = [ax]
    #
    # # Draw packed shapes for each bin
    # colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink', 'cyan', 'yellow']
    #
    # for bin_idx, (bin_items, ax) in enumerate(zip(pgrp, axes)):
    #     ax.set_xlim(0, sheet_w)
    #     ax.set_ylim(0, sheet_h)
    #     ax.set_aspect('equal')
    #
    #     # Draw sheet background
    #     ax.add_patch(patches.Rectangle((0, 0), sheet_w, sheet_h,
    #                                    linewidth=2, edgecolor='black',
    #                                    facecolor='lightgray', alpha=0.3))
    #
    #     # Draw items in this bin
    #     for idx, item in enumerate(bin_items):
    #         vertices = item.get_points()
    #         points = vertices
    #
    #         # Snap for visualization
    #         snapped_points = snap_vertices(points, grid_size=1.0, tolerance=0.6)
    #
    #         color = colors[idx % len(colors)]
    #         shape_polygon = patches.Polygon(snapped_points, closed=True,
    #                                         fill=True, facecolor=color,
    #                                         edgecolor='black', alpha=0.7,
    #                                         linewidth=2)
    #         ax.add_patch(shape_polygon)
    #
    #         # Add label at center
    #         if len(snapped_points) > 0:
    #             center_x = sum(p[0] for p in snapped_points) / len(snapped_points)
    #             center_y = sum(p[1] for p in snapped_points) / len(snapped_points)
    #             ax.text(center_x, center_y, f"#{idx + 1}",
    #                     ha='center', va='center', fontsize=10, fontweight='bold')
    #
    #     ax.set_title(f'Bin {bin_idx + 1} ({len(bin_items)} items)', fontsize=12, fontweight='bold')
    #     ax.grid(True, alpha=0.3, linestyle='--')
    #     ax.set_xlabel('Width (mm)', fontsize=10)
    #     ax.set_ylabel('Height (mm)', fontsize=10)
    #
    #     # Add utilization info
    #     total_area = sum(item.area() for item in bin_items)
    #     bin_area = sheet_w * sheet_h
    #     utilization = (total_area / bin_area) * 100
    #     ax.text(10, sheet_h - 20, f'Utilization: {utilization:.1f}%',
    #             fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    #
    # # Overall title
    # if num_bins > 1:
    #     fig.suptitle(f'NFP Bottom-Left Packing Result - {num_bins} Bins', fontsize=14, fontweight='bold')
    # else:
    #     axes[0].set_title('NFP Bottom-Left Packing Result - Single Bin', fontsize=14, fontweight='bold')
    #
    # plt.tight_layout()
    # plt.show()
    #
    # print("\n" + "=" * 60)
    # print("VISUALIZATION COMPLETE")
    # print("=" * 60)


if __name__ == '__main__':
    test_bottom_left_packing()
