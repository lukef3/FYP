import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_curve, auc, f1_score, accuracy_score
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Define constants
NUM_ALLERGENS = 14  # Number of allergens in your dataset
IMAGE_SIZE = 224  # Resize images to 224x224 (standard for CNNs)
BATCH_SIZE = 32  # Adjust based on GPU memory
EPOCHS = 10  # Number of training epochs
LEARNING_RATE = 0.001  # Learning rate for optimizer
DATASET_PATH = "dataset"  # Path to your dataset

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# Custom Dataset Class
class FoodAllergenDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image_path = item["image_path"]

        try:
            # Attempt to open the image
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"Skipping corrupted or unreadable image: {image_path} (Error: {e})")
            # Return a placeholder image and label
            image = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), (0, 0, 0))  # Black image
            allergens = torch.zeros(NUM_ALLERGENS, dtype=torch.float32)  # Zero vector for allergens
            return image, allergens

        allergens = torch.tensor(item["allergens"], dtype=torch.float32)

        if self.transform:
            image = self.transform(image)

        return image, allergens


# Load dataset
def load_dataset(dataset_path):
    data = []
    for recipe_folder in os.listdir(dataset_path):
        recipe_path = os.path.join(dataset_path, recipe_folder)
        allergens_json_path = os.path.join(recipe_path, "allergens.json")

        if os.path.exists(allergens_json_path):
            with open(allergens_json_path, "r") as f:
                metadata = json.load(f)
                # Check if all allergens are 0
                if any(metadata["allergens"]):  # Only proceed if at least one allergen is present
                    for image_name in metadata["images"]:
                        image_path = os.path.join(recipe_path, image_name)
                        if os.path.exists(image_path):
                            try:
                                # Verify the image is valid
                                with Image.open(image_path) as img:
                                    img.verify()
                                data.append({
                                    "image_path": image_path,
                                    "allergens": metadata["allergens"]
                                })
                            except Exception as e:
                                print(f"Skipping corrupted image: {image_path} (Error: {e})")
    return data


# Preprocess dataset
def preprocess_dataset(data):
    # Split into training and validation sets
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)

    # Define transforms
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # ImageNet normalization
    ])

    # Create datasets
    train_dataset = FoodAllergenDataset(train_data, transform=transform)
    val_dataset = FoodAllergenDataset(val_data, transform=transform)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    return train_loader, val_loader


# Define CNN model
class AllergenCNN(nn.Module):
    def __init__(self, num_allergens):
        super(AllergenCNN, self).__init__()
        self.backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)  # Use pre-trained ResNet18
        self.backbone.fc = nn.Linear(self.backbone.fc.in_features, num_allergens)  # Replace final layer

    def forward(self, x):
        return self.backbone(x)


# Training function
def train(model, train_loader, val_loader, criterion, optimizer, epochs):
    model.to(device)
    best_val_loss = float("inf")

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            # Zero the gradients
            optimizer.zero_grad()

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward pass and optimize
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Print training loss
        epoch_loss = running_loss / len(train_loader)
        train_losses.append(epoch_loss)
        print(f"Epoch [{epoch + 1}/{epochs}], Loss: {epoch_loss:.4f}")

        # Validation
        val_loss = evaluate(model, val_loader, criterion)
        val_losses.append(val_loss)
        print(f"Validation Loss: {val_loss:.4f}")

        # Save the best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "best_model.pth")

    # Plot training and validation loss curves
    plt.figure()
    plt.plot(train_losses, label="Training Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss")
    plt.legend()
    plt.savefig("loss_curves.png")
    plt.show()


# Evaluation function
def evaluate(model, val_loader, criterion):
    model.eval()
    val_loss = 0.0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            val_loss += criterion(outputs, labels).item()

    return val_loss / len(val_loader)


# Generate performance metrics and plots
def evaluate_model(model, val_loader):
    model.eval()
    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            preds = torch.sigmoid(outputs) > 0.5  # Convert logits to binary predictions
            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    all_labels = np.array(all_labels)
    all_preds = np.array(all_preds)

    # Confusion Matrix
    cm = confusion_matrix(all_labels.argmax(axis=1), all_preds.argmax(axis=1))
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.savefig("confusion_matrix.png")
    plt.show()

    # Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(all_labels.ravel(), all_preds.ravel())
    plt.figure()
    plt.plot(recall, precision, marker=".")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.savefig("precision_recall_curve.png")
    plt.show()

    # ROC Curve
    fpr, tpr, _ = roc_curve(all_labels.ravel(), all_preds.ravel())
    roc_auc = auc(fpr, tpr)
    plt.figure()
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.2f})")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.savefig("roc_curve.png")
    plt.show()

    # Accuracy and F1-Score
    accuracy = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="macro")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1-Score: {f1:.4f}")


# Main function
def main():
    # Load and preprocess dataset
    data = load_dataset(DATASET_PATH)
    train_loader, val_loader = preprocess_dataset(data)

    # Initialize model, loss function, and optimizer
    model = AllergenCNN(NUM_ALLERGENS)
    criterion = nn.BCEWithLogitsLoss()  # Binary cross-entropy loss for multi-label classification
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Train the model
    train(model, train_loader, val_loader, criterion, optimizer, EPOCHS)

    # Evaluate the model and generate performance plots
    evaluate_model(model, val_loader)


if __name__ == "__main__":
    main()