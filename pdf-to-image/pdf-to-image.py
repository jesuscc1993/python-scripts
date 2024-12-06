import pymupdf
import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def main():
  parent_folder = input('Enter the path to the parent folder containing the PDF files:\n')
  if not os.path.isdir(parent_folder):
    print(f'The specified path "{parent_folder}" is not a directory.')
  else:
    print('')

    for pdf_file in Path(parent_folder).glob('*.pdf'):
      pdf_to_webp(parent_folder, str(pdf_file))

def process_page(pdf_document, page_number, output_path):
  page = pdf_document.load_page(page_number)
  pixmap = page.get_pixmap()
  img = Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)
  img_path = os.path.join(output_path, f'{page_number + 1:03}.webp')
  img.save(img_path, 'WEBP', lossless=True)
  print(f'Saved: "{img_path}".')

def pdf_to_webp(parent_folder, pdf_path):
  pdf_name = Path(pdf_path).stem
  output_path = os.path.join(parent_folder, pdf_name)
  os.makedirs(output_path, exist_ok=True)

  pdf_document = pymupdf.open(pdf_path)
  num_pages = len(pdf_document)

  with ThreadPoolExecutor() as executor:
    _ = [
      executor.submit(process_page, pdf_document, page_number, output_path)
      for page_number in range(num_pages)
    ]

  print(f'Saved: "{output_path}".\n')
  pdf_document.close()

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'An unexpected error occurred: {e}')
  input('Press Enter to exit...')
