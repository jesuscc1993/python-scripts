import os
from PIL import Image

ICON_FILENAME = "icon.ico"
DESKTOP_INI_FILENAME = "desktop.ini"

def process_parent_folder(image_filenames):
    parent_folder = input("Enter the path to the parent folder containing the folders you want to generate icons for.\nLeave empty instead to provide and process a single folder instead.\nPARENT_FOLDER: ")

    if parent_folder == '':
        target_folder = input("\nEnter the path to the specific folder you want to generate an icon for:\nFOLDER: ")

        if not os.path.isdir(target_folder):
            print(f'The specified path "{target_folder}" is not a directory.')
            return

        print('')
        process_folder(target_folder, image_filenames)

    else:
        if not os.path.isdir(parent_folder):
            print(f'The specified path "{parent_folder}" is not a directory.')
            return

        print('')

    for root, dirs, _ in os.walk(parent_folder):
        for dir_name in dirs:
            item_path = os.path.join(root, dir_name)
            process_folder(item_path, image_filenames)

    print(f"\nFinished generating icons.")

def process_folder(item_path, image_filenames):
    image_path = None
    for image_filename in image_filenames:
        potential_path = os.path.join(item_path, image_filename)
        if os.path.exists(potential_path):
            image_path = potential_path
            break

    if image_path:
        ico_path = os.path.join(item_path, ICON_FILENAME)
        png_to_ico(image_path, ico_path)
        set_folder_icon(item_path)
    else:
        print(f"No suitable image found in {item_path}")

def png_to_ico(image_path, ico_path):
    try:
        if os.path.exists(ico_path):
            os.unlink(ico_path)

        with Image.open(image_path) as img:
            if img.width < 256:
                img = img.resize((256, int(256 * img.height / img.width)), resample=Image.LANCZOS)
            img.thumbnail((256, 256), Image.LANCZOS)
            background = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            offset = (int((256 - img.size[0]) / 2), int((256 - img.size[1]) / 2))
            background.paste(img, offset)
            background.save(ico_path, format='ICO', sizes=[(256, 256)])
    except Exception as e:
        print(f"Error converting {image_path} to ICO: {e}")

def set_folder_icon(folder_path):
    try:
        desktop_ini_path = os.path.join(folder_path, DESKTOP_INI_FILENAME)
        icon_path = os.path.join(folder_path, ICON_FILENAME)

        if os.path.exists(desktop_ini_path):
            os.system(f'attrib -h -s "{desktop_ini_path}"')

        with open(desktop_ini_path, "w") as desktop_ini:
            desktop_ini.write("[.ShellClassInfo]\n")
            desktop_ini.write(f"IconResource={ICON_FILENAME},0\n")

        os.system(f'attrib +h +s "{desktop_ini_path}"')
        os.system(f'attrib +h "{icon_path}"')
        os.system(f'attrib +s "{folder_path}"')

        print(f'Saved "{icon_path}" and "{desktop_ini_path}".')
    except PermissionError:
        print(f'Permission denied: "{desktop_ini_path}". You may need to run the script as an administrator.')
    except Exception as e:
        print(f'Error setting folder icon to "{folder_path}": {e}')
