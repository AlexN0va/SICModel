
## ASSUMES ALL FILES ARE PNGs

#               ....... === Pytorch Setup === .......
# Taken from Qingxi's tutorial https://colab.research.google.com/drive/1cY8NtwnK2esx-nvlxl5JTLYjmG2g5_-s?usp=sharing#scrollTo=-hMA-66wEWmh



# install packages
!pip install opencv-python matplotlib supervision
!pip install 'git+https://github.com/facebookresearch/segment-anything.git'
!pip install torch
!python3 -m pip install --upgrade torchvision
!python3 -m pip install --upgrade os
!python3 -m pip install os-sys


import os
import sys
import cv2
import torch
import torchvision
import numpy as np
from PIL import Image
import supervision as sv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import natsorted


!sudo apt-get update
!sudo apt install imagemagick
!python3 -m pip install --upgrade pip
!python3 -m pip install --upgrade Pillow
!python3 -m pip install --upgrade zstandard

# Check package versions
print("PyTorch version:", torch.__version__)
print("Torchvision version:", torchvision.__version__)
print("CUDA is available:", torch.cuda.is_available())

# download the SAM model
!wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
# ensure we are at to the root path
sys.path.append("..")
# import some packages from segment anything
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
# the model we need to load
sam_checkpoint = "sam_vit_h_4b8939.pth"
model_type = "vit_h"
# choose cude GPU as device
device = "cuda"
# load the model
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
# create the generator that segment objects
mask_generator = SamAutomaticMaskGenerator(sam)
#

folderPath = "/content/mris" # Replace with the path of the folder containing MRIs you want to use

# folderPath = input("Absolute path to the directory containing images (no trailing slash): ")

imageIndex = 0 # creates a variable to store the index of the image in the directory

def showImage(path,size):
  inputImage = cv2.imread(path)
  plt.figure(figsize=(size,size))
  plt.imshow(inputImage)
  plt.axis('off')
  plt.show()

def showImageAxes(path,size,title):
  inputImage = cv2.imread(path)
  plt.figure(figsize=(size,size))
  plt.imshow(inputImage)
  plt.title(title)
  plt.show()

listOfPaths = [] # creates an empty list to put paths in, so that we can visualize images in a grid
listOfCompressionAmounts = []

for filename in os.listdir(folderPath):
  imageIndex += 1
  filePath = folderPath + "/" + filename
  filePathWithoutExtension = filePath.rsplit( ".", 1 )[ 0 ] #removes .png extension

  print("filename: " + filename)
  print("folderpath: " + folderPath)
  print("file path: " + filePath)

  img = cv2.imread(filePath)
  mask = mask_generator.generate(img)

  masks = [ #set up mask generation stuff
      m['segmentation']
      for m
      in sorted(mask, key=lambda x: x['area'], reverse=True)
  ]

  """sv.plot_images_grid(
      images=masks[:4],
      grid_size = (2, 2),
      size=(8, 16)
  )"""

  print(str(mask[1]["bbox"])) # returns the boundary of the first mask
  print(str(mask[1]["bbox"]))
  box = mask[1]["bbox"]

  # defining x, y of top left corner, as well as width and height for the boundary box
  x=box[0]
  y=box[1]
  h=box[3]
  w=box[2]

  # defining original size of the image

  origW = img.shape[1]
  origH = img.shape[0]


  # print the size of the original image
  sizeConverted = os.path.getsize(filePath)
  print(" size of uncropped png: " + str(sizeConverted/1000000))

  foregroundFilePath = filePathWithoutExtension + "Foreground.png" # creates name for foreground file
  #!convert -crop 144x132+232+269 "/content/images/mri(11).png" "/content/images/mri(11)Foreground.png"
  #convert -crop 497x489+7+12 /content/images/mri(11).png /content/images/mri(11)Foreground.png


  # crop image according to segment anything boundary box
  os.system("convert -crop " + str(w) + "x" + str(h) + "+" + str(x) + "+" + str(y) + "  '" + filePath + "' '" +  foregroundFilePath +"'")


  # print size of cropped image
  sizeConverted = os.path.getsize(foregroundFilePath)
  print(" size of cropped png: " + str(sizeConverted/1000000))

  #.       === Create background image ===
  openImg = Image.open(filePath)
  fig, ax = plt.subplots()
  ax.imshow(openImg)
  # puts a black box over the cut image
  rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='black', facecolor='black')
  ax.add_patch(rect)

  #removes whitespace around image
  plt.axis('off')
  backgroundFilePath = filePathWithoutExtension + "Background.png"
  plt.savefig(backgroundFilePath, bbox_inches="tight",pad_inches = 0) # saves background image
  plt.close() #closes image

  # shows the foreground and background separately
  # showImageAxes(foregroundFilePath, 5, "foreground")
  # showImageAxes(backgroundFilePath, 5, "background")

  # converts background to an extremely lossy jpeg
  # make sure you've run sudo apt install imagemagick (block 2, see setup section)
  backgroundFilePathJPEG = filePathWithoutExtension + "Background.jpeg"
  os.system("convert '" + backgroundFilePath + "' -type TrueColor -quality 1 '" + backgroundFilePathJPEG+"'") #
  # showImage(backgroundFilePathJPEG, 5)

  resizedFilePath = filePathWithoutExtension + "Resized.jpeg"
  os.system("convert '" + backgroundFilePath + "' -resize " + str(origW) + "x" + str(origH) + " '" + resizedFilePath+"'")

  outputFilePath = filePathWithoutExtension + "Output.png"
  os.system("composite '" + foregroundFilePath + "' '" + resizedFilePath + "' -geometry +" + str(x) + "+" + str(y) + " '" + outputFilePath+"'")
  print(str(x))
  print(str(y))

  os.system("identify " + filePath)
  os.system("identify " + outputFilePath)

  # Create Data Set
  originalSize = os.path.getsize(filePath)
  finalSize = os.path.getsize(outputFilePath)
  percentDifference = 1.0 - (finalSize/originalSize) # percent difference

  listOfPaths.append(outputFilePath)
  listOfCompressionAmounts.append(percentDifference)


  showImageAxes(filePath, 6, filePath)
  showImageAxes(outputFilePath, 6, outputFilePath)

print(str(listOfPaths))
print(str(listOfCompressionAmounts))

