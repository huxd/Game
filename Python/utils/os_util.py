import os
import shutil

def tryCopy(src_path, target_path):
    target_dir = os.path.dirname(target_path)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    shutil.copy(src_path, target_path)
