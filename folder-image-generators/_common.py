import os
from PIL import Image

FOLDER_IMAGE_FILENAME = "folder.jpg"
FOLDER_IMAGE_SIZE = 256

def process_parent_folder(process_folder):
    parent_folder = input("Enter the path to the parent folder containing the folders you want to generate icons for.\nLeave empty instead to provide and process a single folder instead.\nPARENT_FOLDER: ")

    if parent_folder == '':
        target_folder = input("\nEnter the path to the specific folder you want to generate an icon for:\nFOLDER: ")

        if not os.path.isdir(target_folder):
            print(f'The specified path "{target_folder}" is not a directory.')
            return

        print('')
        process_folder(target_folder)

    else:
        if not os.path.isdir(parent_folder):
            print(f'The specified path "{parent_folder}" is not a directory.')
            return

        print('')

    for root, dirs, _ in os.walk(parent_folder):
        for dir_name in dirs:
            item_path = os.path.join(root, dir_name)
            process_folder(item_path)

    print(f"Finished generating icons.")

def save_resized_image(img, folder_path):
    original_width, original_height = img.size

    if original_width > FOLDER_IMAGE_SIZE and original_height > FOLDER_IMAGE_SIZE:
        if original_width < original_height:
            new_width = FOLDER_IMAGE_SIZE
            new_height = int((FOLDER_IMAGE_SIZE / original_width) * original_height)
        else:
            new_height = FOLDER_IMAGE_SIZE
            new_width = int((FOLDER_IMAGE_SIZE / original_height) * original_width)

        img = img.resize((new_width, new_height), Image.LANCZOS)

    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, TRANSPARENT_COLOR)
        background.paste(img, (0, 0), img)
        img = background

    output_file_path = os.path.join(folder_path, FOLDER_IMAGE_FILENAME)
    img.save(output_file_path)

    print(f"Saved {output_file_path}.\n")