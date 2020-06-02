import os
from PIL import Image


im = Image.open("AppIcon20x20@2x~ipad.png")
path = "C:\\Users\\huxuedong\\Downloads\\g78_pub_0403_1719_r245759\\Payload\\client.app"
for root, dirs, files in os.walk(path):
    for name in files:
        if not name.endswith('.png'):
            continue
        file_path = os.path.join(root, name)
        im = Image.open(file_path)
        if im.mode == 'RGBA':
            print name