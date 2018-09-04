#!/bin/sh
cd /data/crawler_system/projects/di/amazon_track
program=data_insert.py

sn=`ps -ef | grep $program | grep -v grep |awk '{print $2}'`
if ["${sn}" = ""]
then
/usr/bin/python3.6 data_insert.py 2> data_insert.log 
echo start ok !
fi
