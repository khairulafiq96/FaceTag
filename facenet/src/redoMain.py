#!/usr/bin/python
# -*- coding: utf-8 -*-
import globalVar

import gi
import sys
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

import configparser

class Example:

    def __init__(self):

        self.gladefile = "main.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)

        window = self.builder.get_object("winMain")
        self.set_window("winMain")

    def set_window(self,win):
        self.window = self.builder.get_object(win)
        self.window.show_all()

    def main(self):
        Gtk.main()

    def on_window_destroy(self,*args):
        Gtk.main_quit()

    def on_mybutton_selection_changed(self, widget):
        filepath = widget.get_file().get_path()
        f = open( "myConfig.ini", 'w' )
        f.write( '[myVars]'+ '\n' )
        f.write( 'globalFilepath = ' + filepath + '\n' )
        f.close()

    def btn_verify(self,widget):
        entryLbl_link = self.builder.get_object("tog_entryLabel")
        label_verify = self.builder.get_object("txt_verify")
        var_videoLink = entryLbl_link.get_text()
        f = open( "myConfig.ini", 'w' )
        f.write( '[myVars]'+ '\n' )
        f.write( 'webcamLink = ' + var_videoLink +'\n' )
        f.write( 'webcamStatus = ')
        f.close()
        os.system('python3 webcamChecker.py')
        config = configparser.ConfigParser()
        config.read("myConfig.ini")
        getVariable = config.get("myVars", "webcamStatus")
        label_verify.set_text(getVariable)


    #get text function to link to activate
    def btn_proceed (self,widget):
        chkbox_img = self.builder.get_object("checkbox_image")
        if chkbox_img.get_active():
            os.system('python3 test4.py')
        else:
            print("run script for webcam")


    def on_checkb1_toggled(self, button):
        tog_image = self.builder.get_object("tog_fileChooser")
        chkbox_vid = self.builder.get_object("checkbox_video")
        if button.get_active():
            tog_image.set_sensitive(True)
            chkbox_vid.set_active(False)
        else:
            tog_image.set_sensitive(False)


    def on_checkb2_toggled(self, button):
        tog_video = self.builder.get_object("tog_entryLabel")
        chkbox_img = self.builder.get_object("checkbox_image")
        if button.get_active():
            tog_video.set_sensitive(True)
            chkbox_img.set_active(False)
        else:
            tog_video.set_sensitive(False)

    def updateValue (myVariable, myValue):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read("myConfig.ini")
        config.set("myVars", myVariable, myValue)

        with open("myConfig.ini", 'w') as configfile:
            config.write(configfile)


    def readValue (myVariable):
        config = configparser.ConfigParser()
        config.read("myConfig.ini")
        getVariable = config.get("myVars", myVariable)
        return getVariable



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
