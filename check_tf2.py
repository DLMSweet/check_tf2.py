#!/bin/env python
import socket
import time
import sys

class Check_TF2():
    def __init__(self, host, port):
        self.host            = host
        self.port            = port
        self.data,time_taken = self.get_data()
        if self.data == "":
            self.status = "CRITICAL: Host Timed out"
        else:
            self.status = "OK: %s bytes gotten in %.2f seconds" % (len(self.data), time_taken)
            self.parse_data()            
        
    def get_data(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        start = time.time()
        s.connect((self.host, self.port))
        s.send('\xFF\xFF\xFF\xFFTSource Engine Query\0')
        try:
            data = s.recv(1024)
        except socket.timeout:
            data = ""
        s.close()
        end = time.time()
        time_took = end-start
        return data, time_took

    def parse_data(self):
        # https://developer.valvesoftware.com/wiki/Source_Server_Queries
        #print 'Received', repr(data)
        header        = self.data[0:3]
        start_of_data = self.data[4]
        protocol      = self.data[5]
        # Strings that we can't tell the length of. Null terminated.
        split_data        = self.data[6:].split("\x00")
        self.server_name  = split_data[0]
        self.current_map  = split_data[1]
        self.folder_name  = split_data[2]
        self.game_name    = split_data[3]
        # Data we DO know the length of.
        data_split2       = self.data.split(self.game_name)[1]
        self.steam_app_id = repr(data_split2[0:2])
        self.num_players  = ord(data_split2[3])
        self.max_players  = ord(data_split2[4])
        self.num_bots     = ord(data_split2[5])
        self.server_type  = str(data_split2[6])
        self.server_os    = str(data_split2[7])
        self.server_vis   = ord(data_split2[8])
        self.server_VAC   = ord(data_split2[9])
        # I stopped caring at this point
        #print repr(data_split2[10:])
        self.performance_data = "Users=%d;;;0;%d " % (self.num_players, self.max_players)
        self.performance_data = self.performance_data+"Bots=%d;;;; " % (self.num_bots)

    def __str__(self):
        print """
Server Name:             %s
Current Map:             %s
Game Name:               %s
Players on:              %s
Max players:             %s
Number of Bots:          %s
Server Type:             %s
Server OS:               %s
Visibility (0 = Public): %s
VAC (1 = On):            %s
""" % (self.server_name, self.current_map, self.game_name, self.num_players,
       self.max_players, self.num_bots, self.server_type, self.server_os,
       self.server_vis, self.server_VAC)

    def print_data(self):
        self.__str__()

    def print_nagios(self):
        print "%s; Current Map: %s|%s" % ( self.status, self.current_map, self.performance_data)
            
if not len(sys.argv) == 3:
    print "Usage: %s HOSTNAME PORT" % sys.argv[0]
else:
    tf2 = Check_TF2(sys.argv[1], int(sys.argv[2]))
    tf2.print_nagios()


