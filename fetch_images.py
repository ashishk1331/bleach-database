import requests
import os
import json
from PIL import Image


def check_folder_else_create(name):
    if not os.path.exists(name):
        os.makedirs(name)
        print(f"✅ {name} folder created.")
    else:
        print(f"☑️ Folder already exists: {name}")


def get_center_box(width, height):
    if width == height:
        return (0, 0, width, height)
    elif width < height:
        up = (height - width) // 2
        return (0, up, width, width + up)
    else:  # width > height
        left = (width - height) // 2
        return (left, 0, height + left, height)


def crop_scale(path):
    threshold = 256

    img = Image.open(path)

    bbox = get_center_box(*img.size)

    img = img.crop(bbox)

    if img.size[0] > threshold:
        img = img.resize((threshold, threshold))

    img.save(path)


def get_image(url, path):
    global mini

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


with open("data/log.json", "r", encoding="utf-8") as file:
    data = json.loads(file.read())

check_folder_else_create("images")

for ch in data.keys():
    base_path = f"images/{ch}"
    check_folder_else_create(base_path)
    with open(f"data/{ch}.json", "r", encoding="utf-8") as file:
        for char in json.loads(file.read()):
            get_image(char["avatar"], f'{base_path}/{char["slug"]}.png')
