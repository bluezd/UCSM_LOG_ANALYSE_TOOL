#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from loganalyse import Analyse_Logs 

class Main_Dialog_Window(gtk.Window):
    def __init__(self, parent=None, analyse=None):
        # Create the toplevel window
        self.analyse = analyse
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())

        self.set_title(self.__class__.__name__)
        self.set_border_width(8)

        frame = gtk.Frame("Cisco UCSM log analysing")
        self.add(frame)

        vbox = gtk.VBox(False, 8)
        vbox.set_border_width(8)
        frame.add(vbox)

        self.button_entry = dict()

        # Interactive dialog
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
        button1.connect('clicked', self.tarFileanalyze)
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
        button3.connect('clicked', self.tarFileanalyze)
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

    def tarFileanalyze(self, button):
        """docstring for analyze"""
        if self.button_entry[button].get_text():
            #print self.button_entry[button].get_text()
            self.analyse.run(self.button_entry[button].get_text())
        else:
            pass

    def run(self):
        """docstring for run"""
        gtk.main()

def main():
    analy = Analyse_Logs()
    Main_Dialog_Window(analyse = analy).run()

if __name__ == '__main__':
    main()