import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_content(url: str) -> str:
  try:
      response = requests.get(url)
      response.raise_for_status()
      return response.text
  except requests.exceptions.HTTPError as e:
      print(f"Error fetching {url}: {e}")
      return ""

def get_acne_types(base_url: str) -> list:
  content = fetch_content(base_url)
  soup = BeautifulSoup(content, 'html.parser')
  acne_types = []

  for link in soup.find_all('a', href=True):
      if 'acne' in link['href']:
          full_url = urljoin(base_url, link['href'])
          acne_types.append((link.text.strip(), full_url))

  return acne_types

def get_images_from_page(url: str) -> list:
  content = fetch_content(url)
  if not content:
      return []

  soup = BeautifulSoup(content, 'html.parser')
  images = []

  # List of filenames to exclude
  exclude_files = [
      'Instagram_Glyph_Gradient_RGB.png', 'nih.png', 'return-top.png',
      'us_flag_small.png', 'feed.png', 'i_share_fb.png', 'i_share_twitter.png',
      'i_social_media_toolkit.png', 'm_logo_25.png', 'nihlogo.png', 'en.png', 'pdf.jpg', 'site-MMT2.png', 'Fraxel.jpg'
  ]

  for img in soup.find_all('img', src=True):
      img_url = urljoin(url, img['src'])
      if img_url.endswith(('.jpg', '.jpeg', '.png')) and not any(exclude in img_url for exclude in exclude_files):
          images.append(img_url)

  return images

def sanitize_folder_name(name: str) -> str:
  """Sanitize folder"""
  return "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()

def download_images(image_urls: list, folder: str):
  os.makedirs(folder, exist_ok=True)
  for img_url in image_urls:
      try:
          img_data = requests.get(img_url).content
          img_name = os.path.join(folder, os.path.basename(img_url))
          with open(img_name, 'wb') as img_file:
              img_file.write(img_data)
          print(f"Downloaded {img_name}")
      except Exception as e:
          print(f"Error downloading {img_url}: {str(e)}")

def main():
  base_url = "https://dermnetnz.org/topics/acne-and-other-follicular-disorders"
  acne_types = get_acne_types(base_url)

  output_folder = "images"

  for acne_name, acne_url in acne_types:
      print(f"Processing {acne_name}: {acne_url}")
      image_urls = get_images_from_page(acne_url)
      if image_urls:
          download_images(image_urls, folder=output_folder)
      else:
          print(f"No images found for {acne_name}")

if __name__ == "__main__":
  main()
