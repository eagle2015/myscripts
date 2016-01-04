createhistory()
{

/bin/touch /etc/profile.d/history.sh
(
cat <<EOF
HISTSIZE=1000
HISTTIMEFORMAT=""
#HISTTIMEFORMAT="%Y-%m-%d %T - "
PROMPT_COMMAND='
{
    id=\$(history 1 |sed -r "s/^\s+([0-9]+).*/\1/");
    comm=\$(history 1 |sed -r "s/\s+[0-9]+\s+//");
    host=\$(who am i -u | sed -r "s/.*\((.*)\)/\1/");
    if [ "\$id" != "\$lastid" -a ! -z "\$lastid" ]; then
        logger -p local2.debug -t bash -i "user=\$(whoami), login=\$USER, from=\$host, pwd=\$PWD, command=\"\$comm\"";
    fi;
    lastid=\$id;
}'

bind '"\e[A":history-search-backward'
bind '"\e[B":history-search-forward'

export HISTTIMEFORMAT
export PROMPT_COMMAND
EOF
)>>/etc/profile.d/history.sh

}



createlog()
{
	if [ -f /etc/syslog.conf ];then
		r=`grep local2.debug /etc/syslog.conf | wc -l`
		if [ $r -eq 0 ]; then
			echo "local2.debug         /var/log/history.log"  >> /etc/syslog.conf
			/etc/init.d/syslog restart
		else
			echo "local2.debug exits"
		fi

	fi


	if [ -f /etc/rsyslog.conf ];then
		r2=`grep local2.debug /etc/rsyslog.conf | wc -l`
		if [ $r2 -eq 0 ]; then
			echo "local2.debug         /var/log/history.log"  >> /etc/rsyslog.conf
			/etc/init.d/rsyslog restart
		else
			echo "local2.debug exits"
		fi

	fi

}




mymain()
{
    if [ -f /etc/profile.d/history.sh ];then
        source /etc/profile.d/history.sh
        echo "history.sh exits"
    else
        createhistory
        createlog
        source /etc/profile.d/history.sh
    fi

}

mymain
