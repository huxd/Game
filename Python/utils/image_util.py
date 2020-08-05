import os
from PIL import Image


im = Image.open("3.png")
print im.mode
im = Image.open("AppIcon20x20@2x_1.png")
print im.mode
path = "/Users/huxuedong/Downloads/Payload"
for root, dirs, files in os.walk(path):
    for name in files:
        if not name.endswith('.png'):
            continue
        file_path = os.path.join(root, name)
        im = Image.open(file_path)
        # if im.mode == 'RGBA':
        #     print name