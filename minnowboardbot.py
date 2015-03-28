#!/usr/bin/python

import argparse
import commands
import ConfigParser
import datetime
import logging
import os
import psutil
import pygame
import pygame.camera
import random
import sys
import time
import uuid

from apscheduler.scheduler import Scheduler
from apscheduler.threadpool import ThreadPool

from git import Repo
from twython import Twython

def minnowboardBotSetup():
    global twythonid
    twythonid = twythonConfiguration()
    logging.basicConfig(filename='minnowboardbot.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def minnowboardBotExecute(output, media):
    modules = [kernelCompilationMainline, kernelCompilationLinuxNext,
               kernelRepositoryMainline, kernelRepositoryLinuxNext,
               kernelVersion, kernelName, mersennePrime, camera,
               psutilBootTime, psutilCpu, psutilDisks, psutilMemory, psutilNetwork, psutilUsers]
    minnowboardbotmessage = randomize(2) +  ' #MinnowBoard #MinnowBoardBot #Linux '
    status = minnowboardbotmessage + output
    print status
    twythonTimelineSet(twythonid, status, media)

def minnowboardBotScheduler():
    scheduler = Scheduler(misfire_grace_time=3600, coalesce=True, threadpool=ThreadPool(max_threads=1))
    schedule(scheduler)
    scheduler.start()
    scheduler.print_jobs()

def minnowboardBotSchedulerModules(scheduler):
    scheduler.add_interval_job(psUtilExecute, minutes=60)
    scheduler.add_interval_job(kernelExecute, minutes=60)

def minnowboardBotModule(module):
    if module == "psutil":
        psutilExecute()
    elif module == "kernel":
        kernelExecute()
    elif module == "cnext":
        kernelCompilationLinuxNext()
    elif module == "cmainline":
        kernelCompilationMainline()

#===============================================================================
# Twython
#===============================================================================

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
        twythonid.update_status_with_media(media=photo, status=status)
    else:
        twythonid.update_status(status=status)

#===============================================================================
# Miscellaneous
#===============================================================================

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

def camera():
    picturepygame = 'camerapygame.jpg'
    pygame.camera.init()
    mycamera = pygame.camera.Camera("/dev/video0",(1280,720))
    mycamera.start()
    image = mycamera.get_image()
    pygame.image.save(image, picturepygame)
    mycamera.stop()
    return '#Camera #Selfie Hi! This is me, nice to meet you! https://github.com/xe1gyq/minnowboardbot', picturepygame

def randomize(length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace('-',"")
    return random[0:length]

#===============================================================================
# Kernel
#===============================================================================

def kernelPull(branch):
    linuxkernelpath = '/home/xe1gyq/linux'
    repo = Repo(linuxkernelpath)
    git = repo.git
    o = repo.remotes.origin
    git.reset('--hard', 'HEAD')
    print branch
    try:
	git.checkout(branch)
    except:
        pass
    o.pull()
    return linuxkernelpath, repo

def kernelCompilation(linuxkernelpath, repo):
    result = '#LinuxKernel #KernelCompilation ' + repo  +' '
    picturepath = '/home/xe1gyq/picture.png'
    os.chdir(linuxkernelpath)
    status, output = commands.getstatusoutput('git log --pretty --oneline -5 2>&1 | tee -a /tmp/minnowboardbot.gitlog')
    cmdmake = 'make olddefconfig'
    status, output = commands.getstatusoutput(cmdmake)
    cmdmake = 'make -j5 2>&1 | tee -a /tmp/minnowboardbot.output'
    status, output = commands.getstatusoutput(cmdmake)
    print status, output
    if status == 0:
        print 'Ok'
        result = result + 'Ok'
    else:
        print 'Failed'
        result = result + 'Failed'
    result = result + ' ... See Minnowboard @ kernelci.org'
    commands.getstatusoutput('cat /tmp/minnowboardbot.output >> /tmp/minnowboardbot.gitlog')
    picture = 'cat /tmp/minnowboardbot.gitlog | convert -background black -fill white -font Helvetica -pointsize 14 -border 10 -bordercolor black label:@- ' + picturepath
    status, output = commands.getstatusoutput(picture)
    commands.getstatusoutput('rm /tmp/minnowboardbot.*')
    return result, picturepath

def kernelName():
    linuxkernelpath = '/home/xe1gyq/linux'
    os.chdir(linuxkernelpath)
    status, output = commands.getstatusoutput("git tag -l")
    tag = output.splitlines()[-1:]
    datafile = file("/home/xe1gyq/linux/Makefile")
    for line in datafile:
        if "NAME" in line:
            remove, space, result = line.partition(' ')
            remove, space, result = result.partition(' ')
            break
    result = '#LinuxKernel #KernelName ' + str(tag) + ' ' + result
    minnowboardBotExecute(result, None)

def kernelVersion():
    result = '#LinuxKernel #KernelVersion '
    status, output = commands.getstatusoutput("uname -a")
    result = result + output
    result =  result[:-10]
    minnowboardBotExecute(result, None)


def kernelRepositoryMainline():
    result = '#LinuxKernel #Mainline '
    linuxkernelpath, repo = kernelPull('master')
    linuxkernelpath = '/home/xe1gyq/linux'
    picturepath = '/home/xe1gyq/picture.png'
    headcommit = repo.head.commit
    print headcommit
    result = result + 'HEAD commit by ' + headcommit.author.name
    #result = result + ' ' + headcommit.summary
    os.chdir(linuxkernelpath)
    picture = 'git log --pretty -p -1 | convert -background black -fill white -font Helvetica -pointsize 14 -border 10 -bordercolor black label:@- ' + picturepath
    status, output = commands.getstatusoutput(picture)
    minnowboardBotExecute(result, picturepath)

def kernelRepositoryLinuxNext():
    result = '#LinuxKernel #Next '
    linuxkernelpath, repo = kernelPull('akpm')
    linuxkernelpath = '/home/xe1gyq/linux'
    picturepath = '/home/xe1gyq/picture.png'
    headcommit = repo.head.commit
    print headcommit
    result = result + 'HEAD commit by ' + headcommit.author.name
    #result = result + ' ' + headcommit.summary
    os.chdir(linuxkernelpath)
    picture = 'git log --pretty -p -1 | convert -background black -fill white -font Helvetica -pointsize 14 -border 10 -bordercolor black label:@- ' + picturepath
    status, output = commands.getstatusoutput(picture)
    minnowboardBotExecute(result, picturepath)

def kernelCompilationLinuxNext():
    linuxkernelpath, repo = kernelPull("akpm")
    result, picturepath = kernelCompilation(linuxkernelpath, "#LinuxNext")
    minnowboardBotExecute(result, picturepath)

def kernelCompilationMainline():
    linuxkernelpath, repo = kernelPull("master")
    result, picturepath = kernelCompilation(linuxkernelpath, "#Mainline")
    minnowboardBotExecute(result, picturepath)

def kernelExecute():
    modules = [kernelName, kernelVersion,
               kernelRepositoryMainline, kernelRepositoryLinuxNext]
    for module in modules:
        module()
	time.sleep(1)

#===============================================================================
# PSUtil
#===============================================================================

def psutilBootTime():
    output = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    minnowboardBotExecute('#BootTime since ' + output, None)

def psutilCpu():
    output = psutil.cpu_times_percent(interval=1, percpu=False)
    result = '#CpuUtilizationPercentages User ' + "%.1f" % output.user + ' Nice ' + "%.1f" % output.nice
    result = result + ' System ' + "%.1f" % output.system + ' Idle ' + "%.1f" % output.idle
    minnowboardBotExecute(result, None)

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
    minnowboardBotExecute(templ, None)

def psutilMemory():
    # Based on https://github.com/giampaolo/psutil/blob/master/examples/meminfo.py
    result = '#MemoryUsage '
    output = psutil.virtual_memory()
    for name in output._fields:
        value = getattr(output, name)
        if name != 'percent' and name != 'cached' and name != 'inactive' and name != 'buffers':
            value = bytes2human(value)
            result = result + '%s %7s ' % (name.capitalize(), value)
    minnowboardBotExecute(result, None)

def psutilNetwork():
    # Based on https://github.com/giampaolo/psutil/blob/master/examples/nettop.py
    output = psutil.net_io_counters()
    result = "#NetworkStatistics Bytes Tx %s Rx %s" % (bytes2human(output.bytes_sent), bytes2human(output.bytes_recv))
    result = result + " Packets Tx %s Rx %s" % (output.packets_sent, output.packets_recv)
    minnowboardBotExecute(result, None)

def psutilUsers():
    result = '#Users '
    output = psutil.users()
    for user in output:
        result = result + " %s at %s " % (user.name, user.terminal or '-')
    minnowboardBotExecute(result, None)

def psutilExecute():
    modules = [psutilBootTime, psutilCpu, psutilDisks, psutilMemory, psutilNetwork, psutilUsers]
    for module in modules:
        module()
	time.sleep(1)

#===============================================================================
# Cientific Section
#===============================================================================

def mersennePrime():
    datafile = file("/home/xe1gyq/labs/prime.log")
    for line in datafile:
        if "Got" in line:
            result = ''
            remove, space, result = line.partition(' ')
            remove, space, result = result.partition(' ')
    result = "#Mersenne www.mersenne.org " + result
    minnowboardBotExecute(result, None)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='MinnowBoard Bot')
    parser.add_argument('-m', '--modules', help='Module Mode')
    parser.add_argument('-s', '--server', help='Scheduler mode')
    args = parser.parse_args()

    minnowboardBotSetup()

    if args.modules:
        logging.info("Modules")
        minnowboardBotModule(args.modules)

    if args.server == 'scheduler':
        logging.info("Server Mode Scheduler")
        minnowboardBotScheduler()
        while True:
            time.sleep(5)

    if args.server == 'random':
        logging.info("Server Mode Random")
        while True:
            print "To be implemented..."
            time.sleep(5)

# End of File
