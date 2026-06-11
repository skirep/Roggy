"""Tests for the recipe catalog."""

from __future__ import annotations

import pytest

from meal_planner.recipes import (
    RECIPES,
    find_recipe,
    get_all_ingredients,
    get_recipes_by_tag,
    get_recipes_by_type,
)


class TestRecipeCatalog:
    def test_catalog_not_empty(self):
        assert len(RECIPES) > 0

    def test_all_meal_types_covered(self):
        types = {r.meal_type for r in RECIPES}
        assert {"breakfast", "lunch", "snack", "dinner"}.issubset(types)

    def test_get_recipes_by_type(self):
        for meal_type in ("breakfast", "lunch", "snack", "dinner"):
            found = get_recipes_by_type(meal_type)
            assert len(found) > 0, f"No recipes for meal type: {meal_type}"
            for r in found:
                assert r.meal_type == meal_type

    def test_get_recipes_by_tag(self):
        healthy = get_recipes_by_tag("healthy")
        assert len(healthy) > 0
        for r in healthy:
            assert "healthy" in r.tags

    def test_find_recipe_case_insensitive(self):
        r = find_recipe("oatmeal with fruit")
        assert r is not None
        assert r.name == "Oatmeal with Fruit"

    def test_find_recipe_missing(self):
        assert find_recipe("NonExistentRecipe") is None

    def test_all_ingredients_set(self):
        all_ings = get_all_ingredients()
        assert len(all_ings) > 10

    def test_recipe_ingredients_not_empty(self):
        for r in RECIPES:
            assert r.ingredients, f"{r.name} has no ingredients"

    def test_recipe_units_match_ingredients(self):
        for r in RECIPES:
            for ing in r.ingredients:
                assert ing in r.ingredient_units, (
                    f"{r.name}: ingredient '{ing}' has no unit"
                )

    def test_recipe_cost_positive(self):
        for r in RECIPES:
            assert r.cost_per_person > 0, f"{r.name} has non-positive cost"

    def test_recipe_prep_time_non_negative(self):
        for r in RECIPES:
            assert r.prep_time_minutes >= 0, f"{r.name} has negative prep time"

    def test_recipe_scale(self):
        r = find_recipe("Oatmeal with Fruit")
        scaled = r.scale(4)
        for ing, qty in r.ingredients.items():
            assert scaled.ingredients[ing] == pytest.approx(qty * 4)

    def test_recipe_total_cost(self):
        r = find_recipe("Oatmeal with Fruit")
        assert r.total_cost(4) == pytest.approx(r.cost_per_person * 4)

    def test_high_protein_recipes_exist(self):
        hp = get_recipes_by_tag("high-protein")
        assert len(hp) >= 5

    def test_vegetarian_recipes_exist(self):
        veg = get_recipes_by_tag("vegetarian")
        assert len(veg) >= 5

    def test_vegan_recipes_exist(self):
        vegan = get_recipes_by_tag("vegan")
        assert len(vegan) > 0

    def test_low_cost_recipes_exist(self):
        lc = get_recipes_by_tag("low-cost")
        assert len(lc) > 0
