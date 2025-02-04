import os
import json
import shutil

metadata_dir = 'C:/FYP Datasets/Yummly28K/metadata27638'
images_dir = 'C:/FYP Datasets/Yummly28K/images27638'
output_base_dir = 'dataset'

for filename in os.listdir(metadata_dir):
    if filename.endswith('.json') and filename.startswith('meta'):
        # Extract the numeric part of the filename
        number = filename[len('meta'):-len('.json')]
        new_folder = os.path.join(output_base_dir, number)
        os.makedirs(new_folder, exist_ok=True)

        new_images_folder = os.path.join(new_folder, 'images')
        os.makedirs(new_images_folder, exist_ok=True)

        image_filename = f"img{number}.jpg"
        src_image_path = os.path.join(images_dir, image_filename)
        dst_image_path = os.path.join(new_images_folder, image_filename)
        if os.path.exists(src_image_path):
            shutil.copy2(src_image_path, dst_image_path)
        else:
            print(f"Warning: {src_image_path} does not exist")

        metadata_path = os.path.join(metadata_dir, filename)
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        new_data = {
            "ingredients": data.get("ingredientLines", []),
            "images": [os.path.join("images", image_filename)]
        }

        # Write the new json file into the new folder
        new_json_path = os.path.join(new_folder, 'ingredients.json')
        with open(new_json_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
