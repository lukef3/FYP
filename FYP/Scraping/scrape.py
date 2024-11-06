import requests
from bs4 import BeautifulSoup
import os
import json
import time


def scrape_recipe(url, root_folder="dataset"):
    # Fetch the page content
    response = requests.get(url)
    response.raise_for_status()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape the dish name
    dish_name_tag = soup.find('h1', class_='svelte-1muv3s8')
    if not dish_name_tag:
        print("Dish name not found. Using default name 'recipe'.")
        dish_name = "recipe"
    else:
        dish_name = dish_name_tag.get_text(strip=True).replace(" ", "_").lower()

    # Create the folder structure for this dish
    dish_folder = os.path.join(root_folder, dish_name)
    images_folder = os.path.join(dish_folder, "images")
    os.makedirs(images_folder, exist_ok=True)

    # Scrape ingredients
    ingredients = []
    ingredient_list = soup.find('ul', class_='ingredient-list')
    if ingredient_list:
        for item in ingredient_list.find_all('li', style='display: contents'):
            ingredient_text_span = item.find('span', class_='ingredient-text')
            # Find all <a> tags within the ingredient-text span for ingredient names
            ingredient_names = [a.get_text(strip=True) for a in ingredient_text_span.find_all('a')]
            # If no <a> tag is found, it might be a plain text ingredient
            if not ingredient_names:
                ingredient_names = [ingredient_text_span.get_text(strip=True)]
            # Add names to ingredients list
            ingredients.extend(ingredient_names)

    # Initialize JSON data structure
    json_data = {
        "dish_name": dish_name.replace("_", " "),  # Store human-readable dish name
        "ingredients": ingredients,
        "images": []
    }

    # Image counter
    image_counter = 1

    # Scrape main image
    main_image_tag = soup.find('img', class_='only-desktop')
    if main_image_tag:
        main_img_url = main_image_tag.get('src')
        if main_img_url:
            main_img_response = requests.get(main_img_url)
            main_img_response.raise_for_status()
            main_img_name = f"image_{image_counter}.jpg"
            main_img_path = os.path.join(images_folder, main_img_name)
            with open(main_img_path, 'wb') as f:
                f.write(main_img_response.content)
            print(f"Main image downloaded and saved as {main_img_path}")
            json_data["images"].append(f"images/{main_img_name}")
            image_counter += 1

    # Scrape additional images from 'other-images' section
    other_images_div = soup.find('div', class_='other-images')
    if other_images_div:
        img_tags = other_images_div.find_all('img', class_='only-desktop')
        for img_tag in img_tags:
            img_url = img_tag.get('src')
            if not img_url:
                print(f"No src found for additional image {image_counter}. Skipping.")
                continue
            img_response = requests.get(img_url)
            img_response.raise_for_status()
            img_name = f"image_{image_counter}.jpg"
            img_path = os.path.join(images_folder, img_name)
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
            print(f"Additional image downloaded and saved as {img_path}")
            json_data["images"].append(f"images/{img_name}")
            image_counter += 1

    # Save the JSON file
    json_path = os.path.join(dish_folder, "ingredients.json")
    with open(json_path, 'w') as file:
        json.dump(json_data, file, indent=4)
    print(f"Ingredients and image data saved to {json_path}")

    return json_data


def scrape_all_recipes(main_page_url, root_folder="dataset", delay=1):
    # Fetch the main page content
    response = requests.get(main_page_url)
    response.raise_for_status()

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all recipe links in the 'smart-cards' section
    smart_cards_section = soup.find('section', class_='smart-cards')
    if not smart_cards_section:
        print("No 'smart-cards' section found on the page.")
        return

    recipe_links = []
    smart_card_divs = smart_cards_section.find_all('div', class_='smart-card container-sm recipe')
    for card in smart_card_divs:
        link = card.get('data-seo-url')  # Extract the data-seo-url attribute
        if link:
            recipe_links.append(link)

    print(f"Found {len(recipe_links)} recipes on the page.")

    # Scrape each recipe
    for i, recipe_url in enumerate(recipe_links, start=1):
        print(f"Scraping recipe {i}/{len(recipe_links)}: {recipe_url}")
        try:
            scrape_recipe(recipe_url, root_folder=root_folder)
        except Exception as e:
            print(f"Error scraping {recipe_url}: {e}")
        # Add a delay to avoid overloading the server
        time.sleep(delay)

main_page_url = "https://www.food.com/ideas/best-air-fryer-recipes-6847#c-752960"
scrape_all_recipes(main_page_url)
