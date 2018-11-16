#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
import sys
import os
gi.require_version('Gtk','3.0')
from gi.repository import Gtk

import configparser

import mysql.connector
from mysql.connector import Error

class Example:

    def __init__(self):

        self.gladefile = "main.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)

        window = self.builder.get_object("winMain")
        self.set_window("winMain")

        try:
           connection = mysql.connector.connect(host='localhost',
                                     database='facetagDatabase',
                                     user='root',
                                     password='')

           sql_select_query = "SELECT * FROM userData"
           cursor = connection.cursor()
           cursor.execute(sql_select_query)
           records = cursor.fetchall()

           my_name = set()
           my_date = set()
           my_time_in = set()
           my_time_out = set()
           varieties = []

           for row in records:
               my_name.add(row[0])
               my_date.add(row[1])
               my_time_in.add(row[2])
               my_time_out.add(row[3])
               varieties.append(row)
           cursor.close()

        except Error as e :
            print ("Error while connecting to MySQL", e)
        finally:
            #closing database connection.
            if(connection.is_connected()):
                connection.close()
                print("Connection Closed")

        #append lines to 2nd treestore
        [self.builder.get_object("filterstore").append(None,[v[0],v[1],v[2],v[3]]) for v in varieties]




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

        btn_proceed_sensitivity = self.builder.get_object("btnProceed")
        btn_proceed_sensitivity.set_sensitive(True)

    def btn_verify(self,widget):
        entryLbl_link = self.builder.get_object("tog_entryLabel")
        label_verify = self.builder.get_object("txt_verify")
        btn_proceed_sensitivity = self.builder.get_object("btnProceed")

        var_videoLink = entryLbl_link.get_text()
        stat_webcam = 'NULL'
        f = open( "myConfig.ini", 'w' )
        f.write( '[myVars]'+ '\n' )
        f.write( 'webcamLink = ' + var_videoLink +'\n' )
        f.write( 'webcamStatus = '+ stat_webcam + '\n')
        f.write( 'webcamItem = '+ stat_webcam + '\n')
        f.close()
        os.system('python3 webcamChecker.py')
        config = configparser.ConfigParser()
        config.read("myConfig.ini")
        getVariable = config.get("myVars", "webcamStatus")
        label_verify.set_text(getVariable)

        if getVariable == "WEBCAM IS DETECTED":
            btn_proceed_sensitivity.set_sensitive(True)
        else:
            btn_proceed_sensitivity.set_sensitive(False)

    #get text function to link to activate
    def btn_proceed (self,widget):
        chkbox_img = self.builder.get_object("checkbox_image")
        chkbox_vid = self.builder.get_object("checkbox_video")

        if chkbox_img.get_active():
            os.system('python3 test4.py')
        elif chkbox_vid.get_active():
            os.system('python3 test3.py')
        else:
            print("No Data Source")

        self.builder.get_object("filterstore").clear()

        try:
           connection = mysql.connector.connect(host='localhost',
                                     database='facetagDatabase',
                                     user='root',
                                     password='')

           sql_select_query = "SELECT * FROM userData"
           cursor = connection.cursor()
           cursor.execute(sql_select_query)
           records = cursor.fetchall()

           my_name = set()
           my_date = set()
           my_time_in = set()
           my_time_out = set()
           varieties = []
           del varieties[:]

           for row in records:
               my_name.add(row[0])
               my_date.add(row[1])
               my_time_in.add(row[2])
               my_time_out.add(row[3])
               varieties.append(row)
           cursor.close()

        except Error as e :
            print ("Error while connecting to MySQL", e)
        finally:
            #closing database connection.
            if(connection.is_connected()):
                connection.close()
                print("Connection Closed")

        #append lines to 2nd treestore
        [self.builder.get_object("filterstore").append(None,[v[0],v[1],v[2],v[3]]) for v in varieties]

    def on_checkb1_toggled(self, button):
        tog_image = self.builder.get_object("tog_fileChooser")
        chkbox_vid = self.builder.get_object("checkbox_video")
        btn_proceed_sensitivity = self.builder.get_object("btnProceed")
        if button.get_active():
            tog_image.set_sensitive(True)
            chkbox_vid.set_active(False)
        else:
            tog_image.set_sensitive(False)
            btn_proceed_sensitivity.set_sensitive(False)


    def on_checkb2_toggled(self, button):
        tog_video = self.builder.get_object("tog_entryLabel")
        chkbox_img = self.builder.get_object("checkbox_image")
        btn_proceed_sensitivity = self.builder.get_object("btnProceed")
        if button.get_active():
            tog_video.set_sensitive(True)
            chkbox_img.set_active(False)
        else:
            tog_video.set_sensitive(False)
            btn_proceed_sensitivity.set_sensitive(False)

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
