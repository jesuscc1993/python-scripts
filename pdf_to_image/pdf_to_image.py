import pymupdf
import os

from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from mtlogger import logger
from mtprompt import Prompt
from pathlib import Path

OUTPUT_FORMAT = 'WEBP'
OUTPUT_EXTENSION = OUTPUT_FORMAT.lower()
OUTPUT_QUALITY = 100
RESOLUTION_SCALE = 1.5

def main():
  parent_folder = Prompt.dir(
    'Enter the path to the parent folder containing the PDF files'
  )

  process_parent_folder(parent_folder)

def process_parent_folder(
  parent_folder_path: str,
):
  pdf_files = list(Path(parent_folder_path).glob('*.pdf'))
  if not pdf_files:
    logger.warn(f'No PDF files found in "{parent_folder_path}".')
    return

  for pdf_file in pdf_files:
    pdf_to_webp(parent_folder_path, str(pdf_file))

def process_page(
  pdf_document: pymupdf.Document,
  page_number: int,
  output_path: str,
):
  page = pdf_document.load_page(page_number)
  matrix = pymupdf.Matrix(RESOLUTION_SCALE, RESOLUTION_SCALE)
  pixmap = page.get_pixmap(matrix = matrix)

  img = Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)
  img_path = os.path.join(output_path, f'{page_number + 1:03}.{OUTPUT_EXTENSION}')
  img.save(img_path, OUTPUT_FORMAT, quality = OUTPUT_QUALITY)
  logger.log(f'Saved: "{img_path}".')

def pdf_to_webp(
  parent_folder_path: str,
  pdf_path: str,
):
  pdf_name = Path(pdf_path).stem
  output_path = os.path.join(parent_folder_path, pdf_name)
  os.makedirs(output_path, exist_ok = True)

  pdf_document = pymupdf.open(pdf_path)
  num_pages = len(pdf_document)

  with ThreadPoolExecutor() as executor:
    _ = [
      executor.submit(process_page, pdf_document, page_number, output_path)
      for page_number in range(num_pages)
    ]

  logger.log(f'Saved: "{output_path}".\n')
  pdf_document.close()

if __name__ == '__main__':
  try:
    main()
  except Exception as ex:
    logger.unhandled_error(ex)

  Prompt.enter_to_exit()
