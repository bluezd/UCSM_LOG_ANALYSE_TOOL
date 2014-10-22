#!/usr/bin/python

import os
import re
import sys
import tarfile
from gui_main import UCSM_GUI
from ucsm_log import UCSM_LOG_PARSE, ucsm_get_data

Primary_FI = ""

def usage():
    """docstring for usage"""
    if not len(sys.argv) > 1:
        print sys.argv[0], "<file>"
        sys.exit(1)

def determine_cluster_state(DirPath, fileName):
    """docstring for determine_cluster_state"""
    pattern = re.compile("^.*, PRIMARY$")

    f = open(os.path.join(DirPath, fileName), "r")
    for line in f.readlines()[:4]:
        if pattern.match(line.strip()):
            if os.path.basename(DirPath).find(re.split(':', line.strip())[0]) != -1:
                global Primary_FI
                Primary_FI = os.path.basename(DirPath)
            print "FI-%s is the Primary." % re.split(':', line.strip())[0]
    f.close()

def analyse_sam_techsupportinfo(DirPath, fileName):
    """docstring for analyse_sam_techsupportinfo"""
    sam_techsupportinfo = dict()
    sam_techsupportinfo = ucsm_get_data(os.path.join(DirPath, fileName))
    return sam_techsupportinfo

def main():
    """docstring for main"""
    usage()
    #print "Please specifiy the UCSM log path:"
    if tarfile.is_tarfile(sys.argv[1]):
        tar = tarfile.open(sys.argv[1])
        tar.extractall()
        tar.close()
    dir = sys.argv[1].split(".")[0]
    if os.path.isdir(dir):
        for fileName in os.listdir(dir):
            if fileName == "UCSM_A_TechSupport.tar.gz" or fileName == "UCSM_B_TechSupport.tar.gz":
                filePath = os.path.join(dir, fileName)
                fileDirPath = os.path.join(dir, fileName.split(".")[0])
                print "Extracting %s ..." % filePath
                os.mkdir(fileDirPath)
                tar = tarfile.open(filePath)
                tar.extractall(fileDirPath)
                tar.close()

                if not Primary_FI:
                    determine_cluster_state(fileDirPath, "sam_cluster_state")

    print "Analysing the sam_techsupportinfo log"
    techsupportinfo = analyse_sam_techsupportinfo(os.path.join(dir, Primary_FI), "sam_techsupportinfo")
    #print "Analysing the sw_techsupportinfo log"
    UCSM_GUI(techsupportinfo).run()

if __name__ == "__main__":
    main()
