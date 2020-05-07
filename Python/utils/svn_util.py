# -*- coding: utf-8 -*-

import os

# 获取当前版本库本地修改的文件
def getChangedFiles(dir_path):
    cur_dir = os.getcwd()
    os.chdir(dir_path)
    cmd = 'svn status'
    data = os.popen(cmd)
    result = []
    for line in data.readlines():
        line = line.strip()
        if not line.endswith('.py'):
            continue
        info_list = line.split(' ')
        result.append((info_list[0], os.path.join(dir_path, info_list[-1])))
    os.chdir(cur_dir)
    return result

# 会获取版本库里面版本比较高的文件，就算本地还没有更新
def getNewerFiles(dir_path, svn_version):
    cur_dir = os.getcwd()
    os.chdir(dir_path)
    cmd = 'svn diff -r %s:HEAD --summarize' % svn_version
    data = os.popen(cmd)
    result = []
    for line in data.readlines():
        line = line.strip()
        print line
        if not line.endswith('.py'):
            continue
        info_list = line.split(' ')
        result.append((info_list[0], os.path.join(dir_path, info_list[-1])))
    os.chdir(cur_dir)
    return result

# 获取某个路径的svn info信息
def getInfo(dir_path):
    cmd = 'svn info %s' % dir_path
    data = os.popen(cmd)
    info_dict = dict()
    for line in data.readlines():
        line = line.strip()
        if not line:
            continue
        info_list = line.split(':', 1)
        info_dict[info_list[0].strip()] = info_list[1].strip()
    return info_dict

# 获取某个路径的倒数第N个svn log信息
def getNthLogInfo(dir_path, n):
    cmd = 'svn log -l %s %s' % (n, dir_path)
    data = os.popen(cmd)
    info_dict = dict()
    for line in data.readlines():
        line = line.strip()
        if not line or not line.startswith('r'):
            continue
        info_list = line.split('|')
        info_dict['Revision'] = info_list[0].strip()[1:]
        info_dict['Last Changed Date'] = info_list[2].strip()
    return info_dict


game_path = 'E:\\g78\\trunk\\client\\game'
script_npk_path = os.path.join(game_path, 'script.npk')
getNthLogInfo(script_npk_path, 2)
# packer_path = os.path.join(os.path.dirname(game_path), 'packer')
# script_path = os.path.join(game_path, 'script')
# for i in xrange(10):
#     getInfo(os.path.join(game_path, 'script.npk'))