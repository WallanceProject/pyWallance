#!/bin/bash

# Install pyWallance
# Command: ./Install_pyWallance.sh



# -----------------
# LINUX ENVIRONMENT
# -----------------

# Update Ubuntu
sudo apt-get update

# Install modules
sudo apt-get install -y openssh-server \
python3 \
wget \
nmap \
zip

# Create Wallance Project Directory
mkdir -p $HOME/WallanceProject


# ------------
# SUBLIME TEXT
# ------------

sudo apt-get install -y gnupg
sudo apt-get install -y libgtk2.0-0
sudo wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update
sudo apt-get install -y sublime-text



# -----------------
# GRAFANA INTERFACE
# -----------------

# Install Grafana Interface - Install Web Browser (Firefox)
sudo apt-get install -y firefox

# Install Grafana Interface - Install MySQL
sudo apt-get install -y mysql-server
sudo service mysql start
sudo mysql -e "CREATE USER 'grafanaReader'@'localhost'"
sudo mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'grafanaReader'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Install Grafana Interface - Install Grafana (Default Login/Password: admin/admin)
wget https://dl.grafana.com/oss/release/grafana_5.4.3_amd64.deb
sudo dpkg -i grafana_5.4.3_amd64.deb
rm grafana_5.4.3_amd64.deb



# ----------
# pyWALLANCE
# ----------

# Download pyWallance
cd $HOME/WallanceProject
rm -R -f $HOME/WallanceProject/pyWallance
wget https://github.com/WallanceProject/pyWallance/archive/master.zip -O pyWallance.zip

# Unzip pyWallance
unzip pyWallance.zip
mv pyWallance-master pyWallance
rm pyWallance.zip

# Manage Permission Accesses
chmod 755 $HOME/WallanceProject/pyWallance/*

# Install pyWallance Interface
sudo cp $HOME/WallanceProject/pyWallance/pyWallance_DataSource.yaml /etc/grafana/provisioning/datasources/
sudo cp $HOME/WallanceProject/pyWallance/pyWallance_Dashboard.js /usr/share/grafana/public/dashboards/

# Install pyWallance Interface Request Transaction
sudo cp $HOME/WallanceProject/pyWallance/pyWallance_RequestTransaction.desktop /usr/share/applications/
sudo apt-get install -y desktop-file-utils
sudo update-desktop-database

# Create pyWallance_Node.zip archive
cd $HOME/WallanceProject/pyWallance/
zip pyWallance_Node.zip pyWallance_Node.service Node.py Sensor.py
zip -u pyWallance_Node.zip SmartContract/*/*.py

# Create Install pyWallance Node Script
MyCMD='#!/bin/bash\n'
echo -e $MyCMD > Install_pyWallance_Node.sh
#echo -e "sudo apt-get update" >> Install_pyWallance_Node.sh
echo "sudo mv pyWallance/pyWallance_Node.service /etc/systemd/system/" >> Install_pyWallance_Node.sh
echo "sudo systemctl daemon-reload" >> Install_pyWallance_Node.sh
echo "sudo rm -f -R pyWallance && mkdir pyWallance" >> Install_pyWallance_Node.sh
echo "mv Node.py Sensor.py SmartContract pyWallanceDDS" >> Install_pyWallance_Node.sh
echo "rm Install_pyWallance_Node.sh" >> Install_pyWallance_Node.sh
chmod +x Install_pyWallance_Node.sh
zip -u pyWallance_Node.zip Install_pyWallance_Node.sh
rm Install_pyWallance_Node.sh
