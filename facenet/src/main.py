#!/usr/bin/python
# -*- coding: utf-8 -*-
import globalVar

import gi
import sys
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

state = None

class Handler:



    def on_window_destroy(self,*args):
        Gtk.main_quit()

    def on_mybutton_selection_changed(self, widget):
        filepath = widget.get_file().get_path()
        #filepath = "Hello World"
        #print ("selected folder:" + filepath)
        #globalVar.globalFilepath = filepath

        f = open( "myConfig.ini", 'w' )
        f.write( '[myVars]'+ '\n' )
        f.write( 'globalFilepath = ' + filepath + '\n' )
        f.close()

        #print ("[myVars]")
        #print ("globalFilepath: "+globalVar.globalFilepath)
        #print ("Global Var : " + globalVar.globalFilepath)

    def btn_proceed (self,widget):
        os.system('python3 test4.py')

    def on_checkb1_toggled(self, button):
        if button.get_active():
            state = "active_img"

        else:
            state = "inactive_img"
        return (state)

    def on_checkb2_toggled(self, button):
        if button.get_active():
            state = "active_vid"

        else:
            state = "inactive_vid"
        print (state)

    def set_visibility(self,state):
        if state == "active_img":
            widget.set_sensitive(True)
        else:
            widget.set_sensitive(False)

class Example:

    def __init__(self):

        self.gladefile = "main.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(Handler())

        window = self.builder.get_object("winMain")
        #window.show_all()
        self.set_window("winMain")

        #set set_sensitive
        tog_image = self.builder.get_object("toggle_image")
        tog_video = self.builder.get_object("toggle_video")

    if state == "active_img":
        tog_image.set_sensitive(True)

    def set_window(self,win):
        self.window = self.builder.get_object(win)
        self.window.show_all()

    def main(self):
        Gtk.main()

if __name__ == "__main__":
    x = Example()
    x.main()

#if __name__ != "__main__":

    #object1 = Handler()
    #sum = object1.pass_value()

    #def pass_value ():
        #print("Items : "+sum)
        #return (sum)
        #if sum is None:
            #print("sum is none")
