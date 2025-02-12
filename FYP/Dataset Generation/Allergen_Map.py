import os
import json

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
        "egg", "egg white", "egg yolk", "albumin", "ova", "mayonnaise", "meringue"
    ],
    "Fish": [
        "fish", "anchovy", "bass", "carp", "catfish", "cod", "eel", "grouper", "haddock",
        "herring", "mackerel", "perch", "pollock", "salmon", "sardine", "snapper", "sole",
        "trout", "tuna", "whiting", "caviar"
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
        "sulphur dioxide", "sulphite", "sulfite", "SO2", "sodium metabisulfite", "potassium metabisulfite",
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

def get_allergens(ingredient):
    allergens_found = set()
    for allergen, allergen_terms in ALLERGEN_TERMS.items():
        for allergen_term in allergen_terms:
            if allergen_term in ingredient.lower():
                allergens_found.add(allergen)
                break
    return allergens_found

def process_dataset():
    for folder in os.listdir(DATASET_PATH):
        path = os.path.join(DATASET_PATH, folder)
        if os.path.isdir(path):
            ing_file = os.path.join(path, 'ingredients.json')
            out_file = os.path.join(path, 'allergens.json')
            if not os.path.exists(ing_file):
                continue

            try:
                with open(ing_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {ing_file}: {e}")
                continue

            # Match ingredient terms to allergen terms
            matched_allergens = set()
            for ingredient in data.get('ingredients', []):
                matched_allergens |= get_allergens(ingredient)

            # Convert to a binary vector
            vector = [1 if a in matched_allergens else 0 for a in ALLERGENS]
            output_data = {
                "allergens": vector,
                "images": data.get("images", [])
            }
            with open(out_file, 'w', encoding='utf-8') as f_out:
                json.dump(output_data, f_out, indent=4)
            print(f"Processed {folder}: {sorted(matched_allergens)}")

process_dataset()