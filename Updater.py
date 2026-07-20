# gabut 

import subprocess
import sys
import os
from tabnanny import check
import pyfiglet

create_figlet = pyfiglet.figlet_format("Jbeny's Updater")
print(create_figlet)
subprocess.run(["sudo", "apt-get", "update", "-y"])
subprocess.run(["sudo", "apt-get", "upgrade", "-y"])
subprocess.run(["sudo", "apt-get", "dist-upgrade", "-y"])
subprocess.run(["sudo", "apt-get", "autoremove", "-y"])
subprocess.run(["sudo", "apt-get", "clean", "-y"])