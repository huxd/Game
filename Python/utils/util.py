#-*- coding: utf-8 -*-

# 全量编译：148s
# 增量编译 + 去掉海外数据：12s

import os
import time
import datetime
import svn_util
import shutil
import os_util
import time_util
import logging
import platform
import sys
import argparse
import struct
from Queue import Queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
game_path = 'E:\\g78\\trunk\\client\\game'
script_npk_path = os.path.join(game_path, 'script.npk')
script_path = os.path.join(game_path, 'script')
packer_path = os.path.join(os.path.dirname(game_path), 'packer')
file_queue = Queue()
parser = None

def tryImport(module_name):
    try:
        __import__(module_name)
    except:
        os.system('pip install ' + module_name)
        __import__(module_name)

def initSysPath():
    lib_path = os.path.join(packer_path, 'auto_build', 'libs', 'win')
    sys.path.append(lib_path)
    tryImport('watchdog')

initSysPath()

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def buildNpk(target_dir):
    pack_tool = os.path.join(packer_path, 'neox_packer', 'nxspack.exe')
    cmd = '%s  -p -i .svn -case %s' % (pack_tool, target_dir)
    os.system(cmd)

# 写入版本号
def WriteNpkVersion(npk_file):
    cur_version_str = '999.999.99999'
    cur_version = cur_version_str.split(".")
    write_data = struct.pack('=iii', int(cur_version[0]), int(cur_version[1]), int(cur_version[2]))
    wf = file(npk_file, 'r+b')
    wf.seek(8)
    wf.write(write_data)
    wf.close()

def GetScriptNpkChangeTime():
    # 获取script.npk倒数第二次svn更新时间
    info = svn_util.getNthLogInfo(script_npk_path, 2)
    delay_time = 0
    if 'Last Changed Date' not in info:
        # 如果用当前版本的svn信息就提前10分钟
        info = svn_util.getInfo(script_npk_path)
        delay_time = 10 * 3600
    changed_date = info.get('Last Changed Date')
    changed_date = None
    if not changed_date:
        # 如果获取不了script.npk的svn信息就用当前时间
        logging.error("Get scrip.npk svn info failed.")
        return None
    else:
        changed_date = changed_date.split('+')[0].strip()
        changed_time = time_util.getTimestamp(changed_date) - delay_time
    return changed_time

def initPatchNpk():
    global file_queue
    
    logging.info("<<<<<<<< Init script.npk >>>>>>>>")
    changed_time = GetScriptNpkChangeTime()
    if not changed_time:
        buildNpk(script_path)
        return

    # 寻找所有大于这个时间修改的文件
    for root, dirs, files in os.walk(script_path):
        if '.svn' in root:
            continue
        for filename in files:
            file_path = os.path.join(root, filename)

            if os.path.getmtime(file_path) <= changed_time:
                continue
            # 过滤掉多语言
            if not parser.oversea and 'game_data_langs' in file_path:
                continue
            file_queue.put(file_path)
            logging.info("Changed %s", file_path)

    buildPatchNpk()
    logging.info("<<<<<<<< End init script.npk >>>>>>>>")

def buildPatchNpk():
    global file_queue
    if file_queue.empty():
        return
    
    logging.info("<<<<<<<< Build scrip.npk Begin >>>>>>>>")
    tmp_path = os.path.join(game_path, 'script_tmp')
    if os.path.isdir(tmp_path):
        shutil.rmtree(tmp_path)

    record_dict = dict()
    while not file_queue.empty():
        file_path = file_queue.get()
        if record_dict.get(file_path):
            continue
        record_dict[file_path] = True
        rel_path = os.path.relpath(file_path, script_path)
        os_util.tryCopy(file_path, os.path.join(tmp_path, rel_path))

    buildNpk(tmp_path)
    if os.path.isdir(tmp_path):
        shutil.rmtree(tmp_path)

    mergeNpk()
    logging.info("<<<<<<<< Build scrip.npk OK >>>>>>>>")

def mergeNpk():
    import package
    main_npk = package.nxnpk(script_npk_path[:-4])
    patch_npk_path = os.path.join(game_path, 'script_tmp.npk')
    patch_npk = package.nxnpk(patch_npk_path[:-4])

    tmp_path = 'script.new.npk'
    writer = package.npkwriter()
    writer.open(tmp_path, 0)

    write_record = dict()
    merge(writer, patch_npk, write_record)
    merge(writer, main_npk, write_record)

    writer.flush()
    WriteNpkVersion(tmp_path)
    shutil.move(tmp_path, script_npk_path)

def merge(writer, npk, write_record):
    indice_vector = npk.get_indice_vector()
    for cur in indice_vector:
        if write_record.get(cur):
            continue
        write_record[cur] = True
        index_info = npk.get_file_index_info_by_id(cur)
        file_data = npk.get_raw_file_by_id(cur)
        if file_data == None:
            file_data = ''
        assert writer.add(cur, file_data, index_info[1], index_info[2], index_info[3], index_info[4], index_info[5]) == True

class ScriptEventHandler(FileSystemEventHandler):
    def on_moved(self, event):
        if event.is_directory:
            return
        file_path = event.dest_path
        if not file_path.endswith('.py'):
            return
        logging.info("Moved %s", file_path)
        global file_queue
        file_queue.put(file_path)

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if not file_path.endswith('.py'):
            return
        logging.info("Created %s", file_path)
        global file_queue
        file_queue.put(file_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if not file_path.endswith('.py'):
            return
        logging.info("Modified %s", file_path)
        global file_queue
        file_queue.put(file_path)


def startListen():
    event_handler = ScriptEventHandler()
    observer = Observer()
    observer.schedule(event_handler, script_path, recursive=True)
    observer.start()
    start = time.time()
    initPatchNpk()
    logging.info("Elapsed Time %ss" % int(time.time() - start))
    logging.info("<<<<<<<< Begin listening file change >>>>>>>>")
    try:
        while True:
            time.sleep(1)
            buildPatchNpk()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def ParseArgs(args):
    parser = argparse.ArgumentParser(prog="ScriptBuilder", description="Build script.npk", usage='%(prog)s [options]')
    parser.add_argument('-o', '--oversea', action='store_true', required=False, default=False)
    return parser.parse_args(args)

if __name__ == '__main__':
    args_list = sys.argv[1:]
    parser = ParseArgs(args_list)

    if platform.platform().find("Windows") != -1:
        startListen()
    else:
        logging.info("Don't support mac now.")
