#!/usr/bin/env python
# coding=utf8

import csv
import requests
import threading
import Queue

projectname = "test"
URL_PREFIXURL = "http://www.xxx.com/"
CSVFILE = "%s.csv" % projectname
LOGS = "%s_not200.csv" % projectname
KONG = "%s_kong.csv" % projectname
threads = 400


def build_url_queue(csvfile):
    with open(csvfile, 'rb') as myFile:
        lines = csv.reader(myFile)
        urls = Queue.Queue()
        for line in lines:
            sku = line[0]
            try:
                file_path = line[1]
            except IndexError:
                file_path = ""
            qline = sku+ ','+file_path
            urls.put(qline)

    return urls


def get_notfound(url_queue):
    while not url_queue.empty():
        attempt = url_queue.get()
        attempt_list = []
        attempt_list.append(attempt)

        for line in attempt_list:
            rlist = line.split(',')
            sku = rlist[0]
            try:
                file_path = rlist[1]
            except IndexError:
                file_path = ""
            if file_path == "":
                setLog(sku,KONG)
            status_code = requests.head(URL_PREFIXURL + file_path).status_code
            rline = sku+ ','+file_path+','+str(status_code)
            print rline
            if status_code != 200:
                setLog(rline,LOGS)


def setLog(msg,filename):
    with open(filename, 'a') as myFile:
        myFile.write(msg + '\n')


if __name__ == '__main__':
    url_queue = build_url_queue(CSVFILE)
    for i in range(threads):
        t = threading.Thread(target=get_notfound, args=(url_queue,))
        t.start()
