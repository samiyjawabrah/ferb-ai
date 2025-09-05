import torch
import torchvision.models as models
from torchvision import transforms
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from PIL import Image
import os

IMG_WIDTH = 224
IMG_HEIGHT = 224
image_dict = { "Bathroom": 0, "Bedroom": 1, "DiningRoom": 2, "Kitchen": 3, "LivingRoom": 4 }
LR = 0.0001
EPOCHS = 5
data_dir = '../data/House_Room_Dataset/'

# test_transform = transforms.Compose([
  #   transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
  #   transforms.ToTensor(),
  #   transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
  # ])

def main():

  dataset = load_data(data_dir)
  train_data, val_data = train_test_split(dataset, train_size=0.8, test_size=0.2) 

  train_dataloader = DataLoader(train_data, batch_size=32, shuffle=True)
  val_dataloader = DataLoader(val_data, batch_size=32, shuffle=False) #Shuffle should be false for validation set
  
  model =  models.resnet18(pretrained=True)
  num_features = model.fc.in_features
  model.fc = nn.Linear(num_features,5)

  criterion = nn.CrossEntropyLoss()
  optimizer = optim.Adam(model.parameters(), lr=LR)

  train_losses = []
  
  for epoch in range(EPOCHS):
    train_loss = 0
    for images, labels in train_dataloader:
        
      outputs = model(images)
      loss = criterion(outputs,labels)
      train_loss += loss.item() #Adds the numeric loss, must have the .item()
      loss.backward()
      optimizer.step()
      optimizer.zero_grad()
    
    avg_train_loss = train_loss / len(train_dataloader)
    train_losses.append(avg_train_loss)
    print(f"Epoch {epoch+1}/{EPOCHS} - Training Loss {avg_train_loss:.4f}")

    val_loss = 0
    correct = 0
    total = 0
    with torch.no_grad():
      for images, labels in val_dataloader:
        
        val_output = model(images)
        loss = criterion(val_output, labels)
        val_loss += loss.item()

        _, predicted = val_output.max(1)
        correct += (predicted == labels).sum().item()
        total += labels.size(0)
    avg_val_loss = val_loss / len(val_dataloader)
    val_accuracy = correct / total * 100
    print(f"Validation Loss: {avg_val_loss:.4f}, Accuracy: {val_accuracy:.2f}%")

  if not os.path.exists("models"):
    os.makedirs("models")

  torch.save(model.state_dict(), 'models/house_room_model.pth')

  return model, train_losses


def load_data(data_dir):

  train_transform = transforms.Compose([
    transforms.RandomVerticalFlip(0.5),
    transforms.ColorJitter(brightness=0.2),
    transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) 
  ])

  images = []
  labels = []
  for filename in os.listdir(data_dir):
      folder_path = os.path.join(data_dir, filename)
      for pic in os.listdir(folder_path):
          pic_path = os.path.join(folder_path,pic)
          image = Image.open(pic_path)
          if image is not None:
              transformed_image = train_transform(image)
              images.append(transformed_image)
              labels.append(image_dict[filename])
          else:
                continue
  dataset = list(zip(images,labels))
  return dataset


if __name__ == '__main__':
    main()
    # images = load_data('../data/House_Room_Dataset/')
    # print(images[0][0].shape)