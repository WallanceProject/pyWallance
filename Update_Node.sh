#!/bin/bash

# Update pyWallance
# Command: ./Update_pyWallance.sh

# To avoid to type the password, install the RSA Public/Private Key
# Generate RSA Public/Private Key: ssh-keygen -t rsa # ENTER to every field
# Copy Key to target: ssh-copy-id pi@ipaddr



# ----------------------
# EXPORT pyWALLANCE NODE
# ----------------------

# pyWallance Node Service & Launchers
zip pyWallance_Node.zip pyWallance_Node.service \
Node.py Sensor.py

# SmartContracts
zip -u pyWallance_Node.zip SmartContract/*/*.py

# Create Install pyWallance Node Script
MyCMD='#!/bin/bash\n'
echo -e $MyCMD > Install_pyWallance_Node.sh
#echo -e "sudo apt-get update" >> Install_pyWallance_Node.sh
echo "sudo mv pyWallance_Node.service /etc/systemd/system/" >> Install_pyWallance_Node.sh
echo "sudo systemctl daemon-reload" >> Install_pyWallance_Node.sh
echo "sudo rm -f -R pyWallance && mkdir pyWallance" >> Install_pyWallance_Node.sh
echo "mv Node.py Sensor.py SmartContract pyWallance" >> Install_pyWallance_Node.sh
echo "rm -f pyWallance_Node.zip" >> Install_pyWallance_Node.sh
echo "rm -f Install_pyWallance_Node.sh" >> Install_pyWallance_Node.sh
chmod +x Install_pyWallance_Node.sh
zip -u pyWallance_Node.zip Install_pyWallance_Node.sh
rm Install_pyWallance_Node.sh



# ----------------------
# UPDATE pyWALLANCE NODE
# ----------------------

# Find All Node IPs
IPs=$(sudo nmap -sn $(ip -o -f inet addr show | awk '{print $4}' | grep '192') | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print " => "$3;}' | grep "B8:27:EB" | awk '{print $1}')

for ip in $IPs
do
	echo "********** Update Node $ip **********"
	scp pyWallance_Node.zip pi@$ip:/home/pi/
	ssh pi@$ip 'unzip pyWallance_Node.zip && sudo ./Install_pyWallance_Node.sh'
done



# ---------------------------
# UPDATE pyWALLANCE INTERFACE
# ---------------------------

# Update DCoinRate into pyWallance_Dashboard.js file
DCoinRate=$(grep 'DCoinRate = ' Node.py | cut -d " " -f 3)
sed -i "s/SELECT .* AS DCOIN_RATE/SELECT $DCoinRate AS DCOIN_RATE/g" pyWallance_Dashboard.js
sudo cp pyWallance_Dashboard.js /usr/share/grafana/public/dashboards/
