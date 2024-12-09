import json
import re
from fuzzywuzzy import process

# Load the ingredients
with open("unique_ingredients.json", "r") as file:
    original_ingredients = json.load(file)

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
    ingredient_clean = ingredient.lower().strip()

    # Remove descriptors and quantities
    ingredient_clean = re.sub(
        r"\b(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|ounces?|ounces|pounds?|lbs?|inch|oz|g|kg|ml|tbsp|tsp|dash|pinch|quarts?)\b",
        "",
        ingredient_clean,
    )
    ingredient_clean = re.sub(
        r"\b(optional|divided|uncooked|fresh|ground|dried|chopped|sliced|minced|peeled|seeded)\b",
        "",
        ingredient_clean,
    )
    ingredient_clean = re.sub(
        r"\b(\d+[-/]?\d*|[\d.]+)\b", "", ingredient_clean
    )  # Remove numeric quantities

    # Remove special characters and extra spaces
    ingredient_clean = re.sub(r"[^\w\s]", "", ingredient_clean)
    ingredient_clean = re.sub(r"\s+", " ", ingredient_clean).strip()

    # Map to canonical form
    ingredient_canonical = canonical_mapping.get(ingredient_clean, ingredient_clean)

    return ingredient_canonical

# Resolve duplicates with fuzzy matching and create a mapping
def resolve_duplicates(ingredient_list, threshold=85):
    resolved = {}
    mapped_to_canonical = {}
    for ingredient in ingredient_list:
        if not resolved:  # If resolved is empty, add the first ingredient
            resolved[ingredient] = ingredient
            mapped_to_canonical[ingredient] = ingredient
            continue
        # Perform fuzzy matching
        match, score = process.extractOne(
            ingredient, resolved.keys(), scorer=process.default_scorer
        )
        if match and score >= threshold:
            # Map to the existing canonical form
            resolved_key = resolved[match]
            resolved[match] = resolved_key  # Ensure consistency
            mapped_to_canonical[ingredient] = resolved_key
        else:
            resolved[ingredient] = ingredient
            mapped_to_canonical[ingredient] = ingredient
    return resolved, mapped_to_canonical

# Step 1: Clean each ingredient
cleaned_ingredients = [clean_ingredient(ing) for ing in original_ingredients]

# Step 2: Resolve duplicates and get mapping to canonical forms
resolved_duplicates, canonical_mapping_resolved = resolve_duplicates(cleaned_ingredients)

# Step 3: Create a mapping from original ingredients to mapped ingredients
ingredient_mapping = {}
for original, cleaned in zip(original_ingredients, cleaned_ingredients):
    # Find the resolved canonical form for the cleaned ingredient
    canonical = canonical_mapping_resolved.get(cleaned, cleaned)
    ingredient_mapping[original] = canonical

# Step 4: Save the final cleaned and deduplicated list
deduplicated_ingredients = list(resolved_duplicates.values())
with open("refined_ingredients.json", "w") as outfile:
    json.dump(sorted(deduplicated_ingredients), outfile, indent=4)

# Step 5: Save the mapping of original ingredients to mapped ingredients
with open("ingredient_mapping.json", "w") as mapfile:
    json.dump(ingredient_mapping, mapfile, indent=4)

print(f"Total unique ingredients (before): {len(original_ingredients)}")
print(f"Total unique ingredients (after cleaning): {len(deduplicated_ingredients)}")
print("Mapping of original ingredients to mapped ingredients has been saved to 'ingredient_mapping.json'.")
