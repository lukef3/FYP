import os
import json
import shutil
from PIL import Image

# Remove invalid data from dataset

dataset_directory = 'dataset'

def is_valid_image(file_name):  # https://www.geeksforgeeks.org/check-if-a-file-is-valid-image-with-python/
    try:
        with Image.open(file_name) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False

for recipe_folder in os.listdir(dataset_directory):
    recipe_path = os.path.join(dataset_directory, recipe_folder)
    ingredients_file = os.path.join(recipe_path, 'ingredients.json')
    images_directory = os.path.join(recipe_path, 'images')

    is_invalid = False

    if not os.path.isfile(ingredients_file):
        print("Dataset {} without ingredients file".format(ingredients_file))
        is_invalid = True
    else:
        try:
            with open(ingredients_file) as f:
                data = json.load(f)
            for img in data['images']:
                img_path = os.path.join(recipe_path, img)
                # Check if the image exists
                if not os.path.isfile(img_path):
                    is_invalid = True
                    break
                # Check if the image is valid
                if not is_valid_image(img_path):
                    print("Dataset {} invalid image".format(ingredients_file))
                    is_invalid = True
                    break
        except json.JSONDecodeError:
            print("Could open JSON file")
    if is_invalid:
        shutil.rmtree(recipe_path)
        print("Deleted {} ".format(recipe_path))




