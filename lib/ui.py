#!/usr/bin/python

import re
import pygtk
import gobject
import pango
pygtk.require('2.0')
import gtk
from ucsm_log_parse import UCSM_LOG_PARSE, ucsm_get_data

class UCSM_GUI(UCSM_LOG_PARSE):
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self, com_content):
        #UCSM_LOG_PARSE.__init__(self)
        super(UCSM_GUI, self).__init__()
        self.com_content = com_content
        self.info_tab = ['_Equipment','_Event Log', '_Error Log']
        self.tree_store = dict()

        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("UCSM B Series Logs Analysing Tool")
        self.window.set_size_request(800, 800)
        self.window.connect("delete_event", self.delete_event)

        self.hpaned = gtk.HPaned()
        self.window.add(self.hpaned)

        self.notebook = gtk.Notebook()
        for tab in self.info_tab:
            scrolled_window = gtk.ScrolledWindow()
            scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            scrolled_window.set_shadow_type(gtk.SHADOW_IN)

            self._new_notebook_page(self.notebook, scrolled_window, tab)

            treeview = self.__create_treeview(tab)
            scrolled_window.add(treeview)

        self.hpaned.add(self.notebook)

        self.notebook1 = gtk.Notebook()
        self.hpaned.add(self.notebook1)
        
        self.scrolled_window2, self.info_buffer = self.__create_text(False)
        self._new_notebook_page(self.notebook1, self.scrolled_window2, '_Info')
        #self.tag = self.info_buffer.create_tag('title')
        #self.tag.set_property('font', 'Sans 18')

        #self.tag = self.info_buffer.create_tag('good', foreground='#00007F',
        #    weight=pango.WEIGHT_BOLD)
        self.tag = self.info_buffer.create_tag('good', foreground='#007F00',
            style=pango.STYLE_ITALIC)
        self.tag.set_property('font', 'monospace')
        self.tag = self.info_buffer.create_tag('bad', foreground='#7F007F',
            style=pango.STYLE_ITALIC)

        #scrolled_window, self.info_buffer = self.__create_text(True)
        #self._new_notebook_page(scrolled_window, '_Source')
        #tag = self.info_buffer.create_tag('source')
        #tag.set_property('font', 'monospace')
        #tag.set_property('pixels_above_lines', 0)
        #tag.set_property('pixels_below_lines', 0)
        #tag = self.info_buffer.create_tag('keyword', foreground='#00007F',
        #    weight=pango.WEIGHT_BOLD)
        #tag = self.info_buffer.create_tag('string', foreground='#7F007F')
        #tag = self.info_buffer.create_tag('comment', foreground='#007F00',
        #    style=pango.STYLE_ITALIC)

        #self.scrolledwindow = gtk.ScrolledWindow()
        #self.scrolledwindow.add(self.treeview)
        #self.window.add(self.scrolledwindow)
        self.__parse_data(self.tree_store['_Equipment'])
        self.__parse_event_log(self.tree_store['_Event Log'])
        self.__parse_error_log(self.tree_store['_Error Log'])

        self.window.show_all()

    def _new_notebook_page(self, notebook, widget, label):
        l = gtk.Label('')
        l.set_text_with_mnemonic(label)
        notebook.append_page(widget, l)

    def __create_text(self, is_source=False):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)

        self.text_view = gtk.TextView()
        scrolled_window.add(self.text_view)

        self.buffer = gtk.TextBuffer(None)
        self.text_view.set_buffer(self.buffer)
        self.text_view.set_editable(False)
        self.text_view.set_cursor_visible(False)

        self.text_view.set_wrap_mode(not is_source)

        return scrolled_window, self.buffer

    def __parse_error_log(self, treestore):
        self.error_information(self.com_content['`show fault detail`'])
        for priority in self.Fault_Detail.keys():
            p = treestore.append(None, [priority])
            for id_num in sorted(self.Fault_Detail[priority].keys()):
                treestore.append(p, [id_num])

    def __parse_event_log(self, treestore):
        self.event_information(self.com_content['`show event detail`'])
        for time_stamp in sorted(self.Event_Detail.keys()):
            treestore.append(None, [time_stamp])

    def __parse_data(self, treestore):
        """docstring for self.__parse_data"""
        self.chassis_inventory_expand(self.com_content['`show chassis inventory expand`'])
        self.chassis_inventory_detail(self.com_content['`show chassis inventory detail`'])
        self.chassis_iom_detail(self.com_content['`show chassis iom detail`'])
        self.server_inventory_expand(self.com_content['`show server inventory expand`'])
        self.server_status_detail(self.com_content['`show server status detail`'])
        self.server_memory_detail(self.com_content['`show server memory detail`'])

        # Display Chassis Information
        #for chassis in range(1, self.chassis_count + 1):
        loop = 0
        for chassis in self.chassis_num:
            loop += 1
            Chassis_Name = 'Chassis %i' % int(chassis)
            cha = treestore.append(None, [Chassis_Name])
            self.Integrated_Info[Chassis_Name] = dict()

            # parse chassis inventory detail
            treestore.append(cha, ['Chassis Detail'])
            self.Integrated_Info[Chassis_Name]['Chassis Detail'] = self.Chassis_Detail_Content[chassis]

            # parse FANS
            fan = treestore.append(cha, ['Fans'])
            self.Integrated_Info[Chassis_Name]['Fans'] = dict()
            for (i,j) in sorted(self.Chassis_FAN_Content[chassis].iteritems(), key=lambda d:d[0]):
                fan_row = treestore.append(fan, [i])
                self.Integrated_Info[Chassis_Name]['Fans'][i] = j

            # parse IOM
            iom = treestore.append(cha, ['IO Modules'])
            self.Integrated_Info[Chassis_Name]['IO Modules'] = dict()
            for (i,j) in sorted(self.Chassis_IOM_Content[chassis].iteritems(), key=lambda d:d[0]):
                iom_row = treestore.append(iom, [i])
                self.Integrated_Info[Chassis_Name]['IO Modules'][i] = dict()
                iom_status_row = treestore.append(iom_row, ['IOM Status'])
                self.Integrated_Info[Chassis_Name]['IO Modules'][i]['IOM Status'] = self.Chassis_IOM_Detail[chassis][i.split()[1]]
                iom_info_row = treestore.append(iom_row, ['IOM Info'])
                self.Integrated_Info[Chassis_Name]['IO Modules'][i]['IOM Info'] = j 

            # parse PSUs
            psu = treestore.append(cha, ['PSUs'])
            self.Integrated_Info[Chassis_Name]['PSUs'] = dict()
            for (i,j) in sorted(self.Chassis_PSU_Content[chassis].iteritems(), key=lambda d:d[0]):
                psu_row = treestore.append(psu, [i])
                self.Integrated_Info[Chassis_Name]['PSUs'][i] = j

            # parse Servers
            server = treestore.append(cha, ['Servers'])
            self.Integrated_Info[Chassis_Name]['Servers'] = dict()
            for i,j in sorted(self.Server_Mem_Detail[chassis].iteritems(), key = lambda d:d[0]):
                server_row = treestore.append(server, [i])
                self.Integrated_Info[Chassis_Name]['Servers'][i] = dict() 
                # Server Inventory
                server_inv_row = treestore.append(server_row, ["Server Inventory"])
                self.Integrated_Info[Chassis_Name]['Servers'][i]['Server Inventory'] = self.Chassis_Server_Detail[chassis][i]

                # Server Memory Information
                server_mem_row = treestore.append(server_row, ["Memory Info"])
                #self.Integrated_Info[Chassis_Name]['Servers'][i]['Memory Info'] = self.Server_Mem_Detail[chassis][i]
                self.Integrated_Info[Chassis_Name]['Servers'][i]['Memory Info'] = j

                # Server Status
                server_sts_row = treestore.append(server_row, ["Server Status"])
                self.Integrated_Info[Chassis_Name]['Servers'][i]['Server Status'] = self.Server_Status_Detail[chassis][i]

                # Server Information
                server_info_row = treestore.append(server_row, ['Server Info'])
                self.Integrated_Info[Chassis_Name]['Servers'][i]['Server Info'] = self.Chassis_Servers_Content[chassis][i]

        fi = treestore.append(None, ['Fabric Interconnects'])
        self.Integrated_Info['Fabric Interconnects'] = dict()
        # Display Fabric Interconnect Information
        self.fi_inventory_expand(self.com_content['`show fabric-interconnect inventory expand`'])
        for i in sorted(self.FI_Inventory_Info.keys()):
            FI_NAME = 'Fabric Interconnect %s' % i
            fi_row = treestore.append(fi, [FI_NAME])
            self.Integrated_Info['Fabric Interconnects'][FI_NAME] = dict()

            for j,h in self.FI_Inventory_Info[i].iteritems():
                # Fabric Card
                child_row = treestore.append(fi_row, [j])
                self.Integrated_Info['Fabric Interconnects'][FI_NAME][j] = h 
                
    def __create_treeview(self, tab_name):
        """docstring for __create_treeview"""
        treestore = gtk.TreeStore(str)
        self.tree_store[tab_name] = treestore
        treeview = gtk.TreeView(treestore)
        selection = treeview.get_selection()
        selection.set_mode(gtk.SELECTION_BROWSE)
        treeview.set_size_request(200, -1)

        column = gtk.TreeViewColumn(tab_name)

        treeview.append_column(column)

        cell = gtk.CellRendererText()
        cell.set_property('style', pango.STYLE_ITALIC)

        # add the cell to the tvcolumn and allow it to expand
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', 0)

        if tab_name == "_Equipment":
            selection.connect('changed', self.selection_changed_equipment)
        elif tab_name == "_Event Log":
            selection.connect('changed', self.selection_changed_event)
        elif tab_name == "_Error Log":
            selection.connect('changed', self.selection_changed_error)

        treeview.expand_all()

        return treeview

    def selection_changed_error(self, selection):
        self.clear_buffers()
        model, iter = selection.get_selected()
        if not iter or model.iter_has_child(iter):
            return False

        name = model.get_value(iter, 0)
        parent_iter = model.iter_parent(iter)
        parent_name = model.get_value(parent_iter, 0)
        self.insert_data(self.Fault_Detail[parent_name][name])

    def selection_changed_event(self, selection):
        self.clear_buffers()
        model, iter = selection.get_selected()
        if not iter or model.iter_has_child(iter):
            return False

        name = model.get_value(iter, 0)
        self.insert_data(self.Event_Detail[name])

    def selection_changed_equipment(self, selection):
        # model treeStore
        # iter treeIter 
        self.clear_buffers()
        model, iter = selection.get_selected()
        if not iter or model.iter_has_child(iter):
            return False

        parent_list = list()
        parent_count = 0
        tmp_iter = iter
        while True:
            tmp_parent_iter = model.iter_parent(tmp_iter)
            if tmp_parent_iter:
                tmp_parent_name = model.get_value(tmp_parent_iter, 0)
                parent_list.append(tmp_parent_name)
                parent_count += 1
                tmp_iter = tmp_parent_iter
            else:
                break

        parent_list.reverse()
        name = model.get_value(iter, 0)

        if parent_count == 1:
            self.insert_data(self.Integrated_Info[parent_list[0]][name])
        elif parent_count == 2:
            self.insert_data(self.Integrated_Info[parent_list[0]][parent_list[1]][name])
        elif parent_count == 3:
            self.insert_data(self.Integrated_Info[parent_list[0]][parent_list[1]][parent_list[2]][name])

    def insert_data(self, lines):
        buffer = self.info_buffer
        iter = buffer.get_iter_at_offset(0)

        #buffer.insert(iter, lines[0])
        #start = buffer.get_iter_at_offset(0)
        #buffer.apply_tag_by_name('title', start, iter)
        #buffer.insert(iter, '\n')
        #for line in lines[1:]:
        #    buffer.insert(iter, line)
        #    buffer.insert(iter, '\n')

        for line in lines: 
            if line.find("Overall Status:") != -1:
                buffer.insert(iter, line.split(":")[0]+":")
                if line.split(":")[1].strip() and line.split(":")[1].strip() != "Operable":
                    buffer.insert_with_tags_by_name(iter, line.split(":")[1], 'bad')
                else:
                    buffer.insert_with_tags_by_name(iter, line.split(":")[1], 'good')
            else:
                buffer.insert(iter, line)
            buffer.insert(iter, '\n')

    def clear_buffers(self):
        start, end = self.info_buffer.get_bounds()
        self.info_buffer.delete(start, end)

    def run(self):
        gtk.main()

if __name__ == "__main__":
    com_content = dict()
    com_content = ucsm_get_data()
    UCSM_GUI(com_content).run()
