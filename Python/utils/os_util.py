import os
import shutil
import requests

def tryCopy(src_path, target_path):
    target_dir = os.path.dirname(target_path)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    shutil.copy(src_path, target_path)

def uploadFile(path):
    cmd = "scp %s root@39.98.204.104:~" % path
    os.system(cmd)

def downloadFile(url):
    req = requests.get(url)
    

uploadFile("/Users/huxuedong/Downloads/galaxy_2020_7_1.sql")