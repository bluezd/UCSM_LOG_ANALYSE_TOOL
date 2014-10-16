#!/usr/bin/python

import re
import pygtk
pygtk.require('2.0')
import gtk

pattern = re.compile('`show system firmware expand`')
pattern1 = re.compile('`.*`')
pattern2 = re.compile('^`scope .*`')
f = open("sam_techsupportinfo", "r")
#f = open("log-test", "r")

SCOPE = 0 
SCOPE_ING = False
SCOPE_END_PREV = False
SCOPE_NEST = False
content = list()
com_content = dict()
prev_com = ""
First_SCOPE = False
dup_com = dict()
dup_com = {'`scope system`':0, '`scope security`':0, '`scope eth-server`':0}

for line in f.readlines():
    m1 = pattern1.match(line.strip()) 
    m2 = pattern2.match(line.strip()) 

    if re.compile('Mgmt Interface Information').match(line.strip()):
        # scope end
        if prev_com:
            if SCOPE > 2:
                if not pattern2.match(prev_com):
                    com_content[scope_com_list[0]][scope_com_list[1]][prev_com] = content
            else:
                if not pattern2.match(prev_com):
                    com_content[scope_com_list[0]][prev_com] = content
            content = list()
            prev_com = ""

        SCOPE = 0
        #print scope_com_list
        scope_com_list = list()

    if SCOPE > 0 and m1:
        if prev_com:
            if SCOPE > 2:
                if m2 and not pattern2.match(prev_com) and pattern1.match(prev_com):
                    SCOPE = 0
                if len(scope_com_list) == 2:
                    com_content[scope_com_list[0]][scope_com_list[1]] = dict()
                    #com_content[scope_com_list[0]][scope_com_list[1]] = dict()
                    #print "init nest scope"
                if not pattern2.match(prev_com):
                    com_content[scope_com_list[0]][scope_com_list[1]][prev_com] = content
            else:
                if len(scope_com_list) == 1 :
                    #print scope_com_list[0], dup_com.keys()
                    if scope_com_list[0] in dup_com.keys():
                        if dup_com[scope_com_list[0]] == 0:
                            com_content[scope_com_list[0]] = dict()
                            dup_com[scope_com_list[0]] = 1
                    else:
                        com_content[scope_com_list[0]] = dict()

                    #com_content[scope_com_list[0]] = dict()
                if not pattern2.match(prev_com):
                    com_content[scope_com_list[0]][prev_com] = content
            content = list()

            if pattern2.match(prev_com) and pattern2.match(m1.group()): 
                SCOPE +=1
            elif m2 and SCOPE > 0:
                SCOPE -= 1

        prev_com = m1.group()

        if m2: 
            if len(scope_com_list) > 1:
               # print scope_com_list
                scope_com_list = list()

            SCOPE += 1
            scope_com_list.append(m2.group())

        else:
            scope_com_list.append(m1.group())

    elif m2:
        scope_com_list = list()
        scope_com_list.append(m2.group())
        SCOPE += 1
        if prev_com:
            #print content
            com_content[prev_com] = content
            content = list()
        #prev_com = "" 
        prev_com = m2.group() 

    elif m1: 
        #print line.strip()
        #if len(content) > 0:
        if prev_com:
            #print content
            com_content[prev_com] = content
            content = list()
        prev_com = m1.group()
    else:
            pass
            #print line.strip()
            content.append(line.strip())
            #content.append(line)

#if prev_com:
#    com_content[prev_com] = content

#print com_content.keys()
#for i in com_content:
#    if isinstance(i, dict):
#        print i.keys()

#print com_content['`show chassis inventory expand`']
print com_content['`show chassis inventory detail`']

#print com_content['`scope monitoring`']['`show mgmt-if-mon-policy`']


#print com_content['`scope system`'].keys()
#print com_content['`scope system`']['`show managed-entity detail`']
#print com_content['`scope system`']['`scope capability`'].keys()
#print com_content['`scope system`']['`scope services`'].keys()


#print com_content['`scope security`'].keys()
#print com_content['`scope security`']['`scope radius`'].keys()

#print com_content['`scope eth-server`'].keys()
#print com_content['`scope eth-server`']['`scope fabric a`'].keys()
#print com_content['`scope eth-server`']['`scope fabric b`'].keys()

#print com_content['`scope security`'].keys()
#print com_content['`scope security`']['`scope radius`'].keys()
#print com_content['`scope eth-server`']['`scope fabric a`'].keys()
#print com_content['`scope server 1/1`']['`scope adapter 1`'].keys()
#print com_content['`scope server 1/2`']['`scope adapter 1`'].keys()

FAN = False

iocard = re.compile('^IOCard \d+:$')

for i in com_content['`show chassis inventory expand`']:
    if i == "Fan Modules:":
        #print "Fan Modules"
        FAN = True 
        fan_list = list()
        continue
    if iocard.match(i):
        FAN = False
        break
    if FAN:
        fan_list.append(i)

print fan_list
