"""Built-in recipe catalog for the Weekly Meal Planner."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from .models import Recipe

# ---------------------------------------------------------------------------
# Helper to build recipes consistently
# ---------------------------------------------------------------------------


def _recipe(
    name: str,
    meal_type: str,
    ingredients: Dict[str, float],
    units: Dict[str, str],
    cost_per_person: float,
    prep_time: int,
    tags: Set[str],
    calories: int = 0,
    protein: float = 0.0,
) -> Recipe:
    return Recipe(
        name=name,
        meal_type=meal_type,
        ingredients=ingredients,
        ingredient_units=units,
        cost_per_person=cost_per_person,
        prep_time_minutes=prep_time,
        tags=tags,
        calories_per_person=calories,
        protein_per_person=protein,
    )


# ---------------------------------------------------------------------------
# Recipe catalog
# ---------------------------------------------------------------------------

RECIPES: List[Recipe] = [
    # -----------------------------------------------------------------------
    # BREAKFAST
    # -----------------------------------------------------------------------
    _recipe(
        name="Oatmeal with Fruit",
        meal_type="breakfast",
        ingredients={"oats": 0.08, "milk": 0.2, "banana": 0.5, "honey": 0.02},
        units={"oats": "kg", "milk": "L", "banana": "unit", "honey": "kg"},
        cost_per_person=0.60,
        prep_time=10,
        tags={"healthy", "vegetarian", "low-cost", "kids-friendly"},
        calories=320,
        protein=9.0,
    ),
    _recipe(
        name="Scrambled Eggs on Toast",
        meal_type="breakfast",
        ingredients={"eggs": 2.0, "bread": 2.0, "butter": 0.01, "salt": 0.002},
        units={"eggs": "unit", "bread": "slice", "butter": "kg", "salt": "kg"},
        cost_per_person=0.90,
        prep_time=10,
        tags={"high-protein", "vegetarian", "kids-friendly"},
        calories=380,
        protein=22.0,
    ),
    _recipe(
        name="Greek Yogurt Parfait",
        meal_type="breakfast",
        ingredients={"greek_yogurt": 0.2, "granola": 0.04, "berries": 0.1, "honey": 0.01},
        units={"greek_yogurt": "kg", "granola": "kg", "berries": "kg", "honey": "kg"},
        cost_per_person=1.20,
        prep_time=5,
        tags={"healthy", "high-protein", "vegetarian", "no-cook"},
        calories=290,
        protein=18.0,
    ),
    _recipe(
        name="Avocado Toast",
        meal_type="breakfast",
        ingredients={"bread": 2.0, "avocado": 0.5, "lemon": 0.25, "olive_oil": 0.005, "salt": 0.001},
        units={"bread": "slice", "avocado": "unit", "lemon": "unit", "olive_oil": "L", "salt": "kg"},
        cost_per_person=1.40,
        prep_time=8,
        tags={"healthy", "vegetarian", "vegan"},
        calories=350,
        protein=8.0,
    ),
    _recipe(
        name="Pancakes",
        meal_type="breakfast",
        ingredients={
            "flour": 0.075, "milk": 0.1, "eggs": 1.0, "butter": 0.015,
            "sugar": 0.01, "baking_powder": 0.003,
        },
        units={
            "flour": "kg", "milk": "L", "eggs": "unit", "butter": "kg",
            "sugar": "kg", "baking_powder": "kg",
        },
        cost_per_person=0.70,
        prep_time=20,
        tags={"vegetarian", "kids-friendly"},
        calories=400,
        protein=11.0,
    ),
    _recipe(
        name="Fruit Smoothie",
        meal_type="breakfast",
        ingredients={"banana": 1.0, "berries": 0.1, "milk": 0.2, "honey": 0.01},
        units={"banana": "unit", "berries": "kg", "milk": "L", "honey": "kg"},
        cost_per_person=0.80,
        prep_time=5,
        tags={"healthy", "vegetarian", "no-cook", "kids-friendly"},
        calories=240,
        protein=6.0,
    ),
    _recipe(
        name="Egg and Vegetable Omelette",
        meal_type="breakfast",
        ingredients={
            "eggs": 2.0, "bell_pepper": 0.25, "onion": 0.08, "olive_oil": 0.005,
            "salt": 0.001, "cheese": 0.03,
        },
        units={
            "eggs": "unit", "bell_pepper": "unit", "onion": "kg",
            "olive_oil": "L", "salt": "kg", "cheese": "kg",
        },
        cost_per_person=1.00,
        prep_time=15,
        tags={"healthy", "high-protein", "vegetarian", "low-cost"},
        calories=310,
        protein=21.0,
    ),

    # -----------------------------------------------------------------------
    # LUNCH
    # -----------------------------------------------------------------------
    _recipe(
        name="Chicken Caesar Salad",
        meal_type="lunch",
        ingredients={
            "chicken_breast": 0.15, "lettuce": 0.1, "parmesan": 0.02,
            "croutons": 0.03, "caesar_dressing": 0.03, "lemon": 0.25,
        },
        units={
            "chicken_breast": "kg", "lettuce": "kg", "parmesan": "kg",
            "croutons": "kg", "caesar_dressing": "L", "lemon": "unit",
        },
        cost_per_person=3.00,
        prep_time=20,
        tags={"healthy", "high-protein"},
        calories=450,
        protein=38.0,
    ),
    _recipe(
        name="Vegetable Soup",
        meal_type="lunch",
        ingredients={
            "carrot": 0.1, "celery": 0.05, "onion": 0.1, "potato": 0.15,
            "tomato": 0.1, "vegetable_broth": 0.4, "olive_oil": 0.01, "salt": 0.002,
        },
        units={
            "carrot": "kg", "celery": "kg", "onion": "kg", "potato": "kg",
            "tomato": "kg", "vegetable_broth": "L", "olive_oil": "L", "salt": "kg",
        },
        cost_per_person=1.20,
        prep_time=30,
        tags={"healthy", "vegetarian", "vegan", "low-cost"},
        calories=280,
        protein=7.0,
    ),
    _recipe(
        name="Tuna Pasta Salad",
        meal_type="lunch",
        ingredients={
            "pasta": 0.08, "tuna": 0.08, "mayonnaise": 0.03, "celery": 0.04,
            "onion": 0.05, "lemon": 0.25, "salt": 0.001,
        },
        units={
            "pasta": "kg", "tuna": "kg", "mayonnaise": "kg", "celery": "kg",
            "onion": "kg", "lemon": "unit", "salt": "kg",
        },
        cost_per_person=1.80,
        prep_time=20,
        tags={"high-protein", "low-cost"},
        calories=420,
        protein=28.0,
    ),
    _recipe(
        name="Lentil Curry",
        meal_type="lunch",
        ingredients={
            "red_lentils": 0.08, "onion": 0.1, "tomato": 0.1, "coconut_milk": 0.15,
            "curry_powder": 0.005, "garlic": 0.01, "olive_oil": 0.01, "rice": 0.08,
        },
        units={
            "red_lentils": "kg", "onion": "kg", "tomato": "kg", "coconut_milk": "L",
            "curry_powder": "kg", "garlic": "kg", "olive_oil": "L", "rice": "kg",
        },
        cost_per_person=1.40,
        prep_time=35,
        tags={"healthy", "vegetarian", "vegan", "high-protein", "low-cost"},
        calories=480,
        protein=22.0,
    ),
    _recipe(
        name="Chicken Wrap",
        meal_type="lunch",
        ingredients={
            "chicken_breast": 0.12, "tortilla": 1.0, "lettuce": 0.05,
            "tomato": 0.08, "cheese": 0.03, "sour_cream": 0.04,
        },
        units={
            "chicken_breast": "kg", "tortilla": "unit", "lettuce": "kg",
            "tomato": "kg", "cheese": "kg", "sour_cream": "kg",
        },
        cost_per_person=2.50,
        prep_time=20,
        tags={"high-protein", "kids-friendly"},
        calories=510,
        protein=35.0,
    ),
    _recipe(
        name="Caprese Sandwich",
        meal_type="lunch",
        ingredients={
            "bread": 2.0, "mozzarella": 0.08, "tomato": 0.1,
            "basil": 0.005, "olive_oil": 0.01, "salt": 0.001,
        },
        units={
            "bread": "slice", "mozzarella": "kg", "tomato": "kg",
            "basil": "kg", "olive_oil": "L", "salt": "kg",
        },
        cost_per_person=2.00,
        prep_time=10,
        tags={"vegetarian", "no-cook"},
        calories=400,
        protein=18.0,
    ),
    _recipe(
        name="Black Bean Tacos",
        meal_type="lunch",
        ingredients={
            "tortilla": 2.0, "black_beans": 0.1, "avocado": 0.3, "tomato": 0.08,
            "lime": 0.25, "cilantro": 0.005, "salt": 0.001,
        },
        units={
            "tortilla": "unit", "black_beans": "kg", "avocado": "unit",
            "tomato": "kg", "lime": "unit", "cilantro": "kg", "salt": "kg",
        },
        cost_per_person=1.60,
        prep_time=15,
        tags={"healthy", "vegetarian", "vegan", "low-cost", "high-protein"},
        calories=460,
        protein=20.0,
    ),
    _recipe(
        name="Salmon and Rice Bowl",
        meal_type="lunch",
        ingredients={
            "salmon": 0.15, "rice": 0.08, "cucumber": 0.1, "avocado": 0.3,
            "soy_sauce": 0.02, "sesame_oil": 0.005, "sesame_seeds": 0.005,
        },
        units={
            "salmon": "kg", "rice": "kg", "cucumber": "kg", "avocado": "unit",
            "soy_sauce": "L", "sesame_oil": "L", "sesame_seeds": "kg",
        },
        cost_per_person=4.00,
        prep_time=25,
        tags={"healthy", "high-protein"},
        calories=520,
        protein=40.0,
    ),

    # -----------------------------------------------------------------------
    # SNACK
    # -----------------------------------------------------------------------
    _recipe(
        name="Apple with Peanut Butter",
        meal_type="snack",
        ingredients={"apple": 1.0, "peanut_butter": 0.03},
        units={"apple": "unit", "peanut_butter": "kg"},
        cost_per_person=0.60,
        prep_time=2,
        tags={"healthy", "vegetarian", "no-cook", "kids-friendly", "low-cost", "high-protein"},
        calories=200,
        protein=7.0,
    ),
    _recipe(
        name="Hummus and Veggies",
        meal_type="snack",
        ingredients={"hummus": 0.06, "carrot": 0.08, "cucumber": 0.08, "bell_pepper": 0.15},
        units={"hummus": "kg", "carrot": "kg", "cucumber": "kg", "bell_pepper": "unit"},
        cost_per_person=0.80,
        prep_time=5,
        tags={"healthy", "vegetarian", "vegan", "no-cook", "kids-friendly", "high-protein"},
        calories=160,
        protein=6.0,
    ),
    _recipe(
        name="Mixed Nuts",
        meal_type="snack",
        ingredients={"mixed_nuts": 0.04},
        units={"mixed_nuts": "kg"},
        cost_per_person=0.50,
        prep_time=0,
        tags={"healthy", "no-cook", "vegan", "high-protein", "low-cost"},
        calories=220,
        protein=6.0,
    ),
    _recipe(
        name="Banana",
        meal_type="snack",
        ingredients={"banana": 1.0},
        units={"banana": "unit"},
        cost_per_person=0.20,
        prep_time=0,
        tags={"healthy", "no-cook", "vegan", "vegetarian", "low-cost", "kids-friendly"},
        calories=90,
        protein=1.1,
    ),
    _recipe(
        name="Cheese and Crackers",
        meal_type="snack",
        ingredients={"cheese": 0.04, "crackers": 0.04},
        units={"cheese": "kg", "crackers": "kg"},
        cost_per_person=0.70,
        prep_time=3,
        tags={"vegetarian", "no-cook", "kids-friendly"},
        calories=220,
        protein=9.0,
    ),
    _recipe(
        name="Boiled Eggs",
        meal_type="snack",
        ingredients={"eggs": 2.0, "salt": 0.001},
        units={"eggs": "unit", "salt": "kg"},
        cost_per_person=0.40,
        prep_time=12,
        tags={"high-protein", "low-cost", "vegetarian"},
        calories=140,
        protein=12.0,
    ),

    # -----------------------------------------------------------------------
    # DINNER
    # -----------------------------------------------------------------------
    _recipe(
        name="Spaghetti Bolognese",
        meal_type="dinner",
        ingredients={
            "pasta": 0.1, "ground_beef": 0.12, "tomato_sauce": 0.15, "onion": 0.1,
            "garlic": 0.01, "olive_oil": 0.01, "salt": 0.002, "parmesan": 0.02,
        },
        units={
            "pasta": "kg", "ground_beef": "kg", "tomato_sauce": "kg", "onion": "kg",
            "garlic": "kg", "olive_oil": "L", "salt": "kg", "parmesan": "kg",
        },
        cost_per_person=2.50,
        prep_time=40,
        tags={"kids-friendly", "low-cost"},
        calories=620,
        protein=32.0,
    ),
    _recipe(
        name="Grilled Chicken with Roasted Vegetables",
        meal_type="dinner",
        ingredients={
            "chicken_breast": 0.2, "zucchini": 0.15, "bell_pepper": 0.3,
            "onion": 0.1, "olive_oil": 0.02, "garlic": 0.01, "salt": 0.002,
        },
        units={
            "chicken_breast": "kg", "zucchini": "kg", "bell_pepper": "unit",
            "onion": "kg", "olive_oil": "L", "garlic": "kg", "salt": "kg",
        },
        cost_per_person=3.50,
        prep_time=40,
        tags={"healthy", "high-protein"},
        calories=480,
        protein=45.0,
    ),
    _recipe(
        name="Vegetable Stir Fry with Rice",
        meal_type="dinner",
        ingredients={
            "rice": 0.1, "broccoli": 0.1, "carrot": 0.08, "bell_pepper": 0.25,
            "soy_sauce": 0.03, "sesame_oil": 0.005, "garlic": 0.01, "onion": 0.08,
        },
        units={
            "rice": "kg", "broccoli": "kg", "carrot": "kg", "bell_pepper": "unit",
            "soy_sauce": "L", "sesame_oil": "L", "garlic": "kg", "onion": "kg",
        },
        cost_per_person=1.80,
        prep_time=25,
        tags={"healthy", "vegetarian", "vegan", "low-cost", "kids-friendly"},
        calories=440,
        protein=12.0,
    ),
    _recipe(
        name="Baked Salmon with Potatoes",
        meal_type="dinner",
        ingredients={
            "salmon": 0.2, "potato": 0.2, "olive_oil": 0.02, "lemon": 0.5,
            "garlic": 0.01, "salt": 0.002, "dill": 0.003,
        },
        units={
            "salmon": "kg", "potato": "kg", "olive_oil": "L", "lemon": "unit",
            "garlic": "kg", "salt": "kg", "dill": "kg",
        },
        cost_per_person=5.00,
        prep_time=45,
        tags={"healthy", "high-protein"},
        calories=560,
        protein=44.0,
    ),
    _recipe(
        name="Chickpea and Spinach Stew",
        meal_type="dinner",
        ingredients={
            "chickpeas": 0.1, "spinach": 0.1, "tomato": 0.15, "onion": 0.1,
            "garlic": 0.01, "olive_oil": 0.01, "cumin": 0.003, "salt": 0.002,
        },
        units={
            "chickpeas": "kg", "spinach": "kg", "tomato": "kg", "onion": "kg",
            "garlic": "kg", "olive_oil": "L", "cumin": "kg", "salt": "kg",
        },
        cost_per_person=1.50,
        prep_time=30,
        tags={"healthy", "vegetarian", "vegan", "high-protein", "low-cost"},
        calories=380,
        protein=18.0,
    ),
    _recipe(
        name="Beef Tacos",
        meal_type="dinner",
        ingredients={
            "ground_beef": 0.15, "tortilla": 2.0, "tomato": 0.1, "lettuce": 0.06,
            "cheese": 0.04, "sour_cream": 0.04, "lime": 0.25, "taco_seasoning": 0.008,
        },
        units={
            "ground_beef": "kg", "tortilla": "unit", "tomato": "kg", "lettuce": "kg",
            "cheese": "kg", "sour_cream": "kg", "lime": "unit", "taco_seasoning": "kg",
        },
        cost_per_person=3.20,
        prep_time=25,
        tags={"kids-friendly"},
        calories=590,
        protein=36.0,
    ),
    _recipe(
        name="Pasta Primavera",
        meal_type="dinner",
        ingredients={
            "pasta": 0.1, "zucchini": 0.1, "bell_pepper": 0.25, "cherry_tomatoes": 0.1,
            "olive_oil": 0.02, "garlic": 0.01, "parmesan": 0.02, "salt": 0.002,
        },
        units={
            "pasta": "kg", "zucchini": "kg", "bell_pepper": "unit", "cherry_tomatoes": "kg",
            "olive_oil": "L", "garlic": "kg", "parmesan": "kg", "salt": "kg",
        },
        cost_per_person=2.00,
        prep_time=30,
        tags={"healthy", "vegetarian", "low-cost", "kids-friendly"},
        calories=500,
        protein=18.0,
    ),
    _recipe(
        name="Shrimp Stir Fry",
        meal_type="dinner",
        ingredients={
            "shrimp": 0.15, "rice": 0.1, "broccoli": 0.1, "carrot": 0.08,
            "soy_sauce": 0.03, "sesame_oil": 0.005, "garlic": 0.01, "ginger": 0.005,
        },
        units={
            "shrimp": "kg", "rice": "kg", "broccoli": "kg", "carrot": "kg",
            "soy_sauce": "L", "sesame_oil": "L", "garlic": "kg", "ginger": "kg",
        },
        cost_per_person=4.00,
        prep_time=25,
        tags={"healthy", "high-protein"},
        calories=490,
        protein=38.0,
    ),
    _recipe(
        name="Minestrone Soup",
        meal_type="dinner",
        ingredients={
            "pasta": 0.06, "carrot": 0.08, "celery": 0.06, "onion": 0.1,
            "tomato": 0.12, "kidney_beans": 0.08, "vegetable_broth": 0.5,
            "olive_oil": 0.01, "garlic": 0.01, "salt": 0.002,
        },
        units={
            "pasta": "kg", "carrot": "kg", "celery": "kg", "onion": "kg",
            "tomato": "kg", "kidney_beans": "kg", "vegetable_broth": "L",
            "olive_oil": "L", "garlic": "kg", "salt": "kg",
        },
        cost_per_person=1.60,
        prep_time=40,
        tags={"healthy", "vegetarian", "vegan", "low-cost"},
        calories=360,
        protein=14.0,
    ),
    _recipe(
        name="Chicken Stir Fry with Noodles",
        meal_type="dinner",
        ingredients={
            "chicken_breast": 0.15, "noodles": 0.1, "broccoli": 0.1,
            "soy_sauce": 0.03, "sesame_oil": 0.005, "garlic": 0.01, "carrot": 0.08,
        },
        units={
            "chicken_breast": "kg", "noodles": "kg", "broccoli": "kg",
            "soy_sauce": "L", "sesame_oil": "L", "garlic": "kg", "carrot": "kg",
        },
        cost_per_person=3.00,
        prep_time=25,
        tags={"healthy", "high-protein", "kids-friendly"},
        calories=530,
        protein=40.0,
    ),
    _recipe(
        name="Mushroom Risotto",
        meal_type="dinner",
        ingredients={
            "arborio_rice": 0.1, "mushrooms": 0.12, "onion": 0.08,
            "vegetable_broth": 0.4, "parmesan": 0.03, "butter": 0.02,
            "olive_oil": 0.01, "white_wine": 0.05, "garlic": 0.01, "salt": 0.002,
        },
        units={
            "arborio_rice": "kg", "mushrooms": "kg", "onion": "kg",
            "vegetable_broth": "L", "parmesan": "kg", "butter": "kg",
            "olive_oil": "L", "white_wine": "L", "garlic": "kg", "salt": "kg",
        },
        cost_per_person=2.80,
        prep_time=45,
        tags={"healthy", "vegetarian"},
        calories=520,
        protein=16.0,
    ),
    _recipe(
        name="Turkey Meatballs with Tomato Sauce",
        meal_type="dinner",
        ingredients={
            "ground_turkey": 0.18, "pasta": 0.1, "tomato_sauce": 0.2,
            "breadcrumbs": 0.02, "eggs": 0.5, "parmesan": 0.02,
            "garlic": 0.01, "olive_oil": 0.01, "salt": 0.002,
        },
        units={
            "ground_turkey": "kg", "pasta": "kg", "tomato_sauce": "kg",
            "breadcrumbs": "kg", "eggs": "unit", "parmesan": "kg",
            "garlic": "kg", "olive_oil": "L", "salt": "kg",
        },
        cost_per_person=3.00,
        prep_time=45,
        tags={"high-protein", "kids-friendly"},
        calories=560,
        protein=42.0,
    ),
    _recipe(
        name="Fish and Chips",
        meal_type="dinner",
        ingredients={
            "white_fish": 0.18, "potato": 0.25, "flour": 0.04,
            "olive_oil": 0.02, "salt": 0.002, "lemon": 0.25,
        },
        units={
            "white_fish": "kg", "potato": "kg", "flour": "kg",
            "olive_oil": "L", "salt": "kg", "lemon": "unit",
        },
        cost_per_person=3.80,
        prep_time=40,
        tags={"kids-friendly", "high-protein"},
        calories=580,
        protein=38.0,
    ),
    _recipe(
        name="Tofu and Vegetable Curry",
        meal_type="dinner",
        ingredients={
            "tofu": 0.15, "rice": 0.1, "coconut_milk": 0.2, "onion": 0.1,
            "tomato": 0.1, "curry_powder": 0.005, "garlic": 0.01,
            "olive_oil": 0.01, "spinach": 0.08,
        },
        units={
            "tofu": "kg", "rice": "kg", "coconut_milk": "L", "onion": "kg",
            "tomato": "kg", "curry_powder": "kg", "garlic": "kg",
            "olive_oil": "L", "spinach": "kg",
        },
        cost_per_person=2.20,
        prep_time=35,
        tags={"healthy", "vegetarian", "vegan", "high-protein"},
        calories=460,
        protein=22.0,
    ),
]


def get_recipes_by_type(meal_type: str) -> List[Recipe]:
    """Return all recipes of a given meal type."""
    return [r for r in RECIPES if r.meal_type == meal_type]


def get_recipes_by_tag(tag: str) -> List[Recipe]:
    """Return all recipes that have a given tag."""
    return [r for r in RECIPES if tag in r.tags]


def find_recipe(name: str) -> Optional[Recipe]:
    """Find a recipe by exact name (case-insensitive)."""
    lower = name.lower()
    for r in RECIPES:
        if r.name.lower() == lower:
            return r
    return None


def get_all_ingredients() -> Set[str]:
    """Return the set of all ingredients used across all recipes."""
    result: Set[str] = set()
    for r in RECIPES:
        result.update(r.ingredient_names())
    return result
