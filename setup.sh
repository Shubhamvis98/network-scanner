#!/bin/bash

#Colour Output
RED="\033[01;31m"
BOLD="\033[01;01m"
RESET="\033[00m"

banner()
{
clear
cat <<'eof'
                                                    +----+      
         __     _                      _            |    |----+ 
      /\ \ \___| |___      _____  _ __| | __        +----+    | 
     /  \/ / _ \ __\ \ /\ / / _ \| '__| |/ /                  | 
    / /\  /  __/ |_ \ V  V / (_) | |  |   <   +----+      +----+
    \_\ \/ \___|\__| \_/\_/ \___/|_|  |_|\_\  |    |------|    |
     __                                       +----+      +----+
    / _\ ___ __ _ _ __  _ __   ___ _ __             |           
    \ \ / __/ _` | '_ \| '_ \ / _ \ '__|      +----+|           
    _\ \ (_| (_| | | | | | | |  __/ |         |    |-+          
    \__/\___\__,_|_| |_|_| |_|\___|_|         +----+            
_______________________An Nmap Front-end____________________________
eof
echo -e "\n${BOLD}Developer: Shubham Vishwakarma${RESET}"
echo -e "${BOLD}Git: ShubhamVis98${RESET}"
echo -e "${BOLD}Web: https://fossfrog.in${RESET}"
echo -e '____________________________________________________________________\n'
}

banner

[ `id -u` -ne 0 ] && echo -e "${RED}[!]Run as root${RESET}" && exit 1

install_dir='/usr/lib/networkscanner'
desktop_file='/usr/share/applications/networkscanner.desktop'

case $1 in
	install)
		mkdir -v $install_dir
		cp -rv logo.svg networkscanner.py networkscanner.ui $install_dir
		cp -v networkscanner.desktop $desktop_file
		chown root:root -R $install_dir
		chmod 644 $desktop_file
		chmod +x $install_dir/networkscanner.py

		echo '[+]Installation Completed'
		;;
	uninstall)
		[ ! -d $install_dir ] && echo "Network Scanner not found." && exit
		rm -vrf $install_dir
		rm -v $desktop_file

		echo '[+]Removed'
		;;
	*)
		echo -e "${RED}Usage:${RESET}"
		echo -e "\t$0 install"
		echo -e "\t$0 uninstall"
esac

