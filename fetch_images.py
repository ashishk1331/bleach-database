import requests
import os
import json
from PIL import Image


def check_folder_else_create(name: str):
    """Check else create folder.

    It checks if the folder exists; if not, it creates it.

    Args:
        name: path/name to the folder
    """
    if not os.path.exists(name):
        os.makedirs(name)
        print(f"✅ {name} folder created.")
    else:
        print(f"☑️ Folder already exists: {name}")


def get_center_box(width: int, height: int) -> (int, int, int, int):
    """Calculate the center square box for the given width and height.

    Args:
        width: Actual width of the image
        heigth: Actual height of the image

    Returns:
        (left, upper, right, bottom): the center square box coordinates
    """
    if width == height:
        return (0, 0, width, height)
    elif width < height:
        up = (height - width) // 2
        return (0, up, width, width + up)
    else:  # width > height
        left = (width - height) // 2
        return (left, 0, height + left, height)


def crop_scale(path: str):
    """Center crop and scale the image.

    Applies a center crop to the avatar image and shrinks images to a width of `256px`.

    Args:
        path: path to the saved image
    """
    threshold = 256

    img = Image.open(path)

    bbox = get_center_box(*img.size)

    img = img.crop(bbox)

    if img.size[0] > threshold:
        img = img.resize((threshold, threshold))

    img.save(path)


def get_image(url: str, path: str):
    """Fetch image from the `url` and save at `path`.

    Aside from saving the image at disk, it also center crops the image and scales down large images.

    Args:
        url: web url to the png image
        path: local path for the image

    Returns:
        Nothing.
    """

    if url is None:
        return

    if isinstance(url, list):
        url = url[0]

    if os.path.exists(path):
        print(f"☑️ Already written: {path}")
    else:
        with open(path, "wb") as image:
            resp = requests.get(url)
            image.write(resp.content)
            print(f"✅ {path} written.")

    # finally resize the image
    crop_scale(path)


def main():
    """Entry point.

    Loads all characters and saves their avatar using slug from the data, respectively.
    """
    with open("data/log.json", "r", encoding="utf-8") as file:
        data = json.loads(file.read())

    check_folder_else_create("images")

    for ch in data.keys():
        base_path = f"images/{ch}"
        check_folder_else_create(base_path)
        with open(f"data/{ch}.json", "r", encoding="utf-8") as file:
            for char in json.loads(file.read()):
                get_image(char["avatar"], f'{base_path}/{char["slug"]}.png')

if __name__ == '__main__':
    main()
