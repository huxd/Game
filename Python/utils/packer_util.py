#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import os
import sys
import platform
import copy
import hashlib
import shutil

class Context(object):
    pass

NEOX_DIR_MAPPING = {
    'trunk': 'E:\\g78\\NeoX',
    'mtl': 'E:\\g78\\NeoX_mtl\\NeoX',
}

def Log(string, *args):
    print '[%s] %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), string % args)

def RunSysCmd(cur_cmd):
    Log('run cmd %s', cur_cmd)
    if os.system(cur_cmd) != 0:
        Log('run cmd %s failed', cur_cmd)
        exit(1)

def FileMd5(file_path):
    def read_chunks(f):
        block_size = 8 * 1024
        chunk = f.read(block_size)
        while chunk:
            yield chunk
            chunk = f.read(block_size)
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in read_chunks(f):
            m.update(chunk)
    return m.hexdigest()

def BuildEngine(context):
    cur_path = os.getcwd()
    os.chdir(os.path.join(context.packer_path, 'auto_build'))
    cmd = 'python auto_packer.py build -type %s -v %s -b %s -t %s -g %s -c %s -p %s -o mainland -neox %s' % (context.build_type, context.cur_ver_num, context.build_ver, context.target_path, context.game_path, context.cache_path, context.platform, context.noex_path)
    RunSysCmd(cmd)
    os.chdir(cur_path)

def DoUnipack(context):
    import project_config

    apk_name = 'mother_g78_1.60.1804.apk'
    apk_path = os.path.join(context.cur_target_path, apk_name)
    apk_abs_path = os.path.abspath(apk_path)
    target_abs_path = os.path.abspath(context.cur_target_path)
    cmd = "%s -i %s -o %s -g %s -ac %s -u %s -p %s" % ("UniPack_cmd_v4.0.exe", apk_abs_path, target_abs_path, 'g78', 
    "netease_45:ngshare_12,ngpush_7,amap_location,gmbridge_2,glsdk,vivo_performance,ngvoice_extend", project_config.UNIPACK_USER, project_config.UNIPACK_CMD_KEY)
    cur_path = os.getcwd()
    unipack_path = os.path.join(context.packer_path, 'android', 'autobuild', 'unipack')
    os.chdir(unipack_path)
    os.system(cmd)
    os.chdir(cur_path)

def InitContext(build_type, build_ver, build_platform, engine_type):
    context = Context()
    context.build_ver = build_ver
    context.build_type = build_type
    context.platform = build_platform

    if 'Windows' in platform.platform():
        context.target_path = 'E:\\g78\\build_target\\%s' % engine_type
        context.cache_path = 'E:\\g78\\build_target\\res_cache'
        context.packer_path = 'E:\\g78\\packer_mtl'
        context.game_path = 'E:\\g78\\trunk\\client\\game'
        context.noex_path = NEOX_DIR_MAPPING[engine_type]
    else:
        pass
    
    context.npk_packer_path = os.path.join(context.packer_path, 'neox_packer', 'npkpack.exe')
    context.nxs_packer_path = os.path.join(context.packer_path, 'neox_packer', 'nxspack.exe')
    context.npk_ini_path = os.path.join(context.packer_path, 'neox_packer', 'npkpack.ini')
    sys.path.append(os.path.join(context.packer_path, 'auto_build'))
    sys.path.append(os.path.join(context.packer_path, 'auto_build', 'libs'))

    context.cur_target_path = os.path.join(context.target_path, build_ver, build_platform)
    context.cur_ver_num = '1.65.10'

    return context

def GenPatchList(context):
    patch_list_path = os.path.join(context.target_path, '%s_%s_%s' % ('split', 'art', 'win'))
    if not os.path.isfile(patch_list_path):
        f = open(patch_list_path, 'wb')
        f.write('made_for_%s_%s' % ('art', 'win'))
        f.close()
    f = open(patch_list_path, 'rb')
    content = f.read()
    lines = content.split('\n')
    f.close()

    while lines and not lines[-1].strip():
        lines.pop(-1)

    last_list = copy.copy(lines)
    for npk_type, file_path in context.upload_file_list:
        if not npk_type:
            continue
        size = os.stat(file_path).st_size
        md5_str = FileMd5(file_path)
        lines.insert(-1, '%s %s %s %s' % (context.cur_ver_num, npk_type, size, md5_str))
    print patch_list_path
    f = open(patch_list_path, 'wb')
    f.write('\n'.join(lines))
    f.close()

def ClearNPKInfo(parent_path, path_header):
    rm_file_list = ['%s.lst' % path_header,
                    '%s.npk' % path_header,
                    '%s.npk.old' % path_header,
                    '%s.npk.map' % path_header]
    for rm in rm_file_list:
        cur_path = os.path.join(parent_path, rm)
        if os.path.exists(cur_path):
            os.remove(cur_path)
    return

def BuildNpk(context, path_header='res'):
    input_path = 'E:\\res'
    output_path = 'E:\\'
    # ClearNPKInfo(output_path, path_header)
    if os.path.exists(context.npk_ini_path):
        shutil.copy(context.npk_ini_path, 'npkpack.ini')
    # cur_cmd = '%s list -r %s\\* %s' % (context.npk_packer_path, input_path,
    #                                     os.path.join(output_path, '%s.lst' % path_header))
    # RunSysCmd(cur_cmd)
    cur_cmd = '%s pack -case -encrypt %s %s' % (context.npk_packer_path,
                                        os.path.join(output_path, '%s.lst' % path_header),
                                        os.path.join(output_path, '%s.npk' % path_header))
    RunSysCmd(cur_cmd)

def XXX(context):
    context.upload_file_list = []
    target_path = os.path.join(context.cur_target_path, '1.65.10', 'patch_res')
    print target_path
    for name in os.listdir(target_path):
        if not name.endswith('.npk'):
            continue
        npk_name = name.split('_')[1]
        file_path = os.path.join(target_path, name)
        context.upload_file_list.append((npk_name, file_path))
    GenPatchList(context)

def Test():
    for root, dirs, names in os.walk("E:\\g78\\trunk2\\client\\game\\res\\scene"):
        for name in names:
            file_path = os.path.join(root, name)
            if file_path.find("scene") != -1 and (file_path.find("_r.") != -1 or file_path.find("_ro.") != -1):
                print os.path.join(root, name)

def BuildEngine(context, is_mtl=False):
    cur_path = os.getcwd()
    os.chdir(os.path.join(context.packer_path, 'auto_build'))
    if is_mtl:
        cmd = 'python auto_packer_dev.py build_engine -b %s -g %s -p %s -neox %s -proj cn' % (context.build_ver, context.game_path, context.platform, context.noex_path)
    else:
        cmd = 'python auto_packer.py build -type %s -v %s -b %s -t %s -g %s -c %s -p %s -o mainland -neox %s' % (context.build_type, context.cur_ver_num, context.build_ver, context.target_path, context.game_path, context.cache_path, context.platform, context.noex_path)
    RunSysCmd(cmd)
    os.chdir(cur_path)

def Excute():
    # context = InitContext("patch", 'art', 'win', 'trunk')
    context = InitContext("pkg", 'innermicro', 'android', 'trunk')
    BuildEngine(context, True)
    # BuildNpk(context)
    # XXX(context)
    # DoUnipack(context)
    # Test()

Excute()
