from odoo.orm.models import BaseModel

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

    # =================================================================
    #  Sorting / Printing
    # =================================================================

    @api.model
    def sort_sheets_by_area(self, sheets):
        """Sort sheets smallest to largest by area."""
        return sorted(sheets, key=lambda s: (s.width * s.height, s.width, s.height))

    @api.model
    def get_sheets(self, sheets):
        return [{
            'sheet': sheet,
            'name': sheet.name,
            'width': sheet.width,
            'height': sheet.height,
            'area': sheet.width * sheet.height,
            'qty': sheet.qty_available,
            'required_qty': 0,  # Initialize used quantity to 0
            'remaining_qty': sheet.qty_available,  # Initialize remaining quantity to available quantity
        } for sheet in self.sort_sheets_by_area(sheets)]

    @api.model
    def print_sheets(self, sheets):
        """Print sheet details for debugging."""
        for sheet in sheets:
            print(f"Sheet: {sheet.get('name', 'Unknown')}")
            print(f"==== Width         : {sheet.get('width', 0)}")
            print(f"==== Height        : {sheet.get('height', 0)}")
            print(f"==== Area          : {sheet.get('area', 0)}")
            print(f"==== Qty           : {sheet.get('qty', 0)}")
            print(f"==== Used Qty      : {sheet.get('required_qty', 0)}")
            print(f"==== Remaining Qty : {sheet.get('remaining_qty', 0)}")
            print("#" * 50)
        print()

    @api.model
    def print_selected_sheets(self, shape, selected_sheets):
        """Print selected sheet combination."""

        print("\n" + "=" * 70)
        print(f"Shape    : {shape.get('name', 'Unknown')}")
        print(f"Qty      : {shape.get('qty', 0)}")
        print(f"Used Qty : {shape.get('required_qty', 0)}")
        print(f"Remaining: {shape.get('remaining_qty', 0)}")
        print("-" * 70)

        for sheet in selected_sheets:
            print(
                f"{sheet.get('name', 'Unknown'):<10}"
                f" Size: {sheet.get('width', 0)}x{sheet.get('height', 0)}"
                f" Used: {sheet.get('required_qty', 0)}/{sheet.get('qty', 0):<5}"
                f" Remaining: {sheet.get('remaining_qty', 0)}"
            )

        print("=" * 70)

    # =================================================================
    #  Sheet / Shape Helpers
    # =================================================================

    @api.model
    def is_shape_fitting(self, shape, sheet):
        """Return True if the shape fits on the sheet (normal or rotated)."""
        shape_width, shape_height = shape.get('width', 0), shape.get('height', 0)
        sheet_width, sheet_height = sheet.get('width', 0), sheet.get('height', 0)
        return (
                (shape_width <= sheet_width and shape_height <= sheet_height) or
                (shape_height <= sheet_width and shape_width <= sheet_height)
        )

    @api.model
    def shapes_per_sheet(self, sheet, shape_area):
        """How many copies of the shape fit on one sheet instance (by area)."""
        sheet_area = sheet.get('area', 0)
        return sheet_area // shape_area if shape_area else 0

    @api.model
    def sheets_needed(self, shape_qty, shapes_per_sheet):
        """Ceiling division: how many sheet instances cover shape_qty copies."""
        return -(-shape_qty // shapes_per_sheet) if shapes_per_sheet > 0 else 0

    # =================================================================
    #  Validation
    # =================================================================

    @api.model
    def _check_shape_fits_dimensionally(self, shape, fitting_sheets):
        """Raise if the shape does not fit dimensionally in any stock sheet."""
        if not fitting_sheets:
            raise UserError(
                f"Shape '{shape.get('name', 'Unknown')}' "
                f"({shape.get('width', 0)} × {shape.get('height', 0)}) "
                f"does not fit dimensionally in any available stock sheet."
            )

    @api.model
    def _check_stock_capacity(self, shape, fitting_sheets):
        """Raise if total stock capacity is less than shape quantity needed."""
        shape_qty = shape.get('remaining_qty', 0)
        shape_area = shape.get('area', 0)
        total_capacity = self.combination_capacity(fitting_sheets, shape_area)

        if total_capacity < shape_qty:
            raise UserError(
                f"Shape '{shape.get('name', 'Unknown')}' requires {shape_qty} piece(s), "
                f"but all fitting stock sheets combined can only hold {total_capacity} piece(s)."
            )

    @api.model
    def validate_sheet_selection(self, shape, sheets):
        """Run all validations before sheet selection. Returns only dimensionally fitting sheets."""
        fitting_sheets = [sheet for sheet in sheets if
                          sheet.get('remaining_qty', 0) > 0 and self.is_shape_fitting(shape, sheet)]

        self._check_shape_fits_dimensionally(shape, fitting_sheets)
        self._check_stock_capacity(shape, fitting_sheets)

        return fitting_sheets

    # =================================================================
    #  Combination Helpers
    # =================================================================

    @api.model
    def combination_capacity(self, combo, shape_area):
        """Total shape copies a list of sheets can hold at full qty_available."""
        return sum(
            self.shapes_per_sheet(sheet, shape_area) * sheet.get('remaining_qty', 0)
            for sheet in combo
        )

    @api.model
    def build_result(self, combo, last_sheet, last_sheet_required_qty):
        """
        Build the final assignment list.
        Every sheet in combo is used at full availability;
        last_sheet is used only for the remaining quantity.
        """
        result = []

        for sheet in combo:
            sheet.update({
                'required_qty': sheet.get('qty', 0)
            })
            result.append(sheet)

        last_sheet.update({
            'required_qty': last_sheet_required_qty
        })
        result.append(last_sheet)

        return result

    # =================================================================
    #  Single-sheet / Combo Checks
    # =================================================================

    @api.model
    def try_single_sheet(self, sheet, shape_qty, shape_area):
        """Return assignment if this sheet type alone can cover shape_qty, else None."""
        needed = self.sheets_needed(shape_qty, self.shapes_per_sheet(sheet, shape_area))
        if 0 < needed <= sheet.get('remaining_qty', 0):
            sheet.update({
                'required_qty': needed
            })
            return [sheet]
        return None

    @api.model
    def try_combination(self, combo, current_sheet, shape_qty, shape_area):
        """Return assignment if combo + current_sheet together cover shape_qty, else None."""
        remaining = shape_qty - self.combination_capacity(combo, shape_area)

        if remaining <= 0:
            return None  # combo alone was already enough (caught earlier)

        needed = self.sheets_needed(remaining, self.shapes_per_sheet(current_sheet, shape_area))
        if 0 < needed <= current_sheet.get('remaining_qty', 0):
            return self.build_result(combo, current_sheet, needed)

        return None

    # =================================================================
    #  Core Selection
    # =================================================================

    @api.model
    def select_sheets(self, shape, sheets):
        """
        Find the smallest set of sheet types that can hold all copies of `shape`.

        Strategy (greedy, smallest-first):
          1. Try each fitting sheet type alone.
          2. If one type is not enough, try it paired with every previously
             seen candidate combination until the total capacity is met.
          3. A valid combination is guaranteed to exist after validation.

        Returns: [{'sheet': <sheet>, 'required_qty': <int>}, ...]
        """
        shape_qty = shape.get('remaining_qty', 0)
        shape_area = shape.get('area', 0)

        # Validate and get only dimensionally fitting sheets
        fitting_sheets = self.validate_sheet_selection(shape, sheets)

        # Grows as we see more sheets.
        # Example after seeing A, B: [[A], [B], [A, B]]
        candidate_combos = []

        for sheet in fitting_sheets:

            # 1. Sheet alone
            result = self.try_single_sheet(sheet, shape_qty, shape_area)
            if result:
                return result

            # 2. Every known combo + this sheet
            new_combos = []
            for combo in candidate_combos:
                result = self.try_combination(combo, sheet, shape_qty, shape_area)
                if result:
                    return result
                new_combos.append(combo + [sheet])

            # Register sheet alone, then all extended combos, for future rounds
            candidate_combos.append([sheet])
            candidate_combos.extend(new_combos)

        raise AssertionError(
            f"select_sheets: no combination found for '{shape.get('name', 'Unknown')}' "
            f"despite passing validation. This should never happen."
        )
