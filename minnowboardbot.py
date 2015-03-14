#!/usr/bin/python

import ConfigParser
import datetime
import psutil
import random

from twython import Twython

def twythonConfiguration():
    configuration = ConfigParser.ConfigParser()
    configuration.read('twitter.config')
    consumer_key = configuration.get('twitter','consumer_key')
    consumer_secret = configuration.get('twitter','consumer_secret')
    access_token = configuration.get('twitter','access_token')
    access_token_secret = configuration.get('twitter','access_token_secret')
    twythonid = Twython(consumer_key,consumer_secret,access_token,access_token_secret)
    return twythonid

def twythonTimelineSet(twitterid, status, media):
    if media:
        photo = open(media,'rb')
        twithonid.update_status_with_media(media=photo, status=status)
    else:
        twithonid.update_status(status=status)

def psutilCpu():
    output = psutil.cpu_times_percent(interval=1, percpu=False)
    result = '#CpuUtilizationPercentages User ' + "%.1f" % output.user + ' Nice ' + "%.1f" % output.nice
    result = result + ' System ' + "%.1f" % output.system + ' Idle ' + "%.1f" % output.idle
    return result

def psutilMemory():
    output = psutil.virtual_memory()

def psutilDisks():
    return psutil.disk_partitions()

def psutilNetwork():
    return psutil.net_io_counters(pernic=True)

def psutilUsers():
    return psutil.users()

def psutilBootTime():
    output = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    return '#BootTime since ' + output

if __name__ == '__main__':

    twithonid = twythonConfiguration()

    modules = [psutilCpu, psutilMemory, psutilDisks, psutilNetwork, psutilUsers, psutilBootTime]
    modules = [psutilCpu, psutilBootTime]
    output = random.choice(modules)()
    minnowboardbot = '#MinnowBoard '
    status = minnowboardbot + output

    twythonTimelineSet(twithonid, status, media=None)

# End of File
