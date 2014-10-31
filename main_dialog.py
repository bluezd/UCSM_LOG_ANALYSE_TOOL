#!/usr/bin/env python

import os
import pygtk
pygtk.require('2.0')
import gtk
from loganalyse import Analyse_Logs 

class Main_Dialog_Window(gtk.Window):
    def __init__(self, parent=None, analyse=None):
        # Create the toplevel window
        self.analyse = analyse
        self.IMAGEDIR = os.path.join(os.path.dirname(__file__), 'lib/images')
        self.Cisco_Image = os.path.join(self.IMAGEDIR, 'ciscologo.gif')
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())

        self.set_title(self.__class__.__name__)
        self.set_border_width(8)

        frame = gtk.Frame()
        self.add(frame)

        vbox = gtk.VBox(False, 8)
        vbox.set_border_width(8)
        frame.add(vbox)

        #vbox = gtk.VBox(False, 8)
        #vbox.set_border_width(8)
        #self.add(vbox)

        label = gtk.Label()
        label.set_markup("<span font_desc=\"Sans 25\" foreground=\"black\" size=\"x-large\"> Cisco UCS Log Analysing Tool</span>")
        vbox.pack_start(label, False, False, 0)

        #frame = gtk.Frame()
        #frame.set_shadow_type(gtk.SHADOW_IN)

        image = gtk.Image()
        image.set_from_file(self.Cisco_Image)

        align = gtk.Alignment(0.5, 0.5, 0, 0)
        #align.add(frame)
        align.add(image)
        vbox.pack_start(align, False, False, 0)

        #image = gtk.Image()
        #image.set_from_file(self.Cisco_Image)
        #frame.add(image)

        self.button_entry = dict()

        hbox = gtk.HBox(False, 8)

        button = gtk.Button("Browse Files")
        button.connect('clicked', self.browse_files)
        hbox.pack_start(button, False, False, 0)

        label = gtk.Label("UCSM")
        label.set_use_underline(True)
        hbox.pack_start(label, False, False, 0)

        self.entry1 = gtk.Entry()
        hbox.pack_start(self.entry1, True, True, 0)
        label.set_mnemonic_widget(self.entry1)

        self.button_entry[button] = self.entry1

        button1 = gtk.Button("Analyze")
        button1.connect('clicked', self.tar_UCSM_analyze)
        hbox.pack_start(button1, False, False, 0)
        self.button_entry[button1] = self.entry1

        vbox.pack_start(hbox, False, False, 0)

        hbox1 = gtk.HBox(False, 8)

        button2 = gtk.Button("Browse Files")
        button2.connect('clicked', self.browse_files)
        hbox1.pack_start(button2, False, False, 0)

        label = gtk.Label("Chassis")
        label.set_use_underline(True)
        hbox1.pack_start(label, False, False, 0)

        self.entry2 = gtk.Entry()
        hbox1.pack_start(self.entry2, True, True, 0)
        label.set_mnemonic_widget(self.entry2)
        self.button_entry[button2] = self.entry2

        button3 = gtk.Button("Analyze")
        button3.connect('clicked', self.tar_Chassis_analyze)
        hbox1.pack_start(button3, False, False, 0)
        self.button_entry[button3] = self.entry2

        vbox.pack_start(hbox1, False, False, 0)

        self.show_all()

    def browse_files(self, button):
        dialog = gtk.FileChooserDialog("Open..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        
        filter = gtk.FileFilter()
        filter.set_name("Tar files")
        filter.add_pattern("*.tar")
        filter.add_pattern("*.rar")
        filter.add_pattern("*.tar.gz")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.xpm")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'selected'
            self.button_entry[button].set_text(dialog.get_filename())
            #entry.set_text(dialog.get_filename())
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()

    def tar_UCSM_analyze(self, button):
        """docstring for analyze"""
        if self.button_entry[button].get_text():
            #print self.button_entry[button].get_text()
            self.analyse.run(self.button_entry[button].get_text())
        else:
            self.warning()

    def tar_Chassis_analyze(self, button):
        """docstring for tar_Chassis_analyze"""
        if self.button_entry[button].get_text():
            print "## Not implement yet ##"
        else:
            self.warning()

    def warning(self):
        dialog = gtk.Dialog("Warning", self, 0,
                (gtk.STOCK_OK, gtk.RESPONSE_OK))

        hbox = gtk.HBox(False, 8)
        hbox.set_border_width(8)
        dialog.vbox.pack_start(hbox, False, False, 0)

        stock = gtk.image_new_from_stock(
                gtk.STOCK_DIALOG_WARNING,
                gtk.ICON_SIZE_DIALOG)
        hbox.pack_start(stock, False, False, 0)

        warn_label = gtk.Label("Please choose the file first !")
        #hbox.pack_start(warn_label, False, False, 0)
        calign=gtk.Alignment(1,1,1,1)
        calign.add(warn_label)
        hbox.pack_start(calign, False, False, 0)

        dialog.show_all()

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            dialog.destroy()

    def run(self):
        """docstring for run"""
        gtk.main()

def main():
    analy = Analyse_Logs()
    Main_Dialog_Window(analyse = analy).run()

if __name__ == '__main__':
    main()
