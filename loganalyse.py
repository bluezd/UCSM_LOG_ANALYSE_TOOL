#!/usr/bin/python

import os
import re
import sys
import tarfile
import shutil
from gui_main import UCSM_GUI
from ucsm_log import UCSM_LOG_PARSE, ucsm_get_data

class Analyse_Logs(object):
    """docstring for Analyse_Logs"""
    def __init__(self):
        super(Analyse_Logs, self).__init__()
        self.Primary_FI = ""

    def determine_cluster_state(self, DirPath, fileName):
        """docstring for determine_cluster_state"""
        pattern = re.compile("^.*, PRIMARY$")

        f = open(os.path.join(DirPath, fileName), "r")
        for line in f.readlines()[:4]:
            if pattern.match(line.strip()):
                if os.path.basename(DirPath).find(re.split(':', line.strip())[0]) != -1:
                    #global Primary_FI
                    self.Primary_FI = os.path.basename(DirPath)
                print "FI-%s is the Primary." % re.split(':', line.strip())[0]
        f.close()

    def analyse_sam_techsupportinfo(self, DirPath, fileName):
        """docstring for analyse_sam_techsupportinfo"""
        sam_techsupportinfo = dict()
        sam_techsupportinfo = ucsm_get_data(os.path.join(DirPath, fileName))
        return sam_techsupportinfo

    def run(self, tarfilePath):
        """docstring for main"""
        #print "Please specifiy the UCSM log path:"
        dir = tarfilePath.split(".")[0]
        #dir = os.path.dirname(tarfilePath)
        if tarfile.is_tarfile(tarfilePath):
            if os.path.isdir(dir):
                print "deleting the existing dir %s" % dir
                shutil.rmtree(dir)
            tar = tarfile.open(tarfilePath)
            for member in tar.getmembers():
                if member.isreg():
                    tar_dir = dir
                    if not os.path.isdir(tar_dir):
                        os.mkdir(tar_dir)
                    member.name = os.path.basename(member.name)
                    tar.extract(member, tar_dir)
            tar.close()
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

                    if not self.Primary_FI:
                        self.determine_cluster_state(fileDirPath, "sam_cluster_state")

        print "Analysing the sam_techsupportinfo log"
        techsupportinfo = self.analyse_sam_techsupportinfo(os.path.join(dir, self.Primary_FI), "sam_techsupportinfo")
        #print "Analysing the sw_techsupportinfo log"
        UCSM_GUI(techsupportinfo).run()

def usage():
    """docstring for usage"""
    if not len(sys.argv) > 1:
        print sys.argv[0], "<file>"
        sys.exit(1)

def main():
    """docstring for main"""
    usage()
    Analyse_Logs().run(sys.argv[1])

if __name__ == "__main__":
    main()
