#! /usr/bin/python3

from tokens import *
import matplotlib
matplotlib.use("Agg") # has to be before any other matplotlibs imports to set a "headless" backend
import matplotlib.pyplot as plt
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator
import collections
# import sys
import time
# import threading
# import random
import telepot
# from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
# from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
# from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent



memorythreshold = 85  # If memory usage more this %
cputhreshold = 85  # if total cpu usage more than this
poll = 30  # seconds

shellexecution = []
timelist = []
memlist = []
xaxis = []
settingmemth = []
setpolling = []
graphstart = datetime.now()

stopmarkup = {'keyboard': [['Stop']]}
hide_keyboard = {'hide_keyboard': True}

def clearall(chat_id):
    if chat_id in shellexecution:
        shellexecution.remove(chat_id)
    if chat_id in settingmemth:
        settingmemth.remove(chat_id)
    if chat_id in setpolling:
        setpolling.remove(chat_id)

def plotmemgraph(memlist, xaxis, tmperiod):
    # print(memlist)
    # print(xaxis)
    plt.xlabel(tmperiod)
    plt.ylabel('% Used')
    plt.title('Memory Usage Graph')
    plt.text(0.1*len(xaxis), memorythreshold+2, 'Threshold: '+str(memorythreshold)+ ' %')
    memthresholdarr = []
    for xas in xaxis:
        memthresholdarr.append(memorythreshold)
    plt.plot(xaxis, memlist, 'b-', xaxis, memthresholdarr, 'r--')
    plt.axis([0, len(xaxis)-1, 0, 100])
    plt.savefig('/tmp/graph.png')
    plt.close()
    f = open('/tmp/graph.png', 'rb')  # some file on local disk
    return f

class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Do your stuff according to `content_type` ...
        print("Your chat_id:" + str(chat_id)) # this will tell you your chat_id
        if chat_id in adminchatid:  # Store adminchatid variable in tokens.py
            if content_type == 'text':
                if msg['text'] == '/help' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    reply = "/stats - gives summed statistics about memory \\ disk \\ processes (will improve)\n" + \
                            "/shell - goes into the mode of executing shell commands & sends you the output\n" + \
                            "/memgraph - plots a graph of memory usage for a past period and sends you a picture of the graph\n" + \
                            "/setmem - set memory threshold (%) to monitor and notify if memory usage goes above it\n" + \
                            "/setpoll - set polling interval in seconds (higher than 10)\n"
                    bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                if msg['text'] == '/stats' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    # time
                    boottime = datetime.fromtimestamp(psutil.boot_time())
                    now = datetime.now()
                    timedif = "Uptime: %.1f Hours" % (((now - boottime).total_seconds()) / 3600)
                    # memory
                    memory = psutil.virtual_memory()
                    memtotal = "%.2f" % (memory.total / 1024 / 1024 / 1024)
                    #memavail = "%.2f" % (memory.available / 1024 / 1024 / 1024)
                    memused = "%.2f" % (memory.used / 1024 / 1024 / 1024)
                    memuseperc = "(" + str(memory.percent) + " %)"
                    mem = "Memory: " + memused + "/" + memtotal + " GiB " + memuseperc
                    # disk
                    diskparts = psutil.disk_partitions()
                    diskusage = "Disk usage per mount:\n"
                    for part in diskparts:
                        mount = part.mountpoint
                        usage = psutil.disk_usage(mount)
                        usagetotal = "%.2f" % (usage.total / 1024 / 1024 / 1024)
                        #usagefree = "%.2f" % (usage.free / 1024 / 1024 / 1024)
                        usageused = "%.2f" % (usage.used / 1024 / 1024 / 1024)
                        usageperc = "(" + str(usage.percent) + " %)"
                        diskusage += mount + " " + usageused + "/" + usagetotal + " GiB " + usageperc + "\n"
                    # cpu
                    cpuperc = psutil.cpu_percent(percpu=True)
                    cpuusage = "CPU Usage:\n"
                    cpuid = 0
                    for cpu in cpuperc:
                        cpuusage += "CPU" + str(cpuid) + ": " + str(cpu) + " %\n"
                        cpuid += 1
                    cpuusage += "CPU Total: " + str(psutil.cpu_percent()) + " %"
                    # output
                    reply = timedif + "\n" + \
                            "---\n" + \
                            cpuusage + "\n" + \
                            "---\n" + \
                            mem + "\n" + \
                            "---\n" + \
                            diskusage + "\n"
                    bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                elif msg['text'] == "Stop":
                    clearall(chat_id)
                    bot.sendMessage(chat_id, "All operations stopped.", reply_markup=hide_keyboard)
                elif msg['text'] == '/setpoll' and chat_id not in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    setpolling.append(chat_id)
                    bot.sendMessage(chat_id, "Send me a new polling interval in seconds? (higher than 10)", reply_markup=stopmarkup)
                elif chat_id in setpolling:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global poll
                        poll = int(msg['text'])
                        if poll > 10:
                            bot.sendMessage(chat_id, "All set!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Please send a proper numeric value higher than 10.")
                elif msg['text'] == "/shell" and chat_id not in shellexecution:
                    bot.sendMessage(chat_id, "Send me a shell command to execute", reply_markup=stopmarkup)
                    shellexecution.append(chat_id)
                elif msg['text'] == "/setmem" and chat_id not in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    settingmemth.append(chat_id)
                    bot.sendMessage(chat_id, "Send me a new memory threshold to monitor?", reply_markup=stopmarkup)
                elif chat_id in settingmemth:
                    bot.sendChatAction(chat_id, 'typing')
                    try:
                        global memorythreshold
                        memorythreshold = int(msg['text'])
                        if memorythreshold < 100:
                            bot.sendMessage(chat_id, "All set!")
                            clearall(chat_id)
                        else:
                            1/0
                    except:
                        bot.sendMessage(chat_id, "Please send a proper numeric value below 100.")

                elif chat_id in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, disable_web_page_preview=True)
                    else:
                        bot.sendMessage(chat_id, "No output.", disable_web_page_preview=True)
                elif msg['text'] == '/memgraph':
                    bot.sendChatAction(chat_id, 'typing')
                    tmperiod = "Last %.2f hours" % ((datetime.now() - graphstart).total_seconds() / 3600)
                    bot.sendPhoto(chat_id, plotmemgraph(memlist, xaxis, tmperiod))



TOKEN = telegrambot

bot = YourBot(TOKEN)
bot.message_loop()
tr = 0
xx = 0
# Keep the program running.
while 1:
    if tr == poll:
        tr = 0
        timenow = datetime.now()
        memck = psutil.virtual_memory()
        mempercent = memck.percent
        cpupercent = psutil.cpu_percent()
        if len(memlist) > 300:
            memq = collections.deque(memlist)
            memq.append(mempercent)
            memq.popleft()
            memlist = memq
            memlist = list(memlist)
        else:
            xaxis.append(xx)
            xx += 1
            memlist.append(mempercent)
        memfree = (memck.available / 1024 / 1024 / 1024)
        if mempercent > memorythreshold:
            memavail = "Available memory: %.2f GiB" % (memck.available / 1024 / 1024 / 1024)
            graphend = datetime.now()
            tmperiod = "Last %.2f hours" % ((graphend - graphstart).total_seconds() / 3600)
            for adminid in adminchatid:
                bot.sendMessage(adminid, "CRITICAL! LOW MEMORY!\n" + memavail)
                bot.sendPhoto(adminid, plotmemgraph(memlist, xaxis, tmperiod))
        if cpupercent > cputhreshold:
            for adminid in adminchatid:
                bot.sendMessage(adminid, "CRITICAL! HIGH CPU!\n" + str(cpupercent) + " %")
    time.sleep(10)  # 10 seconds
    tr += 10
