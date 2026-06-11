"""Output formatting for the Weekly Meal Planner."""

from __future__ import annotations

from typing import List, Optional

from .models import DayPlan, MealPlan, MealSlot


# Column widths for the weekly table
_DAY_WIDTH = 10
_MEAL_WIDTH = 30


class MealPlanFormatter:
    """Formats a MealPlan into human-readable text."""

    def format_plan(self, plan: MealPlan) -> str:
        """Return a full text report of the meal plan."""
        lines: List[str] = []

        lines.append("=" * 78)
        lines.append(
            f"  WEEKLY MEAL PLAN  |  Week of {plan.week_start.strftime('%B %d, %Y')}"
            f"  |  {plan.people} {'person' if plan.people == 1 else 'people'}"
        )
        lines.append("=" * 78)
        lines.append("")

        # Weekly table
        lines.append(self._format_table(plan.days))
        lines.append("")

        # Per-day detail
        for day in plan.days:
            lines.append(self._format_day_detail(day))

        # Shopping list
        lines.append(self._format_shopping_list(plan))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Weekly overview table
    # ------------------------------------------------------------------

    def _format_table(self, days: List[DayPlan]) -> str:
        meal_types = ["breakfast", "lunch", "snack", "dinner"]
        header_row = f"{'Meal':<12}" + "".join(f"{d.day_name():<14}" for d in days)
        separator = "-" * len(header_row)

        rows = [header_row, separator]
        for mt in meal_types:
            row = f"{mt.capitalize():<12}"
            for day in days:
                slot: Optional[MealSlot] = day.meals().get(mt)
                if slot is not None:
                    name = slot.recipe.name
                    # Truncate long names
                    if len(name) > 12:
                        name = name[:11] + "…"
                    row += f"{name:<14}"
                else:
                    row += f"{'—':<14}"
            rows.append(row)

        return "\n".join(rows)

    # ------------------------------------------------------------------
    # Per-day detail
    # ------------------------------------------------------------------

    def _format_day_detail(self, day: DayPlan) -> str:
        lines: List[str] = []
        lines.append(f"── {day.day_name()} {day.date.strftime('%Y-%m-%d')} " + "─" * 40)

        for mt, slot in day.meals().items():
            if slot is None:
                continue
            lines.append(f"  {mt.upper()}: {slot.recipe.name}")
            lines.append(
                f"    Prep time: {slot.recipe.prep_time_minutes} min  |"
                f"  ~{slot.recipe.calories_per_person} kcal  |"
                f"  ~{slot.recipe.protein_per_person:.0f}g protein"
            )

            # Pantry items used
            if slot.pantry_items_used:
                pantry_strs = [
                    f"{ing} ({qty:.2g} {slot.ingredient_units().get(ing, '')})"
                    for ing, qty in slot.pantry_items_used.items()
                ]
                lines.append(f"    ✔ From pantry : {', '.join(pantry_strs)}")

            # Items to purchase
            if slot.items_to_buy:
                buy_strs = [
                    f"{ing} ({qty:.2g} {slot.ingredient_units().get(ing, '')})"
                    for ing, qty in slot.items_to_buy.items()
                ]
                lines.append(f"    🛒 To purchase : {', '.join(buy_strs)}")

        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Shopping list
    # ------------------------------------------------------------------

    def _format_shopping_list(self, plan: MealPlan) -> str:
        lines: List[str] = []
        lines.append("=" * 78)
        lines.append("  CONSOLIDATED SHOPPING LIST")
        lines.append("=" * 78)

        if not plan.shopping_list.items:
            lines.append("  Everything can be made from the pantry! 🎉")
            lines.append("")
            return "\n".join(lines)

        col_name = 28
        col_qty = 10
        col_unit = 10
        col_cost = 10

        header = (
            f"  {'Ingredient':<{col_name}}"
            f"{'Qty':>{col_qty}}"
            f"  {'Unit':<{col_unit}}"
            f"{'Est. Cost':>{col_cost}}"
        )
        lines.append(header)
        lines.append("  " + "-" * (col_name + col_qty + col_unit + col_cost + 4))

        for item in plan.shopping_list.sorted_items():
            cost_str = f"${item.estimated_cost:.2f}" if item.estimated_cost else "—"
            lines.append(
                f"  {item.name:<{col_name}}"
                f"{item.quantity:>{col_qty}.2f}"
                f"  {item.unit:<{col_unit}}"
                f"{cost_str:>{col_cost}}"
            )

        lines.append("  " + "-" * (col_name + col_qty + col_unit + col_cost + 4))
        lines.append(
            f"  {'ESTIMATED TOTAL':<{col_name + col_qty + col_unit + 2}}"
            f"{'$' + f'{plan.total_estimated_cost:.2f}':>{col_cost}}"
        )
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Short summary
    # ------------------------------------------------------------------

    def format_summary(self, plan: MealPlan) -> str:
        """Return a one-paragraph summary."""
        n_items = len(plan.shopping_list.items)
        return (
            f"Meal plan for the week of {plan.week_start.strftime('%B %d, %Y')} "
            f"({plan.people} {'person' if plan.people == 1 else 'people'}).  "
            f"Shopping list: {n_items} item(s), "
            f"estimated cost: ${plan.total_estimated_cost:.2f}."
        )
