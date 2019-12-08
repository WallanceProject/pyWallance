#!/bin/bash

# Shutdown pyWallance Node (Raspberry)
# Command: ./Shutdown_Node.sh

# To avoid to type the password, install the RSA Public/Private Key
# Generate RSA Public/Private Key: ssh-keygen -t rsa # ENTER to every field
# Copy Key to target: ssh-copy-id pi@ipaddr

# Find All Node IPs
IPs=$(sudo nmap -sn $(ip -o -f inet addr show | awk '{print $4}' | grep '192') | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print " => "$3;}' | grep "B8:27:EB" | awk '{print $1}')

for ip in $IPs
do
	echo "********** Shutdown Node $ip **********"
	ssh pi@$ip 'sudo shutdown -h now' >> /dev/null &
done