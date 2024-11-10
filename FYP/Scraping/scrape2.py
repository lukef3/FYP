import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
import json

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

def scrape_all_recipes_selenium(url):
    """
    Scrape all recipes using Selenium for pages where all content is initially loaded.

    Args:
        url (str): URL of the main page containing recipes.
        root_folder (str): Folder to save scraped data.
        delay (int): Delay in seconds after loading the page.
    """
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)  # Use the appropriate WebDriver for your browser
    driver.get(url)
    time.sleep(2)  # Wait for the page to fully load
    recipe_links = set()  # Use a set to avoid duplicates

    # Parse the current page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all recipe cards
    recipe_cards = soup.find_all('div', class_='fd-tile fd-recipe')
    for card in recipe_cards:
        link = card.get('data-url')  # Extract the dynamically rendered `data-url` attribute
        if link and link not in recipe_links:
            recipe_links.add(link)

    driver.quit()
    return  recipe_links


def main():
    base_url = "https://www.food.com/recipe/?pn={}"
    start_page = 120
    max_page = 200

    for page_number in range(start_page, max_page + 1):
        # Construct the URL for the current page
        page_url = base_url.format(page_number)

        # Scrape all recipes on the current page
        recipe_links = scrape_all_recipes_selenium(page_url)
        print(f"Scraping page {page_number}")
        # Process each recipe
        for i, recipe_url in enumerate(recipe_links, start=1):
            print(f"Processing recipe {i}/{len(recipe_links)}: {recipe_url}")
            try:
                scrape_recipe(recipe_url)
            except Exception as e:
                print(f"Error processing recipe {recipe_url}: {e}")
    print(f"Finished scraping from page {start_page} and {max_page}")

main()


