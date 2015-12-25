#!/usr/local/python2.7.10/bin/python
# coding=utf8

import sys
import os
import datetime
import logging
import time
from multiprocessing.dummy import Pool as ThreadPool

SVN_BIN = "/usr/local/subversion/bin/"
SVN_PATH = "/var/lib/svn/repos/"
SYNC_PATH = "/data/svnback3_3/svn2/svnsync/repos/"
SVN_CO_ROOT_PATH = "http://127.0.0.1/svn/repos/"
DATETIME = (datetime.datetime.now()).strftime('%Y%m%d-%H%M%S')
LOG_PATH = "/data/svn2/svnsync/logs/"
LOG_FILE_NAME = "svnsync.log"
SVN_ADMIN_USER = "svnuser"
SVN_ADMIN_PASSWORD = "svnpassword"

# 主函数


def Main():
    start = time.time()
    logs(
        "-----------------------------日志开始---------------------------------------")
# 检查需要备份的svn仓库根目录是否存在，不存在则退出
    if os.path.exists(SVN_PATH) is False:
        logs(SVN_PATH + "目录不存在")
        logs(
            "-----------------------------日志结束---------------------------------------")
        sys.exit()

# 遍历出svn仓库目录下有多少个文件夹，并确定出那些是svn具体的项目目录
    sourcesvndirs, nosourcesvndirs = dirIsSvnProject(
        listDirs(SVN_PATH), SVN_PATH)
    logs("如下：共有" + str(len(sourcesvndirs)) + "个需要备份的svn项目")
    map(logs, sourcesvndirs)
    logs("---------------------------------------")

# 启用多线程执行svnsync
    pool = ThreadPool()

# 确定后开始准备备份（大概有2种其可能情况，一：备份的项目已经创建，已经创建一般情况我们认同已经初始化过，只需要同步即可(但是要判断是否是源svn项目中的项目，这里只判断名字相同即可) 二：对应的备份项目还未创建，需要创建并初始化，然后再同步)，
# 一：备份的项目已经创建，已经创建一般情况我们认同已经初始化过，只需要同步即可(但是要判断是否是源svn项目中的项目，这里只判断名字相同即可)
    mkDir(SYNC_PATH)
    backsvndirs, nobacksvndirs = dirIsSvnProject(
        listDirs(SYNC_PATH), SYNC_PATH)
    # 如果备份的svn目录 源svn里面已经删除了，这里也要判断下 执行对应的同步
    sync_dirs = []
    for backsvndir in backsvndirs:
        if backsvndir in sourcesvndirs:
            sync_dirs.append(backsvndir)

    if len(sync_dirs) > 0:
        logs("如下：共有" + str(len(sync_dirs)) + "个目录已经初始化，现在只需要同步")
        map(logs, sync_dirs)

    logs("---------------------------------------")
    pool.map(svnSync, sync_dirs)
    logs("---------------------------------------")


# 二：求出2个列表的差，备份项目还未创建，需要创建并初始化，然后再同步)，
    needcreatesvns = list(set(sourcesvndirs) ^ set(sync_dirs))
    if len(needcreatesvns) > 0:
        logs("如下：共有" + str(len(needcreatesvns)) + "个目录需要初始化，然后再同步")
        map(logs, needcreatesvns)
    # 需要创建备份的项目，并初始化，然后同步
    logs("---------------------------------------")
    pool.map(createInitSync, needcreatesvns)
    logs("---------------------------------------")

    pool.close()
    pool.join()
# 统计程序执行时间
    elapsed = time.time() - start
    if elapsed >= 60:
        el = "%0.2f 分钟" % float(elapsed / 60)
    else:
        el = "%0.2f 秒" % float(time.time() - start)
    logs("本程序此次执行时间为：" + el)
    logs(
        "-----------------------------日志结束---------------------------------------")

# 调用函数

# 创建目录（mkdir -p） 没有返回值


def mkDir(path):
    mkdir = os.system('/bin/mkdir' + ' ' + '-p' + ' ' + path)

# 记录调用system执行系统命令是否成功，写入日志


def ifSystem(checkname, message1, message2):
    if checkname == 0:
        logs(message1)
    elif checkname == 1:
        logs(message1)
    else:
        logs(message2)

# 列出文件夹下的目录名:返回给定路径下的目录名


def listDirs(path):
    filenames = os.listdir(path)
    dirs = []
    for dir in filenames:
        if os.path.isdir(path + dir) is True:
            dirs.append(dir)
    return dirs

# 检查是否是svn项目:返回给定目录下的正常的svn项目目录名(列表)


def dirIsSvnProject(dirs, svnpath):
    svndirs = []
    nosvndirs = []
    for dir in dirs:
        svnlook = os.system(SVN_BIN + 'svnlook youngest' + ' ' + svnpath + dir)
        if svnlook == 0:
            svndirs.append(dir)
        elif svnlook == 1:
            svndirs.append(dir)
        else:
            nosvndirs.append(dir)
    return svndirs, nosvndirs

# 检查备份


def checkBak(svndir):
    checkbak = os.system(
        SVN_BIN + 'svnlook youngest' + ' ' + SYNC_PATH + '/' + svndir)
    m1 = svndir + ":同步后，经youngest检查正常"
    m2 = svndir + ":同步后，经youngest检查不正常"
    ifSystem(checkbak, m1, m2)

# 创建pre-revprop-change文件


def createHooksFile(svnproject):
    PRE_REVPROP_CHANGE_FILE = SYNC_PATH + \
        svnproject + '/hooks/pre-revprop-change'
    mkDir(SYNC_PATH + svnproject + '/hooks')
    try:
        with open(PRE_REVPROP_CHANGE_FILE, 'w') as f:
            f.write("#!/bin/sh \n exit 0")
            f.close()
            logs(PRE_REVPROP_CHANGE_FILE + "创建成功")
    except IOError as err:
        logs("写入" + PRE_REVPROP_CHANGE_FILE + "错误：" + str(err))
    os.system('/bin/chmod ' + '+x ' + PRE_REVPROP_CHANGE_FILE)

# 创建svn项目


def createSvn(svnproject):
    createsvn = os.system(
        SVN_BIN + 'svnadmin create' + ' ' + SYNC_PATH + svnproject)
    m1 = svnproject + "：createsvn创建正常"
    m2 = svnproject + "：createsvn创建异常!!!!!!!!!!!!!"
    ifSystem(createsvn, m1, m2)

# 初始化项目,如svnsync init file:///home/backup/svn/svnsync/Project1/  http://svntest.subversion.com/repos/Project1


def svnSyncInit(svnproject):
    svnsyncinit = os.system(SVN_BIN + 'svnsync init file://' + SYNC_PATH + svnproject + ' ' + SVN_CO_ROOT_PATH +
                            svnproject + ' --no-auth-cache --username ' + SVN_ADMIN_USER + ' --password ' + SVN_ADMIN_PASSWORD)
    m1 = svnproject + "：svnSyncInit初始化正常"
    m2 = svnproject + "：svnSyncInit初始化异常!!!!!!!!!!!!!"
    ifSystem(svnsyncinit, m1, m2)

# 同步项目，如。svnsync sync  --non-interactive file:///data/svnbak/test


def svnSync(svnproject):
    svnsync = os.system(SVN_BIN + 'svnsync sync  --non-interactive file://' + SYNC_PATH +
                        svnproject + ' --no-auth-cache --username ' + SVN_ADMIN_USER + ' --password ' + SVN_ADMIN_PASSWORD)
    m1 = svnproject + "：svnSync同步正常"
    m2 = svnproject + "：svnSync同步异常！！！！！！"
    ifSystem(svnsync, m1, m2)
    checkBak(svnproject)


def createInitSync(svnproject):
    createSvn(svnproject)
    createHooksFile(svnproject)
    svnSyncInit(svnproject)
    svnSync(svnproject)


def logs(message):
    mkDir(LOG_PATH)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=LOG_PATH + LOG_FILE_NAME,
                        filemode='a')
    return logging.info(message)

if __name__ == '__main__':
    Main()
