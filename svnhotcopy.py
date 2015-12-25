#!/usr/local/python2.7.10/bin/python
# coding=utf8

import sys
import os
import datetime
import logging
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

DATETIME = (datetime.datetime.now()).strftime('%Y%m%d')
MYSQL_BIN = "/usr/local/ver01/mysql/bin/"
SVN_BIN = "/usr/local/subversion/bin/"
SVN_PATH = "/var/lib/svn/repos/"
ACCESS_FILE = "/var/lib/svn/accessfile"
PASSWD_FILE = "/var/lib/svn/passwdfile"
SVN_CONFIG = "/var/lib/svn/svnconfig/"

BAKDIR = "/data/svnback3_3/svn2/hotcopy/"
BAKDIR_TAR = BAKDIR + "tar/"
PASSWD_AUTHZ_BACKDIR = BAKDIR + DATETIME + "/passwdauthzbak/"
REPOS_BAKDIR = BAKDIR + DATETIME + "/reposbak/"
MYSQL_BACK_PATH = BAKDIR + DATETIME + "/mysqlbak/"

LOG_PATH = "/home/ryan/svn2/svnhotcopy/logs/"
LOG_FILE_NAME = "svnhotcopy.log"
MYSQL_USER = "svnmanager"
MYSQL_PASSWORD = "svnmanager"
DATABASE_NAME = "svnmanager"


def Main():
    start = time.time()
# SVN仓库目录是否存在，不存在退出备份脚本
    logs(
        "-----------------------------日志开始---------------------------------------")
    if os.path.exists(BAKDIR_TAR + DATETIME + '.tar.gz') is True:
        logs(BAKDIR_TAR + DATETIME + '.tar.gz' + "备份已经存在，不需要重复备份")
        logs(
            "-----------------------------日志结束---------------------------------------")
        sys.exit()

    if os.path.exists(SVN_PATH) is False:
        logs(SVN_PATH + "目录不存在")
        logs(
            "-----------------------------日志结束---------------------------------------")
        sys.exit()

# 遍历出所有SVN仓库目录
    svndirs, nosvndirs = dirIsSvnProject(listDirs(SVN_PATH))
    logs("如下：共有" + str(len(svndirs)) + "个需要备份的svn项目")
    map(logs, svndirs)
    if len(nosvndirs) > 0:
        logs("如下：共有" + str(len(nosvndirs)) + "个目录经svnlook检查异常，或者原本就不是svn项目")
        map(logs, nosvndirs)
    logs("---------------------------------------")

# 备份svnrepos
    mkDir(REPOS_BAKDIR)
# 启用多线程执行hostcopy
    pool = ThreadPool()
    pool.map(hostCopy2, svndirs)
    pool.close()
    pool.join()
    logs("---------------------------------------")

# 备份passwd和authz文件
    mkDir(PASSWD_AUTHZ_BACKDIR)
    cpBak(ACCESS_FILE)
    cpBak(PASSWD_FILE)
    cpBak(SVN_CONFIG)

# mysqldump 备份
    mkDir(MYSQL_BACK_PATH)
    mysqlDump()
    logs("---------------------------------------")

# 打包备份
    mkDir(BAKDIR_TAR)
    tarBak()

# 程序执行时间
    elapsed = (time.time() - start)
    if elapsed >= 60:
        el = "%0.2f 分钟" % float(elapsed / 60)
    else:
        el = "%0.2f 秒" % float(time.time() - start)
    logs("此次备份共花时间：" + el)
    logs(
        "-----------------------------日志结束---------------------------------------")
# 调用的相关函数
# 记录调用system执行系统命令是否成功，写入日志


def ifSystem(checkname, message1, message2):
    if checkname == 0:
        logs(message1)
    elif checkname == 1:
        logs(message1)
    else:
        logs(message2)


def mysqlDump():
    mysqldump = os.system(MYSQL_BIN + 'mysqldump' + ' -u' + MYSQL_USER + ' -p' + MYSQL_PASSWORD +
                          ' ' + DATABASE_NAME + ' > ' + MYSQL_BACK_PATH + '/' + DATABASE_NAME + '.sql')
    m1 = "数据库" + DATABASE_NAME + "已备份OK"
    m2 = "数据库" + DATABASE_NAME + "备份异常"
    ifSystem(mysqldump, m1, m2)


def cpBak(file):
    m1 = file + "已备份"
    m2 = file + "备份异常"
    if os.path.exists(file) is True:
        cpbak = os.system('/bin/cp -rf ' + file + ' ' + PASSWD_AUTHZ_BACKDIR)
        ifSystem(cpbak, m1, m2)
    else:
        logs(file + "文件不存在")

# 备份并调用检查备份函数


def hostCopy2(svndir):
    m1 = "备份" + svndir + "完成"
    m2 = "备份" + svndir + "异常---------------------"
    hotcopy = os.system(SVN_BIN + 'svnadmin hotcopy --clean-logs' +
                        ' ' + SVN_PATH + svndir + ' ' + REPOS_BAKDIR + '/' + svndir)
    ifSystem(hotcopy, m1, m2)
    checkbak = checkBak2(svndir)
    # return hotcopy,checkbak

# 检查备份


def checkBak2(svndir):
    checkbak = os.system(
        SVN_BIN + 'svnlook youngest' + ' ' + REPOS_BAKDIR + '/' + svndir)
    m1 = "检查" + svndir + "备份项目正常"
    m2 = "检查" + svndir + "备份项目异常---------------------"
    ifSystem(checkbak, m1, m2)

# 打包目录，并删除源目录


def tarBak():
    bakname = BAKDIR_TAR + DATETIME + '.tar.gz'
    needbakdir = BAKDIR + DATETIME
    tarbak_m1 = bakname + "备份打包完成,并删除源文件"
    tarbak_m2 = bakname + "备份打包异常"
    if os.path.exists(bakname) is False:
        tarbak = os.system(
            '/bin/tar' + ' ' + 'zcfP' + ' ' + bakname + ' ' + needbakdir + ' --remove-files')
        ifSystem(tarbak, tarbak_m1, tarbak_m2)
        os.system('/bin/rm' + ' ' + '-Rf' + ' ' + needbakdir)
    else:
        logs(bakname + "这个已经备份过了")

# 创建目录（mkdir -p） 没有返回值一般不会异常，此处不判断


def mkDir(path):
    mkdir = os.system('/bin/mkdir' + ' ' + '-p' + ' ' + path)

# 列出文件夹下的目录名:返回给定路径下的目录名


def listDirs(path):
    filenames = os.listdir(path)
    dirs = []
    for dir in filenames:
        if os.path.isdir(path + dir) is True:
            dirs.append(dir)
    return dirs

# 检查是否是svn项目:返回给定目录下的正常的svn项目目录名(列表)


def dirIsSvnProject(dirs):
    svndirs = []
    nosvndirs = []
    for dir in dirs:
        svnlook = os.system(
            SVN_BIN + 'svnlook youngest' + ' ' + SVN_PATH + dir)
        if svnlook == 0:
            svndirs.append(dir)
        elif svnlook == 1:
            svndirs.append(dir)
        else:
            nosvndirs.append(dir)
    return svndirs, nosvndirs

# 日志


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
