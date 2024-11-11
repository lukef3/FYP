import json
import re
from fuzzywuzzy import process

# Load the ingredients
with open("unique_ingredients.json", "r") as file:
    ingredients = json.load(file)

# Define a mapping dictionary for canonical names
canonical_mapping = {
    "white sugar": "sugar",
    "yellow onions": "onion",
    "yellow onion": "onion",
    "red onions": "onion",
    "white wine vinegar": "vinegar",
    "red wine vinegar": "vinegar",
    "cornstarch": "corn starch",
    "garlic cloves": "garlic",
    "worcestershire sauce": "sauce",
    "wide egg noodles uncooked": "egg noodles",
    "yukon gold potatoes": "potatoes",
    "yukon gold potato": "potatoes",
    # Add more mappings as needed
}

# Function to clean ingredient names
def clean_ingredient(ingredient):
    # Convert to lowercase and strip extra spaces
    ingredient = ingredient.lower().strip()

    # Remove descriptors and quantities
    ingredient = re.sub(r"\b(cup|tablespoon|teaspoon|ounces?|pounds?|lbs?|inch|oz|g|kg|ml|tbsp|tsp|dash|pinch|quarts?)\b", "", ingredient)
    ingredient = re.sub(r"\b(optional|divided|uncooked|fresh|ground|dried|chopped|sliced|minced|peeled|seeded)\b", "", ingredient)
    ingredient = re.sub(r"\b(\d+[-/]?\d*|[\d.]+)\b", "", ingredient)  # Remove numeric quantities

    # Remove special characters and extra spaces
    ingredient = re.sub(r"[^\w\s]", "", ingredient)
    ingredient = re.sub(r"\s+", " ", ingredient).strip()

    # Map to canonical form
    ingredient = canonical_mapping.get(ingredient, ingredient)

    return ingredient

# Resolve duplicates with fuzzy matching
def resolve_duplicates(ingredient_list, threshold=85):
    resolved = {}
    for ingredient in ingredient_list:
        if not resolved:  # If resolved is empty, add the first ingredient
            resolved[ingredient] = ingredient
            continue
        # Perform fuzzy matching
        match, score = process.extractOne(ingredient, resolved.keys(), scorer=process.default_scorer)
        if match and score >= threshold:
            resolved[match] = resolved[match]  # Use existing canonical match
        else:
            resolved[ingredient] = ingredient  # Add new entry
    return list(resolved.values())


# Step 1: Clean each ingredient
cleaned_ingredients = [clean_ingredient(ingredient) for ingredient in ingredients]

# Step 2: Resolve duplicates
deduplicated_ingredients = resolve_duplicates(cleaned_ingredients)

# Save the final cleaned and deduplicated list
with open("final_refined_ingredients.json", "w") as outfile:
    json.dump(sorted(deduplicated_ingredients), outfile, indent=4)

print(f"Total unique ingredients (before): {len(ingredients)}")
print(f"Total unique ingredients (after cleaning): {len(deduplicated_ingredients)}")
print("Final refined ingredients saved to final_refined_ingredients.json")
