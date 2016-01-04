###我的相关脚本

####1:thearding_queue.py
*该脚本可用来统计大量不同url的返回状态，如果不是200就记录到文件中.url是从csv文件中取出并放入query队列中,然后启用多线程并发执行检测,csv文件主要是由url对应的编号+url后缀.

####2:myrsync.sh  
* 线上同步脚本

####3:svnhotcopy.py  svnsync.py
* svn备份脚本
* svnhotcopy.py  svnhotcopy方式完整备份
* svnsync.py     svnsync 同步差异备份
####4:myhistory.sh
* 记录history命令到文件记录(可以通过elk日志系统收集),收集结果如下：
```BASH
[root@ryan ryan]# cat /var/log/history.log 
Jan  4 16:30:03 ryan bash[19452]: user=root, login=root, from=192.168.2.159, pwd=/root, command="ls"
Jan  4 16:30:07 ryan bash[19465]: user=root, login=root, from=192.168.2.159, pwd=/root, command="cat /var/log/history.log "
Jan  4 16:30:12 ryan bash[19478]: user=root, login=root, from=192.168.2.159, pwd=/root, command="pwd"
Jan  4 16:30:13 ryan bash[19490]: user=root, login=root, from=192.168.2.159, pwd=/, command="cd /"
Jan  4 16:30:19 ryan bash[19526]: user=root, login=root, from=192.168.2.159, pwd=/home/ryan, command="cd /home/ryan"
```
