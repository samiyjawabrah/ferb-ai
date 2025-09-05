import torch
import torchvision.models as models
from torchvision import transforms
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
# from sklearn import train_test_split
from PIL import Image
import os

IMG_WIDTH = 224
IMG_HEIGHT = 224
image_dict = { "Bathroom": 0, "Bedroom": 1, "DiningRoom": 2, "Kitchen": 3, "LivingRoom": 4 }


def main():

  dataloader = DataLoader(load_data('../data/House_Room_Dataset/'), batch_size=32, shuffle=True)

  train_transform = transforms.Compose([
    transforms.RandomVerticalFlip(15),
    transforms.ColorJitter(brightness=0.2),
    transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)) 
  ])

  test_transform = transforms.Compoe([
    transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
  ])



  model =  models.resnet18(pretrained=True)

  return


def load_data(data_dir):

  train_transform = transforms.Compose([
    transforms.RandomVerticalFlip(15),
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

  return (images,labels)


if __name__ == '__main__':
    # main()
    images = load_data('../data/House_Room_Dataset/')
    print(images[0][0].shape)