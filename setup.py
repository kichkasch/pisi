"""
Manual setup file for pisi

Run with 
    python setup.py build /         - or
    python setup.py install /
    
Puts all PISI stuff under /opt/pisi (assuming you provide / as destination)
Some links and additional stuff is put in corresponding places.
"""

import sys
import os
import os.path
import shutil

filesToMove = [
               ['conf', 'home/root/.pisi', 'conf.default'], 
               ['build/pisi.desktop', 'usr/share/applications', 'pisi.desktop'], 
               ['build/pisi.png', 'usr/share/pixmaps', 'pisi.png']
               ]
filesToLink = [
               ['../opt/pisi/pisi.py', 'bin','pisi'], 
               ['../opt/pisi/pisigui.py', 'bin', 'pisigui']
               ]


def doBuild(path):
    pass

def doInstall(path):
    print "installing pisi"
    basedir = os.path.join(path, 'opt/pisi')
    if not os.path.exists(os.path.join(path, 'opt/')):
        os.mkdir(os.path.join(path, 'opt/'))
    shutil.copytree(os.getcwdu(), basedir)
    for entry in filesToMove:
        dir = os.path.join(path, entry[1])
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.move(os.path.join(basedir, entry[0]), os.path.join(path, entry[1], entry[2]))
    for entry in filesToLink:
        destDir = os.path.join(path, entry[1])
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        os.symlink(entry[0], os.path.join(destDir, entry[2]))            

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Wrong number of arguments"
        sys.exit(1)
    if sys.argv[1] == 'build':
        doBuild(sys.argv[2])
    elif sys.argv[1] == 'install':
        doInstall(sys.argv[2])
    
    else:
        print "Unknown command"
        sys.exit(1)

