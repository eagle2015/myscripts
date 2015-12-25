#!/bin/bash
checkchar()
{
    if [ -z $char  ];then
        echo "放弃同步.(您没有输入)"
        exit 0;
    fi

    if [ $char = $projectname ];then
       echo "执行同步(您输入的是：\"$char\")"
       myrsync
    else
        echo "放弃同步(您输入的是：\"$char\")"
        exit 0;
    fi
}

myrsync()
{
    /usr/bin/rsync -vzrtopg --progress --delete --exclude-from=/home/svn/www.xxxname.com/exclude.list --password-file=/home/gbecuser/bin/rsync.passwd /home/wwwroot/www.xxxname.com/ webuser@10.41.119.247::xxxnameweb --log-format=%f >>/home/gbecuser/bin/logs/xxxname/rsync_247_${dateTime}_${dateTimeMinute}.txt 2>&1
    checkresult


    /usr/bin/rsync -vzrtopg --delete --progress -e ssh --exclude-from=/home/svn/www.xxxname.com/exclude.list /home/wwwroot/www.xxxname.com/ gbecuser@10.60.40.236:/home/wwwroot/www.xxxname.com/  --log-format=%f >>/home/gbecuser/bin/logs/xxxname/rsync_236_${dateTime}_${dateTimeMinute}.txt 2>&1
    checkresult
}

checkresult()
{
    if [ $? -eq 0 ];then
        echo "同步成功"
    else
        echo "同步异常"
    fi
}

dateTime=`date +%F`
dateTimeMinute=`date +%H%M%S`
projectname="xxxname"

read -p "您真的要同步$projectname到线上和备份机器吗!(请输入\"$projectname\"确认)" char
checkchar
