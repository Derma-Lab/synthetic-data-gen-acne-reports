import os
from PIL import Image

def resize_images(input_folder, output_folder, size=(269, 187)):
  os.makedirs(output_folder, exist_ok=True)

  for filename in os.listdir(input_folder):
      if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
          try:
              with Image.open(os.path.join(input_folder, filename)) as img:
                  img = img.resize(size, Image.LANCZOS)
                  img.save(os.path.join(output_folder, filename))
                  print(f"Resized and saved: {filename}")
          except Exception as e:
              print(f"Error processing {filename}: {e}")

input_folder = 'images'
output_folder = 'resize_img'

resize_images(input_folder, output_folder)