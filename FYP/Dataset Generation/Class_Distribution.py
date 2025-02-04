import os
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

DATASET_PATH = "dataset"
NUM_ALLERGENS = 14  # Number of allergens in your dataset

# Function to load dataset and count allergens
def analyze_dataset(dataset_path):
    allergen_counts = defaultdict(lambda: {"present": 0, "absent": 0})  # Counts for each allergen
    total_images = 0

    for recipe_folder in os.listdir(dataset_path):
        recipe_path = os.path.join(dataset_path, recipe_folder)
        allergens_json_path = os.path.join(recipe_path, "allergens.json")

        if os.path.exists(allergens_json_path):
            with open(allergens_json_path, "r") as f:
                metadata = json.load(f)
                allergens = metadata["allergens"]
                num_images = len(metadata["images"])

                # Update counts for each allergen
                for idx, value in enumerate(allergens):
                    if value == 1:
                        allergen_counts[idx]["present"] += num_images
                    else:
                        allergen_counts[idx]["absent"] += num_images

                total_images += num_images

    return allergen_counts, total_images

# Function to calculate and print allergen percentages
def print_allergen_percentages(allergen_counts, total_images):
    print("Allergen Distribution:")
    for idx in range(NUM_ALLERGENS):
        present = allergen_counts[idx]["present"]
        absent = allergen_counts[idx]["absent"]
        percentage_present = (present / total_images) * 100
        print(f"Allergen {idx + 1}:")
        print(f"  Present: {present} ({percentage_present:.2f}%)")
        print(f"  Absent: {absent}")

# Main function
def main():
    allergen_counts, total_images = analyze_dataset(DATASET_PATH)
    print_allergen_percentages(allergen_counts, total_images)

if __name__ == "__main__":
    main()