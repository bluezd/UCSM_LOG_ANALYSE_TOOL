#!/usr/bin/python

import re
import pygtk
pygtk.require('2.0')
import gtk

class BasicTreeViewExample(object):
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self, com_content):
        self.chassis_count = 0
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

        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Basic TreeView Example")
        self.window.set_size_request(200, 200)
        self.window.connect("delete_event", self.delete_event)

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str)

        self.chassis_inventory_expand(com_content['`show chassis inventory expand`'])
        self.chassis_inventory_detail(com_content['`show chassis inventory detail`'])
        self.chassis_iom_detail(com_content['`show chassis iom detail`'])
        self.server_inventory_expand(com_content['`show server inventory expand`'])
        self.server_status_detail(com_content['`show server status detail`'])
        self.server_memory_detail(com_content['`show server memory detail`'])

        # Display Chassis Information
        for chassis in range(1, self.chassis_count + 1):
            cha = self.treestore.append(None, ['Chassis %i' % chassis])

            # parse chassis inventory detail
            chassis_detail = self.treestore.append(cha, ['Chassis Detail'])
            for i in self.Chassis_Detail_Content[sorted(self.Chassis_Detail_Content.keys())[chassis - 1]]:
                chassis_detail_row = self.treestore.append(chassis_detail, [i])

            # parse FANS
            fan = self.treestore.append(cha, ['Fans'])
            #for (i,j) in self.Chassis_FAN_Content[chassis].items():
            for (i,j) in sorted(self.Chassis_FAN_Content[chassis].iteritems(), key=lambda d:d[0]):
                fan_row = self.treestore.append(fan, [i])
                for h in j:
                    self.treestore.append(fan_row, [h])

            # parse IOM
            iom = self.treestore.append(cha, ['IO Modules'])
            for (i,j) in sorted(self.Chassis_IOM_Content[chassis].iteritems(), key=lambda d:d[0]):
                iom_row = self.treestore.append(iom, [i])
                iom_status_row = self.treestore.append(iom_row, ['IOM Status'])
                for x in self.Chassis_IOM_Detail[sorted(self.Chassis_IOM_Detail.keys())[chassis - 1]][i.split()[1]]:
                    self.treestore.append(iom_status_row, [x])
                iom_info_row = self.treestore.append(iom_row, ['IOM Info'])
                for h in j:
                    self.treestore.append(iom_info_row, [h])

            # parse PSUs
            psu = self.treestore.append(cha, ['PSUs'])
            for (i,j) in sorted(self.Chassis_PSU_Content[chassis].iteritems(), key=lambda d:d[0]):
                psu_row = self.treestore.append(psu, [i])
                for h in j:
                    self.treestore.append(psu_row, [h])

            # parse Servers
            server = self.treestore.append(cha, ['Servers'])
            for (i,j) in sorted(self.Chassis_Servers_Content[chassis].iteritems(), key=lambda d:d[0]):
                server_row = self.treestore.append(server, [i])
                # Server Inventory
                server_inv_row = self.treestore.append(server_row, ["Server Inventory"])
                for x in self.Chassis_Server_Detail[sorted(self.Chassis_Server_Detail.keys())[chassis - 1]][i.split(' ')[1].split('/')[1]]:
                    self.treestore.append(server_inv_row, [x])
                # Server Memory Information
                server_mem_row = self.treestore.append(server_row, ["Memory Info"])
                for x in self.Server_Mem_Detail[sorted(self.Server_Mem_Detail.keys())[chassis - 1]][i.split(' ')[1].split('/')[1]]:
                    self.treestore.append(server_mem_row, [x])
                # Server Status
                server_sts_row = self.treestore.append(server_row, ["Server Status"])
                for x in self.Server_Status_Detail[sorted(self.Server_Status_Detail.keys())[chassis - 1]][i.split(' ')[1].split('/')[1]]:
                    self.treestore.append(server_sts_row, [x])
                # Server Information
                server_info_row = self.treestore.append(server_row, ['Server Info'])
                for h in j:
                    self.treestore.append(server_info_row, [h])

        # Display Fabric Interconnect Information
        #self.fi_inventory_expand(com_content['`show fabric-interconnect inventory expand`'])

        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        #self.tvcolumn = gtk.TreeViewColumn('Column 0')
        self.tvcolumn = gtk.TreeViewColumn('Equipment Information')

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        #self.window.add(self.treeview)
        
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.window.add(self.scrolledwindow)
       # self.treeview.set_model(listmodel)

        self.window.show_all()

    def chassis_inventory_expand(self, chassis_inv_list):
        """docstring for chassis_inventory"""

        for item in chassis_inv_list: 
            if self.RE_Chassis.match(item):
                self.chassis_count += 1

                serverPattern = re.compile('^\s+Server %s/\d+:$' % self.chassis_count)
                self.Chassis_Servers_Content[self.chassis_count] = dict()
                serverPrevNum = ""

                psuPattern = re.compile('^\s+PSU \d+:$')
                self.Chassis_PSU_Content[self.chassis_count] = dict()
                psuPrevNum = ""

                fanPattern = re.compile('^\s+Tray 1 Module \d+:$')
                self.Chassis_FAN_Content[self.chassis_count] = dict()
                fanPrevNum = ""

                iomPattern = re.compile('^\s+IOCard \d+:$')
                self.Chassis_IOM_Content[self.chassis_count] = dict()
                iomPrevNum = ""

                allContent = list()
            # parse servers
            elif serverPattern.match(item):
                if serverPrevNum:
                    self.Chassis_Servers_Content[self.chassis_count][serverPrevNum] = allContent
                    allContent = list()

                serverPrevNum = serverPattern.match(item).group().split(":")[0].strip()
            elif psuPattern.match(item):
                if serverPrevNum:
                    self.Chassis_Servers_Content[self.chassis_count][serverPrevNum] = allContent
                    allContent = list()
                    serverPrevNum = ""

                if psuPrevNum:
                    self.Chassis_PSU_Content[self.chassis_count][psuPrevNum] = allContent
                    allContent = list()
                    
                psuPrevNum = psuPattern.match(item).group().split(":")[0].strip()
            elif fanPattern.match(item):
                if psuPrevNum:
                    self.Chassis_PSU_Content[self.chassis_count][psuPrevNum] = allContent[:-1]
                    allContent = list()
                    psuPrevNum = ""

                if fanPrevNum:
                    self.Chassis_FAN_Content[self.chassis_count][fanPrevNum] = allContent
                    allContent = list()
                
                fanPrevNum = "Fan Module " + "".join(fanPattern.match(item).group().split(":")[0].split()[-1:])
            elif iomPattern.match(item):
                if fanPrevNum:
                    self.Chassis_FAN_Content[self.chassis_count][fanPrevNum] = allContent
                    allContent = list()
                    fanPrevNum = ""

                if iomPrevNum:
                    self.Chassis_IOM_Content[self.chassis_count][iomPrevNum] = allContent
                    allContent = list()

                iomPrevNum = iomPattern.match(item).group().split(":")[0].strip()
            elif "    Fabric Facing Interfaces:" == item:
                if iomPrevNum:
                    self.Chassis_IOM_Content[self.chassis_count][iomPrevNum] = allContent
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
                chassisPrevNum = self.RE_Chassis.match(item).group().split(":")[0]
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
                serverPrevNum = serverDetailPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[1]
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
                serverPrevNum = serverStatusPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[1]
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
                serverPrevNum = serverMemPattern.match(item).group().split(':')[0].split(' ')[1].split('/')[1]
            elif item:
                allContent.append(item)

        if serverPrevNum and chassisPrevNum:
            self.Server_Mem_Detail[chassisPrevNum][serverPrevNum] = allContent
            serverPrevNum = ""

    #def fi_inventory_expand(self, fi_inv_info):
    #    """docstring for fi_inventory_expand"""
    #    fiPattern = re.compile('^[A-Z]$')


pattern1 = re.compile('`.*`')
pattern2 = re.compile('^`scope .*`')
f = open("logs/sam_techsupportinfo", "r")
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
            #content.append(line.strip())
            content.append(line.rstrip())

def main():
    gtk.main()

if __name__ == "__main__":
    #tvexample = BasicTreeViewExample(com_content['`show chassis inventory expand`'])
    tvexample = BasicTreeViewExample(com_content)
    main()

f.close()
