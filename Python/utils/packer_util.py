#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import os
import sys

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

def BuildEngine(context):
    cur_path = os.getcwd()
    os.chdir(os.path.join(context.packer_path, 'auto_build'))
    cmd = 'python auto_packer.py build -type %s -v %s -b %s -t %s -g %s -c %s -p %s -o mainland -neox %s' % (context.build_type, context.cur_ver_num, context.build_ver, context.target_path, context.game_path, context.cache_path, context.platform, context.noex_path)
    RunSysCmd(cmd)
    os.chdir(cur_path)

def DoUnipack(context):
    import project_config

    apk_name = 'mother_g78_%s.apk' % context.cur_ver_num
    apk_path = os.path.join(context.cur_target_path, apk_name)
    apk_abs_path = os.path.abspath(apk_path)
    target_abs_path = os.path.abspath(context.cur_target_path)
    cmd = "%s -i %s -o %s -g %s -ac %s -u %s -p %s" % ("UniPack_cmd_v4.0.exe", apk_abs_path, target_abs_path, 'g78', 
    "nearme_vivo_2:netease_codescanner_2,ngshare_8,ngpush,amap_location,gmbridge_2", project_config.UNIPACK_USER, project_config.UNIPACK_CMD_KEY)
    cur_path = os.getcwd()
    unipack_path = os.path.join(context.packer_path, 'android', 'autobuild', 'unipack')
    os.chdir(unipack_path)
    os.system(cmd)
    os.chdir(cur_path)

def InitContext(build_type, build_ver, platform, engine_type):
    context = Context()
    context.build_ver = build_ver
    context.build_type = build_type
    context.platform = platform

    context.target_path = 'E:\\g78\\build_target\\%s' % engine_type
    context.cur_target_path = os.path.join(context.target_path, build_ver, platform)
    context.packer_path = 'E:\\g78\\packer'
    
    sys.path.append(os.path.join(context.packer_path, 'auto_build'))
    sys.path.append(os.path.join(context.packer_path, 'auto_build', 'libs'))

    context.game_path = 'E:\\g78\\trunk2\\client\\game'

    context.cur_ver_num = '1.59.1'

    context.noex_path = NEOX_DIR_MAPPING[engine_type]
    context.cache_path = 'E:\\g78\\build_target\\res_cache'
    return context

def Test():
    for root, dirs, names in os.walk("E:\\g78\\trunk2\\client\\game\\res\\scene"):
        for name in names:
            file_path = os.path.join(root, name)
            if file_path.find("scene") != -1 and (file_path.find("_r.") != -1 or file_path.find("_ro.") != -1):
                print os.path.join(root, name)

def Excute():
    context = InitContext("pkg", 'innermicro', 'android', 'trunk')
    BuildEngine(context)
    # DoUnipack(context)
    # Test()

Excute()
