#!/usr/bin/python

import re
import pygtk
import gobject
import pango
pygtk.require('2.0')
import gtk

class UCSM_LOG_PARSE(object):
    def __init__(self):
        self.chassis_num = list()
        self.RE_Chassis = re.compile('^Chassis \d+:$')
        self.Chassis_Detail_Content = dict()
        self.Chassis_Servers_Content = dict()
        self.Chassis_PSU_Content = dict()
        self.Chassis_FAN_Content = dict()
        self.Chassis_IOM_Content = dict()
        self.Chassis_IOM_Detail = dict()
        self.Chassis_Server_Detail = dict()
        self.Server_Status_Detail = dict()
        self.Server_Mem_Detail = dict()
        self.FI_Inventory_Info = dict()
        self.Event_Detail = dict()
        self.Fault_Detail = dict()
        self.Integrated_Info = dict()
        self.System_Firmware = dict()

    def chassis_inventory_expand(self, chassis_inv_list):
        """docstring for chassis_inventory"""
        for item in chassis_inv_list: 
            if self.RE_Chassis.match(item):
                chassis_number = filter(str.isdigit, item)
                self.chassis_num.append(chassis_number)

                serverPattern = re.compile('^\s+Server %s/\d+:$' % chassis_number)
                self.Chassis_Servers_Content[chassis_number] = dict()
                serverPrevNum = ""

                psuPattern = re.compile('^\s+PSU \d+:$')
                self.Chassis_PSU_Content[chassis_number] = dict()
                psuPrevNum = ""

                fanPattern = re.compile('^\s+Tray 1 Module \d+:$')
                self.Chassis_FAN_Content[chassis_number] = dict()
                fanPrevNum = ""

                iomPattern = re.compile('^\s+IOCard \d+:$')
                self.Chassis_IOM_Content[chassis_number] = dict()
                iomPrevNum = ""

                allContent = list()
            # parse servers
            elif serverPattern.match(item):
                if serverPrevNum:
                    self.Chassis_Servers_Content[chassis_number][serverPrevNum] = allContent
                    allContent = list()

                serverPrevNum = serverPattern.match(item).group().strip().rstrip(':').split(' ')[1]
            # parse psu
            elif psuPattern.match(item):
                if serverPrevNum:
                    self.Chassis_Servers_Content[chassis_number][serverPrevNum] = allContent
                    allContent = list()
                    serverPrevNum = ""

                if psuPrevNum:
                    self.Chassis_PSU_Content[chassis_number][psuPrevNum] = allContent
                    allContent = list()
                    
                psuPrevNum = psuPattern.match(item).group().split(":")[0].strip()
            # parse fan
            elif fanPattern.match(item):
                if psuPrevNum:
                    self.Chassis_PSU_Content[chassis_number][psuPrevNum] = allContent[:-1]
                    allContent = list()
                    psuPrevNum = ""

                if fanPrevNum:
                    self.Chassis_FAN_Content[chassis_number][fanPrevNum] = allContent
                    allContent = list()
                
                fanPrevNum = "Fan Module " + "".join(fanPattern.match(item).group().split(":")[0].split()[-1:])
            # parse iom
            elif iomPattern.match(item):
                if fanPrevNum:
                    self.Chassis_FAN_Content[chassis_number][fanPrevNum] = allContent
                    allContent = list()
                    fanPrevNum = ""

                if iomPrevNum:
                    self.Chassis_IOM_Content[chassis_number][iomPrevNum] = allContent
                    allContent = list()

                iomPrevNum = iomPattern.match(item).group().split(":")[0].strip()
            elif "    Fabric Facing Interfaces:" == item:
                if iomPrevNum:
                    self.Chassis_IOM_Content[chassis_number][iomPrevNum] = allContent
                    allContent = list()
                    iomPrevNum = ""
            elif item:
                allContent.append(item)

    def chassis_inventory_detail(self, chassis_detail_list):
        chassisPrevNum = ""
        allContent = list()
        for item in chassis_detail_list:
            if self.RE_Chassis.match(item):
                if allContent:
                    self.Chassis_Detail_Content[chassisPrevNum] = allContent
                self.Chassis_Detail_Content[self.RE_Chassis.match(item).group().split(":")[0]] = dict()
                allContent = list()
                chassisPrevNum = filter(str.isdigit, self.RE_Chassis.match(item).group())
            elif item:
                allContent.append(item) 

        if chassisPrevNum:
            self.Chassis_Detail_Content[chassisPrevNum] = allContent
            chassisPrevNum = ""

    # self.Chassis_IOM_Detail = {'1':{'1':"",'2':""}, '2':{'1':"", '2':""}}
    def chassis_iom_detail(self, chassis_iom_info):
        iomDetailPattern = re.compile('^Chassis Id: \d+$')
        iomIDPattern = re.compile('^ID: \d+$')
        allContent = list()
        chassisPrevNum = ""
        iomPrevNum = ""

        for item in chassis_iom_info:
            if iomDetailPattern.match(item):
                if allContent:
                    self.Chassis_IOM_Detail[chassisPrevNum][iomPrevNum] = allContent
                if iomDetailPattern.match(item).group().split(":")[1].strip() != chassisPrevNum:
                    self.Chassis_IOM_Detail[iomDetailPattern.match(item).group().split(":")[1].strip()] = dict()
                chassisPrevNum = iomDetailPattern.match(item).group().split(":")[1].strip()
            elif iomIDPattern.match(item):
                #self.Chassis_IOM_Detail[chassisPrevNum][iomIDPattern.match(item).group().split(":")[1]] = dict()
                iomPrevNum = iomIDPattern.match(item).group().split(":")[1].strip()
                allContent = list()
            elif item:
                allContent.append(item)

        if iomPrevNum and chassisPrevNum:
            self.Chassis_IOM_Detail[chassisPrevNum][iomPrevNum] = allContent
            chassisPrevNum = ""
            iomPrevNum = ""

    def server_inventory_expand(self, server_inv_info):
        """docstring for server_inventory_expand"""
        serverDetailPattern = re.compile('^Server \d+/\d+:$')
        allContent = list()
        serverPrevNum = ""
        chassisPrevNum = ""

        for item in server_inv_info:
            if serverDetailPattern.match(item):
                if allContent:
                    self.Chassis_Server_Detail[chassisPrevNum][serverPrevNum] = allContent
                    allContent = list()
                if serverDetailPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0] != chassisPrevNum:
                    self.Chassis_Server_Detail[serverDetailPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]] = dict()
                chassisPrevNum = serverDetailPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]
                serverPrevNum = serverDetailPattern.match(item).group().rstrip(':').split(' ')[1]
            elif item:
                allContent.append(item)

        if serverPrevNum and chassisPrevNum:
            self.Chassis_Server_Detail[chassisPrevNum][serverPrevNum] = allContent
            serverPrevNum = ""
            chassisPrevNum = ""

    def server_status_detail(self, server_sts_detail):
        """docstring for server_status_detail"""
        serverStatusPattern = re.compile('^Server \d+/\d+:$')
        allContent = list()
        serverPrevNum = ""
        chassisPrevNum = ""

        for item in server_sts_detail:
            if serverStatusPattern.match(item):
                if allContent:
                    self.Server_Status_Detail[chassisPrevNum][serverPrevNum] = allContent
                    allContent = list()
                if serverStatusPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0] != chassisPrevNum:
                    self.Server_Status_Detail[serverStatusPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]] = dict()
                chassisPrevNum = serverStatusPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]
                serverPrevNum = serverStatusPattern.match(item).group().rstrip(':').split(' ')[1]
            elif item:
                allContent.append(item)

        if serverPrevNum and chassisPrevNum:
            self.Server_Status_Detail[chassisPrevNum][serverPrevNum] = allContent
            serverPrevNum = ""

    def server_memory_detail(self, server_mem_detail):
        """docstring for server_memory_detail"""
        serverMemPattern = re.compile('^Server \d+/\d+:$')
        allContent = list()
        serverPrevNum = ""
        chassisPrevNum = ""

        for item in server_mem_detail:
            if serverMemPattern.match(item):
                if allContent:
                    self.Server_Mem_Detail[chassisPrevNum][serverPrevNum] = allContent
                    allContent = list()
                if serverMemPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0] != chassisPrevNum:
                    self.Server_Mem_Detail[serverMemPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]] = dict()
                chassisPrevNum = serverMemPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[0]
                serverPrevNum = serverMemPattern.match(item).group().rstrip(':').split(' ')[1]
            elif item:
                allContent.append(item)

        if serverPrevNum and chassisPrevNum:
            self.Server_Mem_Detail[chassisPrevNum][serverPrevNum] = allContent
            serverPrevNum = ""

    def fi_inventory_expand(self, fi_inv_info):
        """docstring for fi_inventory_expand"""
        fiPattern = re.compile('^[A-Z]:$')
        contentPattern = re.compile('^\s+\w+.*:$')
        allContent = list()
        fiPrevNum = ""
        contentPrevNum = ""

        for item in fi_inv_info:
            if contentPattern.match(item):
                if allContent:
                    self.FI_Inventory_Info[fiPrevNum][contentPrevNum] = allContent
                    allContent = list()
                contentPrevNum = contentPattern.match(item).group().split(":")[0].strip()
            elif fiPattern.match(item):
                if allContent:
                    self.FI_Inventory_Info[fiPrevNum][contentPrevNum] = allContent
                    allContent = list()
                if fiPattern.match(item).group().split(":")[0] != fiPrevNum:
                    self.FI_Inventory_Info[fiPattern.match(item).group().split(":")[0]] = dict()
                fiPrevNum = fiPattern.match(item).group().split(":")[0]
            elif item:
                allContent.append(item)

        if fiPrevNum and contentPrevNum:
            self.FI_Inventory_Info[fiPrevNum][contentPrevNum] = allContent
            fiPrevNum = ""
            contentPrevNum = ""

    def event_information(self, event_info):
        """docstring for event_information"""
        allContent = list()
        prev_time_stamp = ""
        for line in event_info:
            if line.find("Creation Time") != -1:
                if allContent:
                    self.Event_Detail[prev_time_stamp] = allContent
                time_stamp = line.split(" ")[2]
                prev_time_stamp = time_stamp
                allContent = list()
            elif prev_time_stamp:
                allContent.append(line)

        if prev_time_stamp and allContent:
            self.Event_Detail[prev_time_stamp] = allContent

    def error_information(self, error_info):
        """docstring for event_information"""
        errorPattern = re.compile('^Severity:.*$')
        IDPattern = re.compile('^ID: \d+$')
        allContent = list()
        level = ""
        id_num = ""

        for line in error_info:
            if errorPattern.match(line):
                if allContent:
                    if time_stamp not in self.Fault_Detail[level]:
                        self.Fault_Detail[level][time_stamp] = allContent
                    else:
                        self.Fault_Detail[level][time_stamp].extend(allContent)
                level = line.split(":")[1].strip()
                if level not in self.Fault_Detail:
                    self.Fault_Detail[level] = dict()
                allContent = list()
            if line.find("Creation Time") != -1:
                time_stamp = line.split(" ")[2]
            if level:
                allContent.append(line)

        if time_stamp and allContent:
            if time_stamp not in self.Fault_Detail[level]:
                self.Fault_Detail[level][time_stamp] = allContent
            else:
                self.Fault_Detail[level][time_stamp].extend(allContent)

    def system_firmware_detail(self, firmware_detail, chassis_firmware_detail):
        """docstring for system_firmware_detial"""
        firmwareName = re.compile('^\w+.*:$')
        serverPattern = re.compile('^\s+Server \d+:$')
        iomPattern = re.compile('^\s+IOM \d+.*:$')
        allContent = list()
        iomPrevNum = ""
        prev = ""

        for line in firmware_detail:
            m1 = firmwareName.match(line)
            if m1 and not self.RE_Chassis.match(line):
                if prev:
                    self.System_Firmware[prev] = allContent
                    allContent = list()
                prev = m1.group()[:-1]
                self.System_Firmware[prev] = dict()
            elif self.RE_Chassis.match(line):
                if prev:
                    self.System_Firmware[prev] = allContent
                break
            allContent.append(line)

        if prev:
            self.System_Firmware[prev] = allContent
            allContent = list()
            prev = ""

        for line in chassis_firmware_detail:
            if self.RE_Chassis.match(line):
                if iomPrevNum:
                    self.System_Firmware[chassis_number]["iom"][iomPrevNum] = allContent
                    allContent = list()
                    iomPrevNum = ""

                chassis_number = filter(str.isdigit, line)
                self.System_Firmware[chassis_number] = dict()
                self.System_Firmware[chassis_number]["servers"] = dict()
                self.System_Firmware[chassis_number]["iom"] = dict()
                serverPrevNum = ""
                iomPrevNum = ""
            elif serverPattern.match(line):
                if serverPrevNum:
                    self.System_Firmware[chassis_number]["servers"][serverPrevNum] = allContent
                    allContent = list()
                serverPrevNum = filter(str.isdigit, line)
            elif iomPattern.match(line):
                if serverPrevNum:
                    self.System_Firmware[chassis_number]["servers"][serverPrevNum] = allContent
                    allContent = list()
                    serverPrevNum = ""

                if iomPrevNum:
                    self.System_Firmware[chassis_number]["iom"][iomPrevNum] = allContent
                    allContent = list()
                iomPrevNum = filter(str.isdigit, line)
            else:
                allContent.append(line)

        if iomPrevNum:
            self.System_Firmware[chassis_number]["iom"][iomPrevNum] = allContent
            allContent = list()
            iomPrevNum = ""

def ucsm_get_data(path = "../logs/sam_techsupportinfo"):
    """docstring for ucsm_get_data"""
    pattern1 = re.compile('`.*`')
    pattern2 = re.compile('^`scope .*`')
    f = open(path, "r")

    SCOPE = 0
    SCOPE_ING = False
    SCOPE_END_PREV = False
    SCOPE_NEST = False
    content = list()
    com_content = dict()
    prev_com = ""
    First_SCOPE = False
    dup_com = dict()
    dup_com = {'`scope system`':0, '`scope vm-mgmt`':0, '`scope security`':0, '`scope eth-server`':0}
    SCOPE_Third = False

    for line in f.readlines():
        m1 = pattern1.match(line.strip())
        m2 = pattern2.match(line.strip())

        if re.compile('Server Interface Information').match(line.strip()) or re.compile('.*MgmtIf Information$').match(line.strip()) or re.compile('Server Interface Information').match(line.strip()):
            # scope end
            if prev_com:
                if SCOPE > 2:
                    if not pattern2.match(prev_com):
                        com_content[scope_com_list[0]][scope_com_list[1]][prev_com] = content
                elif SCOPE > 3:
                    if not pattern2.match(prev_com):
                        com_content[scope_com_list[0]][scope_com_list[1]][scope_com_list[2]][prev_com] = content
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
                        if scope_com_list[1] in dup_com.keys():
                            if dup_com[scope_com_list[1]] == 0:
                                com_content[scope_com_list[0]][scope_com_list[1]] = dict()
                                dup_com[scope_com_list[1]] = 1
                        else:
                            try:
                                com_content[scope_com_list[0]][scope_com_list[1]] = dict()
                            except Exception, e:
                                print "#### Error ####"
                                print scope_com_list[0]
                                print scope_com_list[1]
                                print m1.group()
                                print scope_com_list
                    elif len(scope_com_list) == 3 and pattern2.match(prev_com):
                        com_content[scope_com_list[0]][scope_com_list[1]][scope_com_list[2]] = dict()
                        SCOPE_Third = True
                        #print "init nest scope"
                    if not pattern2.match(prev_com):
                        if SCOPE_Third:
                            com_content[scope_com_list[0]][scope_com_list[1]][scope_com_list[2]][prev_com] = content
                            if m2 and not pattern2.match(prev_com) and pattern1.match(prev_com):
                                SCOPE_Third = False
                        else:
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
                    if pattern2.match(scope_com_list[0]) and pattern2.match(scope_com_list[1]) and SCOPE > 1:
                        pass
                    else:
                        scope_com_list = list()
                   # print scope_com_list

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
                #content.append(line.strip())
                content.append(line.rstrip())
    f.close()
    return com_content

def main():
    # using example
    com_content = dict()
    com_content = ucsm_get_data()
    ucsm = UCSM_LOG_PARSE()
    ucsm.chassis_inventory_detail(com_content['`show chassis inventory detail`'])
    for i,j in sorted(ucsm.Chassis_Detail_Content.iteritems(), key=lambda d:d[0]):
        print i
        print j

if __name__ == "__main__":
    main()
