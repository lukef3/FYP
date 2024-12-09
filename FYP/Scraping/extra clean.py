import os
import json
import re
from collections import Counter
from rapidfuzz import process, fuzz

# Define the path to your dataset
DATASET_PATH = 'dataset'  # Replace with your dataset path

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

# Optional: Additional canonical terms to ensure comprehensive mapping
additional_canonical = [
    "sugar", "onion", "vinegar", "corn starch", "garlic", "sauce",
    "egg noodles", "potatoes", "salt", "cumin", "black beans",
    "chicken bouillon cubes", "boiling water", "red bell pepper",
    "celery ribs", "garlic", "lemon juice", "cornstarch",
    # Add other canonical terms as necessary
]

# Precompile regex patterns for performance
quantity_pattern = re.compile(
    r"\b(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|ounces?|ounce|pounds?|lbs?|inch|oz|g|kg|ml|tbsp|tsp|dash|pinch|quarts?)\b",
    re.IGNORECASE)
descriptor_pattern = re.compile(
    r"\b(optional|divided|uncooked|fresh|ground|dried|chopped|sliced|minced|peeled|seeded|cooked|cooking|crushed|large|small|medium|extra-virgin|virgin|light|dark)\b",
    re.IGNORECASE)
number_pattern = re.compile(r"\b(\d+[-/]?\d*|[\d.]+)\b")
special_char_pattern = re.compile(r"[^\w\s]")
multi_space_pattern = re.compile(r"\s+")


# Function to clean ingredient names
def clean_ingredient(ingredient):
    # Convert to lowercase and strip extra spaces
    ingredient = ingredient.lower().strip()

    # Remove descriptors and quantities
    ingredient = quantity_pattern.sub("", ingredient)
    ingredient = descriptor_pattern.sub("", ingredient)
    ingredient = number_pattern.sub("", ingredient)

    # Remove special characters and extra spaces
    ingredient = special_char_pattern.sub("", ingredient)
    ingredient = multi_space_pattern.sub(" ", ingredient).strip()

    # Map to canonical form using exact match first
    if ingredient in canonical_mapping:
        return canonical_mapping[ingredient]

    # If not in canonical_mapping, attempt fuzzy matching
    # against both canonical_mapping values and additional_canonical list
    combined_canonical = list(canonical_mapping.values()) + additional_canonical
    match, score, _ = process.extractOne(
        ingredient, combined_canonical, scorer=fuzz.token_sort_ratio)

    if score >= 90:  # Adjust threshold as needed
        return match
    else:
        return ingredient  # Return as-is if no good match is found


# Function to process all ingredients and count frequencies
def process_ingredients(dataset_path):
    ingredient_counter = Counter()

    # Traverse through each dish folder
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('ingredients.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        ingredients = data.get('ingredients', [])
                        for ingredient in ingredients:
                            cleaned = clean_ingredient(ingredient)
                            if cleaned:  # Ensure non-empty
                                ingredient_counter[cleaned] += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return ingredient_counter


# Function to write ingredients to a text file with counts
def write_ingredients_to_file(ingredient_counter, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for ingredient, count in ingredient_counter.most_common():
            f.write(f"{ingredient}: {count}\n")
    print(f"Ingredients written to {output_file}")


# Main execution
if __name__ == "__main__":
    # Step 1: Process all ingredients and count frequencies
    ingredient_counts = process_ingredients(DATASET_PATH)

    # Step 2: Write the counts to a text file
    output_txt = 'cleaned_ingredients_counts.txt'  # Specify your desired output file
    write_ingredients_to_file(ingredient_counts, output_txt)
