import json
from collections import Counter
import matplotlib.pyplot as plt

# Load the refined ingredients list
with open("unique_ingredients.json", "r") as file:
    ingredients = json.load(file)

# 1. Total Unique Ingredients
total_unique_ingredients = len(ingredients)

ingredient_counter = Counter(ingredients)
top_ingredients = ingredient_counter.most_common(100)

# 2. Analyze the Length of Each Ingredient Name
ingredient_lengths = [len(ingredient) for ingredient in ingredients]
average_length = sum(ingredient_lengths) / len(ingredient_lengths)
shortest_ingredient = min(ingredients, key=len)
longest_ingredient = max(ingredients, key=len)

# 3. Most Common Prefixes or Patterns
prefix_counter = Counter([ingredient.split()[0] for ingredient in ingredients if len(ingredient.split()) > 0])
top_prefixes = prefix_counter.most_common(10)

# 4. Most Common Words in Ingredients
word_counter = Counter(word for ingredient in ingredients for word in ingredient.split())
top_words = word_counter.most_common(100)

# Display Summary
print(f"Total Unique Ingredients: {total_unique_ingredients}")
print(f"Average Length of Ingredient Names: {average_length:.2f} characters")
print(f"Shortest Ingredient: '{shortest_ingredient}' ({len(shortest_ingredient)} characters)")
print(f"Longest Ingredient: '{longest_ingredient}' ({len(longest_ingredient)} characters)")
print("Top 10 Most Common Prefixes:", top_prefixes)
print("Top 10 Most Common Words:", top_words)

# 5. Visualization: Top Prefixes
prefixes, prefix_counts = zip(*top_prefixes)
plt.figure(figsize=(10, 6))
plt.bar(prefixes, prefix_counts)
plt.xlabel("Prefixes")
plt.ylabel("Count")
plt.title("Top 10 Most Common Prefixes in Ingredient Names")
plt.show()

# 6. Visualization: Top Words
words, word_counts = zip(*top_words)
plt.figure(figsize=(10, 6))
plt.bar(words, word_counts)
plt.xlabel("Words")
plt.ylabel("Count")
plt.title("Top 100 Most Common Words in Ingredient Names")

# Rotate the x-axis labels by 90 degrees
plt.xticks(rotation=90)

plt.tight_layout()  # This helps ensure everything fits nicely
plt.show()

# 7. Length Distribution of Ingredient Names
plt.figure(figsize=(10, 6))
plt.hist(ingredient_lengths, bins=20, color='skyblue', edgecolor='black')
plt.xlabel("Length of Ingredient Names (characters)")
plt.ylabel("Frequency")
plt.title("Distribution of Ingredient Name Lengths")
plt.show()
