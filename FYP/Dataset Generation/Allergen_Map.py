import os
import json
import re

# Path to the dataset folder
DATASET_PATH = 'dataset'

# List of 14 major allergens
ALLERGENS = [
    "Cereals containing gluten",
    "Crustaceans",
    "Eggs",
    "Fish",
    "Peanuts",
    "Soybeans",
    "Milk",
    "Nuts",
    "Celery",
    "Mustard",
    "Sesame seeds",
    "Sulphur dioxide and sulphites",
    "Lupin",
    "Molluscs"
]

# Dictionary mapping allergens to possible ingredient terms
ALLERGEN_TERMS = {
    "Cereals containing gluten": [
        "wheat", "barley", "rye", "oats", "spelt", "kamut", "triticale", "malt", "brewer's yeast",
        "semolina", "farro", "bulgur", "couscous", "durum", "einkorn", "graham", "matzo", "pasta",
        "noodles", "bread", "cracker", "granola", "flour"
    ],
    "Crustaceans": [
        "crab", "shrimp", "prawn", "lobster", "krill", "crayfish", "langostino", "abalone",
        "clam", "cockle", "conch", "geoducks", "limpets", "mussels", "octopus", "oysters",
        "periwinkle", "quahaugs", "scallops", "snails", "escargot", "squid", "calamari", "whelks"
    ],
    "Eggs": [
        "egg", "egg white", "egg yolk", "albumin", "ova"
    ],
    "Fish": [
        "fish", "anchovy", "bass", "carp", "catfish", "cod", "eel", "grouper", "haddock",
        "herring", "mackerel", "perch", "pollock", "salmon", "sardine", "snapper", "sole",
        "trout", "tuna", "whiting"
    ],
    "Peanuts": [
        "peanut", "groundnut"
    ],
    "Soybeans": [
        "soy", "soya", "tofu", "edamame", "soy sauce", "soybean oil", "soy lecithin", "miso",
        "tempeh", "natto", "tamari"
    ],
    "Milk": [
        "milk", "butter", "ghee", "cream", "cheese", "whey", "yogurt", "casein", "lactose",
        "condensed milk", "evaporated milk", "ice cream", "milk powder", "chocolate"
    ],
    "Nuts": [
        "almond", "walnut", "hazelnut", "pistachio", "cashew", "pecan", "macadamia",
        "brazil nut", "filbert", "marcona", "pine nut", "chestnut"
    ],
    "Celery": [
        "celery", "celery stalk", "celery rib"
    ],
    "Mustard": [
        "mustard", "mustard seed", "mustard powder", "prepared mustard", "Dijon mustard", "yellow mustard"
    ],
    "Sesame seeds": [
        "sesame", "sesame seed", "tahini", "sesame oil"
    ],
    "Sulphur dioxide and sulphites": [
        "sulphur dioxide", "sulphites", "sulfites", "SO2", "sodium metabisulfite", "potassium metabisulfite",
        "calcium sulphite", "magnesium sulphite", "sulfur dioxide"
    ],
    "Lupin": [
        "lupin", "lupine"
    ],
    "Molluscs": [
        "mollusc", "mussel", "oyster", "clam", "scallop", "octopus", "squid", "snail", "abalone",
        "conch", "whelk"
    ]
}

PUNCTUATION_REGEX = re.compile(r'[^\w\s]')

def preprocess_ingredient(ingredient):
    # Convert to lowercase
    ingredient = ingredient.lower()
    # Remove special characters
    ingredient = re.sub(r'[^\w\s]', '', ingredient)
    # Strip extra spacing
    ingredient = ingredient.strip()
    return ingredient

def map_ingredient_to_allergens(ingredient, allergen_terms):
    matched_allergens = []
    for allergen, terms in allergen_terms.items():
        for term in terms:
            if term in ingredient:
                matched_allergens.append(allergen)
                break  # No need to check other terms for this allergen
    return matched_allergens

def create_allergen_vector(matched_allergens, allergen_list):
    return [1 if allergen in matched_allergens else 0 for allergen in allergen_list]

def process_recipe(recipe_path, allergen_terms, allergen_list):
    ingredients_file = os.path.join(recipe_path, 'ingredients.json')
    allergens_file = os.path.join(recipe_path, 'allergens.json')

    # Check if ingredients.json exists
    if os.path.exists(ingredients_file):
        with open(ingredients_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {ingredients_file}: {e}")
                return
        ingredients = data.get('ingredients', [])
        images = data.get('images', [])
        matched_allergens = set()

        for ingredient in ingredients:
            cleaned = preprocess_ingredient(ingredient)
            matches = map_ingredient_to_allergens(cleaned, allergen_terms)
            for match in matches:
                matched_allergens.add(match)

        allergen_vector = create_allergen_vector(matched_allergens, allergen_list)
        # json data structure
        allergens_data = {
            "dish_name": data.get("dish_name", ""),
            "allergens": allergen_vector,
            "images": images
        }
        # Save allergens.json
        with open(allergens_file, 'w', encoding='utf-8') as f_out:
            json.dump(allergens_data, f_out, indent=4)
        print(f"Processed {os.path.basename(recipe_path)}: Allergens - {sorted(matched_allergens)}")
    else:
        print(f"No ingredients.json found in {recipe_path}")

def process_dataset(dataset_path, allergen_terms, allergen_list):
    # Loop through each recipe folder in the dataset
    for recipe_name in os.listdir(dataset_path):
        recipe_path = os.path.join(dataset_path, recipe_name)
        if os.path.isdir(recipe_path):
            process_recipe(recipe_path, allergen_terms, allergen_list)

def main():
    processed_allergen_terms = {}
    for allergen, terms in ALLERGEN_TERMS.items():
        processed_terms = [preprocess_ingredient(term) for term in terms]
        processed_allergen_terms[allergen] = processed_terms

    process_dataset(DATASET_PATH, processed_allergen_terms, ALLERGENS)

main()