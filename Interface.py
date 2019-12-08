
# pyWallance Interface
# Command: python3 Interface.py

import os
import time
import socket
import struct
import select
import signal
import hashlib
import itertools
import threading
from os import listdir
from random import randrange
from collections import Counter

from Node import *
from Sensor import *


#############################################################
#					  INTERFACE CLASS 						#
#############################################################


class Interface():


	########################
	# INTERFACE PARAMETERS #
	########################

	# Sensor Transaction:
	# [0]: Publisher ID
	# [1]: Topic Name ("SENSOR")
	# [2]: Value

	# Transaction (Request/Consensus):
	# [0]: Subscriber ID
	# [1]: Publisher ID
	# [2]: SmartContract ID
	# [3]: Price
	# [4]: Time
	# [5]: Previous State
	# [6]: DCoin
	# [7]: Nonce


	############################
	# INTERFACE INITIALIZATION #
	############################
	def __init__(self):

		# Create MySQL Wallance Database
		os.system("mysql -u grafanaReader -e 'CREATE DATABASE IF NOT EXISTS pyWALLANCE;'")
		os.system("mysql -u grafanaReader -e \"SET @@SESSION.TIME_ZONE = '+00:00';\"")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'CREATE TABLE IF NOT EXISTS WALLET (PUBLISHER VARCHAR(32), COUNTER INTEGER, STATE VARCHAR(64));'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'CREATE TABLE IF NOT EXISTS REQUEST_TRANSACTIONS (PUBLISHER VARCHAR(32), SMARTCONTRACT VARCHAR(32), PRICE INTEGER, TIME INTEGER, PREVSTATE VARCHAR(64), OUTDATE INTEGER, UNIQUE(PUBLISHER, PREVSTATE));'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'CREATE TABLE IF NOT EXISTS CONSENSUS_TRANSACTIONS (SUBSCRIBER VARCHAR(32), PUBLISHER VARCHAR(32), SMARTCONTRACT VARCHAR(32), PRICE INTEGER, TIME INTEGER, PREVSTATE VARCHAR(64), DCOIN INTEGER, OUTDATE INTEGER);'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'CREATE TABLE IF NOT EXISTS SMARTCONTRACT (NAME VARCHAR(32) UNIQUE, PRICE INTEGER);'")

		# Create SmartContract Database
		for i in os.listdir("SmartContract"):
			if os.path.exists("SmartContract/" +  i + "/" + i + ".py"):
				os.system("mysql -u grafanaReader -D pyWALLANCE -e \"INSERT INTO SMARTCONTRACT (NAME,PRICE) VALUES('" + i.split(Node.DataDelimiter)[0] + "'," + str(i.split(Node.DataDelimiter)[1]) + ");\"")

		# MySQL Wallance Database Lockers
		self.MySQLLock = threading.RLock()

		self.InterfaceRunning = True	

		# Start Consensus Receiver Thread
		self.Receiver = threading.Thread(target=self.ReceiverThread)
		self.Receiver.start()

		# Start Grafana Interface & Nodes
		self.StartGrafana()
		self.StartNode()

		# Set SIGINT signal catcher (CTRL-C)
		signal.signal(signal.SIGINT, self.Stop)


	#############################
	# INTERFACE RECEIVER THREAD #
	#############################
	def ReceiverThread(self):

		# Create & Bind the socket
		RXSocket = []
		RXSocket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
		RXSocket.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
		RXSocket[0].bind((Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))
		RXSocket[1].bind((Sensor.MulticastIP, Sensor.MulticastPort))

		# Add the socket to the multicast group on all interfaces & Non-Blocking
		RXSocket[0].setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack('4sL', socket.inet_aton(Node.ConsensusMulticastIP), socket.INADDR_ANY))
		RXSocket[0].setblocking(False)

		RXSocket[1].setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack('4sL', socket.inet_aton(Sensor.MulticastIP), socket.INADDR_ANY))
		RXSocket[1].setblocking(False)

		# Server Reception loop
		while self.InterfaceRunning:
			
			try:
				ready_socks,_,_ = select.select(RXSocket, [], [], 0)

				for sock in ready_socks:
					PeerData, PeerAddr = sock.recvfrom(1024)

					# Parse Data
					Interface.ParseData(sock.getsockname()[0], PeerData)
	
			except:
				pass

			# Waiting Time Loop
			time.sleep(Node.SamplingTime)

		RXSocket[0].close()
		RXSocket[1].close()
		print("Close Receiver %s:%s" % (Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))
		print("Close Receiver %s:%s" % (Sensor.MulticastIP, Sensor.MulticastPort))


	######################################
	# INTERFACE SEND REQUEST TRANSACTION #
	######################################
	def SendRequestTransaction(RequestInfo):

		# Init & Configure Time-To-Live TX Socket
		TX = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		TX.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
		TX.connect((Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))

		# Parse RequestInfo (Format:  appname:PublisherID_SmartContractID_Price)
		MyRequestTX = RequestInfo.split(':')[1]	# Remove app name
		MyRequestTX = MyRequestTX.split("_")

		# MyRequestTX values
		# [0]: Publisher ID
		# [1]: SmartContract ID
		# [2]: Price
		if (len(MyRequestTX[0]) == 0) or (len(MyRequestTX[1]) == 0) or (len(MyRequestTX[2]) == 0):
			return -1

		# Recover Publisher's PrevState
		PrevState = os.popen("mysql -u grafanaReader -D pyWALLANCE -s -e \"SELECT STATE FROM WALLET WHERE PUBLISHER='" + MyRequestTX[0] + "';\"").readlines()
		PrevState = PrevState[0].split('\n')[0]

		
		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce

		Transaction = [MyRequestTX[0], MyRequestTX[0], MyRequestTX[1], MyRequestTX[2], \
					  str(int(time.time())), PrevState, str(0)]

		# Compute Light PoW
		Nonce = Node.ComputeLightPoW(Transaction)

		# Send Request Transaction
		RequestTX = ""
		for i in Transaction:
			RequestTX += i + Node.DataDelimiter
		RequestTX += str(Nonce)
		TX.sendto(RequestTX.encode("utf8"), (Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))
		TX.close()


	########################
	# INTERFACE PARSE DATA #
	########################
	def ParseData(Topic, Data):

		# Sensor Transaction:
		# [0]: Publisher ID
		# [1]: Topic Name ("SENSOR")
		# [2]: Value

		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce

		# Sensor Topic
		if Topic == Sensor.MulticastIP:
			MyData = Data.decode("utf8").split(Sensor.DataDelimiter)
			os.system("mysql -u grafanaReader -D pyWALLANCE -e \"SELECT COALESCE( (SELECT COUNTER FROM WALLET WHERE PUBLISHER='" + MyData[0] + "')+1,1) INTO @CPT; SELECT COALESCE( (SELECT STATE FROM WALLET WHERE PUBLISHER='" + MyData[0] + "'),'" + Node.GenesisState + "') INTO @ST; PREPARE STMT FROM 'INSERT INTO WALLET (PUBLISHER,COUNTER,STATE) VALUES (''" + MyData[0] + "'', ?, ?)'; EXECUTE STMT USING @CPT,@ST;\"")
			os.system("mysql -u grafanaReader -D pyWALLANCE -e \"SELECT MAX(COUNTER) FROM WALLET WHERE PUBLISHER='" + MyData[0] + "' INTO @CPT; PREPARE STMT FROM 'DELETE FROM WALLET WHERE PUBLISHER=''" + MyData[0] + "'' AND COUNTER <?'; EXECUTE STMT USING @CPT;\"")


		elif Topic == Node.ConsensusMulticastIP:
			MyData = Data.decode("utf8").split(Node.DataDelimiter)

			# Check Light PoW & SmartContract
			if (Node.CheckLightPoW(MyData) == 0) and (Node.CheckSmartContract(MyData[2], MyData[3]) == True):

				# Add New Request Transaction
				if MyData[0] == MyData[1]:

					# Manage old Consensus Responses of Requester
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"UPDATE CONSENSUS_TRANSACTIONS SET OUTDATE = OUTDATE-1 WHERE PUBLISHER='" + MyData[1] + "';\"")
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"DELETE FROM CONSENSUS_TRANSACTIONS WHERE OUTDATE <= 0;\"")

					# Manage old Request Transaction of Requester
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"UPDATE REQUEST_TRANSACTIONS SET OUTDATE = OUTDATE-1 WHERE PUBLISHER='" + MyData[1] + "';\"")
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"DELETE FROM REQUEST_TRANSACTIONS WHERE OUTDATE <= 0;\"")

					# Insert Request Transaction
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"INSERT INTO REQUEST_TRANSACTIONS (PUBLISHER,SMARTCONTRACT,PRICE,TIME,PREVSTATE,OUTDATE) VALUES ('" + MyData[1] + "','" + MyData[2] + "'," + MyData[3] + "," + MyData[4] + ",'" + MyData[5] + "'," + str(Node.TransactionOutdate) + ");\"")
			
				# Add New Consensus Transaction
				else:
					os.system("mysql -u grafanaReader -D pyWALLANCE -e \"INSERT INTO CONSENSUS_TRANSACTIONS (SUBSCRIBER,PUBLISHER,SMARTCONTRACT,PRICE,TIME,PREVSTATE,DCOIN,OUTDATE) VALUES ('" + MyData[0] + "','" + MyData[1] + "','" + MyData[2] + "'," + MyData[3] + "," + MyData[4] + ",'" + MyData[5] + "'," + MyData[6] + "," + str(Node.TransactionOutdate) + ");\"")

		else:
			print("Error Topic")


	###############################
	# INTERFACE CONSENSUS PROCESS #
	###############################
	def ConsensusProcess():

		while True:

			# Find Majority
			MajAvailable = os.popen("mysql -u grafanaReader -D pyWALLANCE -s -e \"SELECT EXISTS (SELECT 1 FROM CONSENSUS_TRANSACTIONS GROUP BY PUBLISHER, SMARTCONTRACT, PRICE, TIME, PREVSTATE, DCOIN HAVING PREVSTATE=(SELECT STATE FROM WALLET WHERE PUBLISHER=CONSENSUS_TRANSACTIONS.PUBLISHER) AND ((SELECT COUNT(DISTINCT PUBLISHER) FROM WALLET)*(" + str(Node.MajorityThreshold) +")) <= COUNT(DISTINCT SUBSCRIBER) LIMIT 1);\"").readlines()
			MajAvailable = MajAvailable[0].split('\n')[0]

			# No Majority
			if MajAvailable != '1':
				break

			else:

				# Recover Majority group
				MajGroup = os.popen("mysql -u grafanaReader -D pyWALLANCE -s -e \"SELECT PUBLISHER, SMARTCONTRACT, PRICE, TIME, PREVSTATE, DCOIN FROM CONSENSUS_TRANSACTIONS GROUP BY PUBLISHER, SMARTCONTRACT, PRICE, TIME, PREVSTATE, DCOIN HAVING PREVSTATE=(SELECT STATE FROM WALLET WHERE PUBLISHER=CONSENSUS_TRANSACTIONS.PUBLISHER) AND ((SELECT COUNT(DISTINCT PUBLISHER) FROM WALLET)*(" + str(Node.MajorityThreshold) +")) <= COUNT(DISTINCT SUBSCRIBER) LIMIT 1;\"").readlines()
				MajGroup = MajGroup[0].split('\t')

				# Extract Publisher
				Publisher = MajGroup[0]

				# Extract SmartContract
				SmartContract= MajGroup[1]

				# Extract Price
				Price = MajGroup[2]

				# Extract Time
				Time = MajGroup[3]

				# Extract PrevState
				PrevState = MajGroup[4]

				# Extract DCoin
				DCoin = MajGroup[5].split('\n')[0]

				# Reward Participants
				os.system("mysql -u grafanaReader -D pyWALLANCE -e \"UPDATE WALLET SET COUNTER=COUNTER+" + str(Node.DCoinReward) + " WHERE PUBLISHER IN (SELECT SUBSCRIBER FROM CONSENSUS_TRANSACTIONS WHERE PUBLISHER='" + Publisher + "' AND SMARTCONTRACT='" +  SmartContract + "' AND PRICE=" + Price + " AND Time=" + Time + " AND PREVSTATE='" + PrevState + "' AND DCOIN=" + DCoin + ");\"")

				# Remove used Consensus Responses & Request Transactions
				os.system("mysql -u grafanaReader -D pyWALLANCE -e \"DELETE FROM CONSENSUS_TRANSACTIONS WHERE PUBLISHER='" + Publisher + "' AND PREVSTATE='" + PrevState + "';\"")
				os.system("mysql -u grafanaReader -D pyWALLANCE -e \"DELETE FROM REQUEST_TRANSACTIONS WHERE PUBLISHER='" + Publisher + "' AND PREVSTATE='" + PrevState + "';\"")

				# Update Wallet (State & Counter) of Publisher after Majority
				# Compute NewState (Publisher - SmartContract - Price - Time - PrevState - DCoin)
				MyTX = Publisher + SmartContract + Price + Time + PrevState + DCoin
				NewState = hashlib.sha256(MyTX.encode()).hexdigest().upper()

				os.system("mysql -u grafanaReader -D pyWALLANCE -e \"DELETE FROM WALLET WHERE PUBLISHER='" + Publisher + "'; INSERT INTO WALLET (PUBLISHER,COUNTER,STATE) VALUES ('" + Publisher + "', " + DCoin + "*" + str(Node.DCoinRate) + ", '" + NewState + "');\"")

				# Execute SmartContract (DEMO ONLY)
				os.system("/usr/bin/firefox -new-tab file:$HOME/WallanceProject/Wallance/SmartContract/Nespresso_2/Nespresso_2.png &")


	########################
	# INTERFACE START NODE #
	########################
	def StartNode(self):
		os.system("for ip in $(sudo nmap -sn $(ip -o -f inet addr show | awk '{print $4}' | grep '192') | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print \" => \"$3;}' | grep \"B8:27:EB\" | awk '{print $1}'); \
				   do \
				   echo '********** Start Node $ip **********'; \
				   ssh pi@$ip 'sudo service pyWallanceNode start' >> /dev/null & \
				   done")


	###########################
	# INTERFACE START GRAFANA #
	###########################
	def StartGrafana(self):
		os.system("sudo service grafana-server restart")
		os.system("sudo service mysql restart")
		os.system("/usr/bin/firefox -new-tab http://localhost:3000/dashboard/script/pyWallance_Dashboard.js &")


	#######################
	# INTERFACE STOP NODE #
	#######################
	def StopNode(self):
		os.system("for ip in $(sudo nmap -sn $(ip -o -f inet addr show | awk '{print $4}' | grep '192') | awk '/Nmap scan report for/{printf $5;}/MAC Address:/{print \" => \"$3;}' | grep \"B8:27:EB\" | awk '{print $1}'); \
				   do \
				   echo '********** Stop Node $ip **********'; \
				   ssh pi@$ip 'sudo service pyWallanceNode stop' >> /dev/null & \
				   done")


	##################
	# INTERFACE STOP #
	##################
	def Stop(self, Signum, Frame):

		# Stop Nodes
		self.StopNode()

		# Stop all Sockets & Thread
		self.InterfaceRunning = False
		self.Receiver.join()

		# Clear pyWallance Database
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'DROP TABLE IF EXISTS SMARTCONTRACT;'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'DROP TABLE IF EXISTS WALLET;'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'DROP TABLE IF EXISTS REQUEST_TRANSACTIONS;'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'DROP TABLE IF EXISTS CONSENSUS_TRANSACTIONS;'")
		os.system("mysql -u grafanaReader -D pyWALLANCE -e 'DROP DATABASE IF EXISTS pyWALLANCE;'")

		# Shutdown Grafana
		os.system("killall -q firefox >> /dev/null")

		print("Interface Closed")




#############################################################
#						  MAIN PART 						#
#############################################################

if __name__== "__main__":

	# Init Interface
	MyInterface = Interface()

	# Main Loop
	while MyInterface.InterfaceRunning:

		# Compute Consensus Process
		Interface.ConsensusProcess()

		# Waiting Time
		time.sleep(Node.SamplingTime)

	print("End of Interface")
