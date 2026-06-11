"""Command-line interface for the Weekly Meal Planner."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from typing import List, Optional

from .database import Database
from .formatter import MealPlanFormatter
from .models import PantryItem, UserPreferences
from .pantry import PantryManager
from .planner import MealPlanner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_preferences(args: argparse.Namespace) -> UserPreferences:
    dietary: set = set()
    if getattr(args, "vegetarian", False):
        dietary.add("vegetarian")
    if getattr(args, "vegan", False):
        dietary.add("vegan")
    if hasattr(args, "diet") and args.diet:
        for d in args.diet:
            dietary.add(d.lower())

    excluded: set = set()
    if hasattr(args, "exclude") and args.exclude:
        excluded = {e.lower() for e in args.exclude}

    preferred: set = set()
    if hasattr(args, "prefer") and args.prefer:
        preferred = {p.lower() for p in args.prefer}

    adults = getattr(args, "adults", 2) or 2
    children = getattr(args, "children", 0) or 0

    return UserPreferences(
        adults_count=adults,
        children_count=children,
        people=adults + children,
        dietary_restrictions=dietary,
        excluded_ingredients=excluded,
        preferred_tags=preferred,
        max_prep_time_minutes=getattr(args, "max_prep_time", None),
        weekly_budget=getattr(args, "budget", None),
    )


def _parse_date(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        print(f"Error: invalid date '{s}'. Expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Sub-commands
# ---------------------------------------------------------------------------


def cmd_generate(args: argparse.Namespace, db: Database) -> None:
    """Generate a new weekly meal plan."""
    preferences = _build_preferences(args)
    pantry = PantryManager(db)
    planner = MealPlanner(db, pantry)
    formatter = MealPlanFormatter()

    week_start: Optional[date] = None
    if getattr(args, "week_start", None):
        week_start = _parse_date(args.week_start)

    mode = getattr(args, "mode", "default") or "default"

    plan = planner.generate_week(preferences=preferences, week_start=week_start, mode=mode)

    if getattr(args, "save", False):
        planner.save_plan_to_history(plan)
        print("Plan saved to history.\n")

    print(formatter.format_plan(plan))


def cmd_pantry(args: argparse.Namespace, db: Database) -> None:
    """Manage pantry inventory."""
    pantry = PantryManager(db)
    sub = args.pantry_cmd

    if sub == "list":
        items = pantry.get_all()
        if not items:
            print("Pantry is empty.")
            return
        print(f"{'Ingredient':<25}{'Quantity':>10}  {'Unit':<8}  {'Expiry'}")
        print("-" * 60)
        for item in items:
            exp = item.expiry_date.isoformat() if item.expiry_date else "—"
            print(f"{item.name:<25}{item.quantity:>10.2f}  {item.unit:<8}  {exp}")

    elif sub == "add":
        expiry = _parse_date(args.expiry) if getattr(args, "expiry", None) else None
        item = PantryItem(name=args.name, quantity=args.quantity, unit=args.unit, expiry_date=expiry)
        pantry.add_item(item)
        print(f"Added/updated: {args.name} ({args.quantity} {args.unit})")

    elif sub == "remove":
        pantry.remove_item(args.name)
        print(f"Removed: {args.name}")

    elif sub == "clear":
        pantry.clear()
        print("Pantry cleared.")

    else:
        print(f"Unknown pantry sub-command: {sub}", file=sys.stderr)
        sys.exit(1)


def cmd_history(args: argparse.Namespace, db: Database) -> None:
    """View or rate meal history."""
    sub = args.history_cmd

    if sub == "list":
        limit = getattr(args, "limit", 20) or 20
        meal_type = getattr(args, "meal_type", None)
        records = db.get_meal_history(limit=limit, meal_type=meal_type)
        if not records:
            print("No meal history found.")
            return
        print(f"{'Date':<12}{'Type':<12}{'Recipe':<35}{'People':>7}  {'Rating'}")
        print("-" * 75)
        for r in records:
            rating = str(r.user_rating) if r.user_rating else "—"
            print(f"{r.meal_date.isoformat():<12}{r.meal_type:<12}{r.recipe_name:<35}{r.people:>7}  {rating}")

    elif sub == "rate":
        db.update_meal_feedback(
            meal_id=args.id,
            user_rating=getattr(args, "rating", None),
            family_feedback=getattr(args, "feedback", None),
        )
        print(f"Updated feedback for meal #{args.id}")

    else:
        print(f"Unknown history sub-command: {sub}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meal_planner",
        description="Roggy Weekly Meal Planner",
    )
    parser.add_argument(
        "--db",
        default="meal_planner.db",
        metavar="PATH",
        help="Path to SQLite database (default: meal_planner.db)",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    # ------------------------------------------------------------------ #
    # generate
    # ------------------------------------------------------------------ #
    gen = subparsers.add_parser("generate", help="Generate a weekly meal plan")
    gen.add_argument("--adults", type=int, default=2, metavar="N", help="Number of adults (default 2)")
    gen.add_argument("--children", type=int, default=0, metavar="N", help="Number of children (default 0)")
    gen.add_argument(
        "--mode",
        choices=["default", "low-cost", "healthy", "high-protein", "pantry-only"],
        default="default",
        help="Planning mode",
    )
    gen.add_argument("--week-start", metavar="YYYY-MM-DD", help="Monday of the target week")
    gen.add_argument("--budget", type=float, metavar="AMOUNT", help="Weekly budget limit")
    gen.add_argument("--max-prep-time", type=int, metavar="MINUTES", help="Max prep time per meal (minutes)")
    gen.add_argument(
        "--diet",
        nargs="+",
        metavar="TAG",
        help="Dietary restrictions (e.g. vegetarian vegan gluten-free)",
    )
    gen.add_argument("--exclude", nargs="+", metavar="INGREDIENT", help="Ingredients to exclude")
    gen.add_argument("--prefer", nargs="+", metavar="TAG", help="Preferred tags (e.g. healthy high-protein)")
    gen.add_argument("--save", action="store_true", help="Save generated plan to meal history")
    gen.set_defaults(func=cmd_generate)

    # ------------------------------------------------------------------ #
    # pantry
    # ------------------------------------------------------------------ #
    pantry_p = subparsers.add_parser("pantry", help="Manage pantry inventory")
    pantry_sub = pantry_p.add_subparsers(dest="pantry_cmd")
    pantry_sub.required = True

    pantry_sub.add_parser("list", help="List pantry items")

    add_p = pantry_sub.add_parser("add", help="Add or update a pantry item")
    add_p.add_argument("name", help="Ingredient name")
    add_p.add_argument("quantity", type=float, help="Quantity available")
    add_p.add_argument("unit", help="Unit (kg, L, unit, etc.)")
    add_p.add_argument("--expiry", metavar="YYYY-MM-DD", help="Expiry date")

    rem_p = pantry_sub.add_parser("remove", help="Remove a pantry item")
    rem_p.add_argument("name", help="Ingredient name to remove")

    pantry_sub.add_parser("clear", help="Remove all pantry items")
    pantry_p.set_defaults(func=cmd_pantry)

    # ------------------------------------------------------------------ #
    # history
    # ------------------------------------------------------------------ #
    hist_p = subparsers.add_parser("history", help="View and rate meal history")
    hist_sub = hist_p.add_subparsers(dest="history_cmd")
    hist_sub.required = True

    list_h = hist_sub.add_parser("list", help="List meal history")
    list_h.add_argument("--limit", type=int, default=20, metavar="N", help="Number of records (default 20)")
    list_h.add_argument("--meal-type", choices=["breakfast", "lunch", "snack", "dinner"])

    rate_h = hist_sub.add_parser("rate", help="Rate a meal and add feedback")
    rate_h.add_argument("id", type=int, help="Meal history record ID")
    rate_h.add_argument("--rating", type=int, choices=range(1, 6), metavar="1-5", help="User rating (1-5)")
    rate_h.add_argument("--feedback", metavar="TEXT", help="Family feedback")

    hist_p.set_defaults(func=cmd_history)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    db = Database(db_path=args.db)
    args.func(args, db)


if __name__ == "__main__":
    main()
