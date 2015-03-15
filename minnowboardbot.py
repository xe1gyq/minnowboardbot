#!/usr/bin/python

import commands
import ConfigParser
import datetime
import os
import psutil
import pygame
import pygame.camera
import random
import sys
import uuid

from git import Repo
from twython import Twython

def randomize(length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace('-',"")
    return random[0:length]

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 Kb'
    >>> bytes2human(100001221)
    '95.4 Mb'
    """
    symbols = ('Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s' % (value, s)
    return '%.2f B' % (n)

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
    return result, None

def psutilMemory():
    # Based on https://github.com/giampaolo/psutil/blob/master/examples/meminfo.py
    result = '#MemoryUsage '
    output = psutil.virtual_memory()
    for name in output._fields:
        value = getattr(output, name)
        if name != 'percent' and name != 'cached' and name != 'inactive' and name != 'buffers':
            value = bytes2human(value)
            result = result + '%s %7s ' % (name.capitalize(), value)
    return result, None

def psutilDisks():
    # Based on https://github.com/giampaolo/psutil/blob/master/examples/disk_usage.py
    templ = "#DiskUsage Total %s Used %s Free %s Percent %s%% Filesystem %s Mountpoint %s"
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        if part.mountpoint == '/':
            templ = templ % (
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint)
    return templ, None

def psutilNetwork():
    # Based on https://github.com/giampaolo/psutil/blob/master/examples/nettop.py
    output = psutil.net_io_counters()
    result = "#NetworkStatistics Bytes Tx %s Rx %s" % (bytes2human(output.bytes_sent), bytes2human(output.bytes_recv))
    result = result + " Packets Tx %s Rx %s" % (output.packets_sent, output.packets_recv)
    return result, None

def psutilUsers():
    result = '#Users '
    output = psutil.users()
    for user in output:
        result = result + " %s at %s " % (user.name, user.terminal or '-')
    return result, None

def psutilBootTime():
    output = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    return '#BootTime since ' + output, None

def camera():
    picturepygame = 'camerapygame.jpg'
    pygame.camera.init()
    mycamera = pygame.camera.Camera("/dev/video0",(1280,720))
    mycamera.start()
    image = mycamera.get_image()
    pygame.image.save(image, picturepygame)
    mycamera.stop()
    return '#Camera Hi! This is me, nice to meet you! https://github.com/xe1gyq/minnowboardbot', picturepygame

def kernelVersion():
    result = '#KernelVersion '
    status, output = commands.getstatusoutput("uname -a")
    result = result + output
    return result, None

def kernelPull():
    linuxkernelpath = '/home/xe1gyq/linux'
    repo = Repo(linuxkernelpath)
    o = repo.remotes.origin
    o.pull()
    return linuxkernelpath, repo

def kernelRepository():
    result = '#Mainline '
    linuxkernelpath, repo = kernelPull()
    linuxkernelpath = '/home/xe1gyq/linux'
    picturepath = '/home/xe1gyq/picture.png'
    headcommit = repo.head.commit
    print headcommit
    result = result + 'HEAD commit by ' + headcommit.author.name
    #result = result + ' ' + headcommit.summary
    os.chdir(linuxkernelpath)
    picture = 'git log --pretty --oneline -5 | convert -background black -fill white -font Helvetica -pointsize 14 -border 10 -bordercolor black label:@- ' + picturepath
    status, output = commands.getstatusoutput(picture)
    return result, picturepath

def kernelCompilation():
    result = '#KernelCompilation '
    picturepath = '/home/xe1gyq/picture.png'
    linuxkernelpath, repo = kernelPull()
    os.chdir(linuxkernelpath)
    cmdmake = 'make -j5'
    status, output = commands.getstatusoutput(cmdmake)
    print status, output
    if status == 0:
        print 'Ok'
        result = result + 'Ok'
    else:
        print 'Failed'
        result = result + 'Failed'
    result = result + ' @ kernelci.org'
    picture = cmdmake + ' | convert -background black -fill white -font Helvetica -pointsize 14 -border 10 -bordercolor black label:@- ' + picturepath
    status, output = commands.getstatusoutput(picture)
    return result, picturepath

if __name__ == '__main__':

    twithonid = twythonConfiguration()

    modules = [camera, kernelCompilation, kernelRepository, kernelVersion,
               psutilBootTime, psutilCpu, psutilDisks, psutilMemory, psutilNetwork, psutilUsers]
    output, media = random.choice(modules)()
    minnowboardbot = randomize(2) +  ' #MinnowBoard #MinnowBoardBot #Linux '
    status = minnowboardbot + output

    twythonTimelineSet(twithonid, status, media)

# End of File
