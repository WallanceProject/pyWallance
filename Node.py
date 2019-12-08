
# pyWallance Node
# Command: python3 Node.py

import os
import time
import socket
import struct
import select
import signal
import hashlib
import itertools
import threading
from random import randrange
from collections import Counter

from Sensor import *


#############################################################
#						 NODE CLASS 						#
#############################################################


class Node():


	###################
	# NODE PARAMETERS #
	###################
	ConsensusMulticastIP = "224.168.0.1"
	ConsensusMulticastPort = 10000
	DataDelimiter = "_"

	MajorityThreshold = 2.0/3.0		# Must be > 1/2
	Difficulty = 1 					# Number of nipples set to '0' at the beginning of Hash
	DCoinRate = 5 					# Number of shared Sensor value for 1 DCoin (WARNING: CHANGE INTO pyWallance.js file and copy update pyWallance.js to /usr/share/grafana/public/dashboards/)
	DCoinReward	= 2 				# Number of Sub-division of DCoin for the participation of Consensus
	GenesisState = "0000000000000000000000000000000000000000000000000000000000000000"
	TransactionOutdate = 5			# Number of Request Transaction of Publisher before removing its old Consensus Transaction
	SamplingTime = 2				# Time between consecutive epochs (in second)

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


	#######################
	# NODE INITIALIZATION #
	#######################
	def __init__(self):

		# Consensus Data
		self.Wallet = {}				# NodeID: (Counter, State)
		self.RequestTransaction = []	# Publisher ID, SmartContract ID, Price, Time, PrevState, Outdate
		self.ConsensusTransaction = []	# SubscriberID, Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin, Outdate

		# Consensus Data Lockers
		self.WalletLock = threading.RLock()
		self.RequestTransactionLock = threading.RLock()
		self.ConsensusTransactionLock = threading.RLock()
		
		# Consensus TX
		self.TX = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TX.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
		self.TX.connect((Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))

		self.NodeRunning = True

		# Start Consensus Receiver Thread
		self.Receiver = threading.Thread(target=self.ReceiverThread)
		self.Receiver.start()

		# Start Sensor TX Thread
		self.MySensor = Sensor()
		self.MySensorTX = threading.Thread(target=self.MySensor.SensorLoop)
		self.MySensorTX.start()	

		# Set SIGTERM signal catcher (Service Stop)
		signal.signal(signal.SIGTERM, self.Stop)


	########################
	# NODE RECEIVER THREAD #
	########################
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
		while self.NodeRunning:
			
			try:
				ready_socks,_,_ = select.select(RXSocket, [], [], 0)

				for sock in ready_socks:
					PeerData, PeerAddr = sock.recvfrom(1024)

					# Parse Data
					self.ParseData(sock.getsockname()[0], PeerData)

				# -- Print Part -- #
				with self.WalletLock:
					print("\n-------------------")
					print("Wallet:")
					print("\n".join("{}: {}".format(i,j) for i,j in sorted(self.Wallet.items())))

				with self.RequestTransactionLock:
					print("\nRequest Transaction:")
					print("\n".join("{}".format(i) for i in self.RequestTransaction))

				with self.ConsensusTransactionLock:
					print("\nConsensus Transaction:")
					print("\n".join("{}".format(i) for i in self.ConsensusTransaction))
					print("-------------------\n")
	
			except:
				pass

			# Waiting Time Loop
			time.sleep(Node.SamplingTime)

		RXSocket[0].close()
		RXSocket[1].close()
		print("Close Receiver %s:%s" % (Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))
		print("Close Receiver %s:%s" % (Sensor.MulticastIP, Sensor.MulticastPort))


	###################################
	# NODE SEND CONSENSUS TRANSACTION #
	###################################
	def SendConsensusTransaction(self, Transaction):
		
		# Format Consensus Transaction
		ConsTX = ""
		for i in Transaction[0:len(Transaction)-1]:
			ConsTX += str(i) + Node.DataDelimiter
		ConsTX += Transaction[len(Transaction)-1]

		self.TX.sendto(ConsTX.encode("utf8"), (Node.ConsensusMulticastIP, Node.ConsensusMulticastPort))


	###################
	# NODE PARSE DATA #
	###################
	def ParseData(self, Topic, Data):

		# Sensor Topic
		if Topic == Sensor.MulticastIP:
			self.UpdateWalletCounter(Data.decode("utf8").split(Sensor.DataDelimiter))

		elif Topic == Node.ConsensusMulticastIP:
			self.AddTransaction(Data.decode("utf8").split(Node.DataDelimiter))

		else:
			print("Error Topic")


	##############################
	# NODE UPDATE WALLET COUNTER #
	##############################
	def UpdateWalletCounter(self, Data):

		# Sensor Transaction:
		# [0]: Publisher ID
		# [1]: Topic Name ("SENSOR")
		# [2]: Value

		with self.WalletLock:
			try:
				self.Wallet[Data[0]] = (self.Wallet[Data[0]][0]+1, self.Wallet[Data[0]][1])
			except KeyError:
				self.Wallet[Data[0]] = (1, Node.GenesisState)


	###################
	# NODE VALID HASH #
	###################
	def ValidHash(Hash):

		for i in range (0, Node.Difficulty):
			if Hash[i] != '0':
				return -1
		return 0


	##########################
	# NODE COMPUTE LIGHT POW #
	##########################
	def ComputeLightPoW(Transaction):

		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce

		Nonce = 0

		while True:
			MyTX = Transaction[0] + Transaction[1] + Transaction[2] + str(Transaction[3]) + str(Transaction[4]) + Transaction[5] + str(Transaction[6]) + str(Nonce)
			MyHash = hashlib.sha256(MyTX.encode()).hexdigest().upper()

			if Node.ValidHash(MyHash) == 0:
				return Nonce
			else:
				Nonce += 1


	########################
	# NODE CHECK LIGHT POW #
	########################
	def CheckLightPoW(Transaction):

		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce
		MyHash = Transaction[0] + Transaction[1] + Transaction[2] + str(Transaction[3]) + str(Transaction[4]) + Transaction[5] + str(Transaction[6]) + str(Transaction[7])
		MyHash = hashlib.sha256( MyHash.encode()).hexdigest().upper()
		return Node.ValidHash(MyHash)


	############################
	# NODE CHECK SMARTCONTRACT #
	############################
	def CheckSmartContract(SmartContract, Price):
		return os.path.exists("SmartContract/" + SmartContract + "_" + str(Price) + "/" + SmartContract + "_" + str(Price) + ".py")


	########################
	# NODE ADD TRANSACTION #
	########################
	def AddTransaction(self, Transaction):

		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce

		# Request Transaction List:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, Outdate

		# Consensus Transaction List:
		# Subscriber ID, Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin, Outdate

		# Check Light PoW && Existing SmartContract
		if (Node.CheckLightPoW(Transaction) == 0) and (Node.CheckSmartContract(Transaction[2], Transaction[3]) == True):

			# New Request Transaction
			if Transaction[0] == Transaction[1]:

				# Manage Consensus Transaction
				with self.RequestTransactionLock, self.ConsensusTransactionLock:
					Outdated = []

					# Decrement Outdate value of Consensus Transaction of Requester
					for idx, ConsTX in enumerate(self.ConsensusTransaction):
						if Transaction[1] == ConsTX[1]:
							if self.ConsensusTransaction[idx][7] == 0:
								Outdated.append(idx)

							self.ConsensusTransaction[idx][7] -= 1

					# Remove Outdated Consensus Transaction of Requester
					for idx in reversed(Outdated):
						del self.ConsensusTransaction[idx]

					Outdated = []

					# Decrement Outdate value of Request Transaction of Requester
					for idx, ReqTX in enumerate(self.RequestTransaction):
						if Transaction[1] == ReqTX[0]:
							if self.RequestTransaction[idx][5] == 0:
								Outdated.append(idx)

							self.RequestTransaction[idx][5] -= 1

					# Remove Outdated Request Transaction of Requester
					for idx in reversed(Outdated):
						del self.RequestTransaction[idx]

					# Check if already Request Transaction with same (Publisher, State) pair
					ToAdd = True
					for ReqTX in self.RequestTransaction:
						if (ReqTX[0] == Transaction[1]) and (ReqTX[4] == Transaction[5]):
							ToAdd = False
							break

					# Add Request Transaction
					if ToAdd == True:
						self.RequestTransaction.append(Transaction[1:6] + [Node.TransactionOutdate])

			# New Consensus Transaction
			else:
				with self.ConsensusTransactionLock:
					self.ConsensusTransaction.append(Transaction[0:7] + [Node.TransactionOutdate])
		else:
			print("Error Transaction")


	#################################
	# NODE FIND REQUEST TRANSACTION #
	#################################
	def FindRequestTransaction(self):

		# Wallet:
		# NodeID: (Counter, State)

		# Request Transaction List:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, Outdate

		with self.WalletLock, self.RequestTransactionLock:
			for idx, ReqTX in enumerate(self.RequestTransaction):
				try:
					if (float(ReqTX[2]) <= (self.Wallet[ReqTX[0]][0] / Node.DCoinRate)) and (ReqTX[4] == self.Wallet[ReqTX[0]][1]):

						# Remove Request Transaction
						del self.RequestTransaction[idx]
						return ReqTX
				except:
					pass

			return []


	#######################################
	# NODE GENERATE CONSENSUS TRANSACTION #
	#######################################
	def GenerateConsensusTransaction(self):

		# Transaction (Request/Consensus):
		# [0]: Subscriber ID
		# [1]: Publisher ID
		# [2]: SmartContract ID
		# [3]: Price
		# [4]: Time
		# [5]: Previous State
		# [6]: DCoin
		# [7]: Nonce

		# Wallet:
		# NodeID: (Counter, State)

		# Request Transaction List:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, Outdate

		# Consensus Transaction List:
		# Subscriber ID, Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin, Outdate

		# Find Request Transaction
		MyReqTX = self.FindRequestTransaction()

		if len(MyReqTX) != 0:

			# Avoid Sender of Request Transaction send Consensus Transaction
			if MyReqTX[0] != self.TX.getsockname()[0][10:]:

				# Set Subscriber ID
				MyConsTX = [self.TX.getsockname()[0][10:]]

				# Add Request Transaction info
				MyConsTX = MyConsTX + MyReqTX[0:len(MyReqTX)-1]

				# Add New DCoin value
				MyConsTX.append( str((self.Wallet[MyReqTX[0]][0] - (float(MyReqTX[2])*Node.DCoinRate))/Node.DCoinRate) )

				# Compute Light PoW (set Nonce value)
				MyConsTX.append( str(Node.ComputeLightPoW(MyConsTX)) )
				return MyConsTX

			else:
				return []
		else:
			return []


	######################
	# NODE FIND MAJORITY #
	######################
	def FindMajority(self):

		# Wallet:
		# NodeID: (Counter, State)

		# Consensus Transaction List:
		# Subscriber ID, Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin, Outdate

		# Majority Group:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin

		# Remove doublons (Multiple Subscriber's votes)
		with self.WalletLock, self.ConsensusTransactionLock:
			self.ConsensusTransaction.sort()
			self.ConsensusTransaction = list(self.ConsensusTransaction for self.ConsensusTransaction,_ in itertools.groupby(self.ConsensusTransaction))

			# Recover Groups of Consensus Transaction with correct PrevState
			Groups = Counter(tuple(item[1:7]) for item in self.ConsensusTransaction if item[5] == self.Wallet[item[1]][1])

			# Recover Network Size
			NetworkSize = len(self.Wallet)

			# Find Majority Groups
			for i in Groups:
				if Groups[i] >= Node.MajorityThreshold * NetworkSize:
					return list(i)

			# No Majority
			return []


	######################
	# NODE UPDATE WALLET #
	######################
	def UpdateWallet(self, MajorityGroup):

		# MajorityGroup:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin

		# Format MajorityGroup Entries
		MyTX = MajorityGroup[0] + MajorityGroup[1] + str(MajorityGroup[2]) + str(MajorityGroup[3]) + MajorityGroup[4] + str(MajorityGroup[5])
		NewState = hashlib.sha256(MyTX.encode()).hexdigest().upper()

		with self.WalletLock:
			self.Wallet[MajorityGroup[0]] = ( (MajorityGroup[5]*Node.DCoinRate), NewState)


	############################
	# NODE START SMARTCONTRACT #
	############################
	def StartSmartContract(self, SmartContract, Price):
		os.system("python3 SmartContract/" + SmartContract + "_" + Price + "/" + SmartContract + "_" + Price + ".py &")


	##########################
	# NODE CONSENSUS PROCESS #
	##########################
	def ConsensusProcess(self):

		# Wallet:
		# NodeID: (Counter, State)

		# Request Transaction List:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, Outdate

		# Consensus Transaction List:
		# Subscriber ID, Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin, Outdate

		# Find Majority Group:
		# Publisher ID, SmartContract ID, Price, Time, PrevState, DCoin
		MyConsGroup = self.FindMajority()

		if len(MyConsGroup) != 0:

			# Reward Participants
			with self.WalletLock, self.ConsensusTransactionLock, self.RequestTransactionLock:
				Subscribers = {i[0] for i in self.ConsensusTransaction if i[1:7] == MyConsGroup}
				
				for i in Subscribers:
					self.Wallet[i] = (self.Wallet[i][0]+Node.DCoinReward, self.Wallet[i][1])

				# Remove used Consensus Transaction (with old PrevState)
				Outdated = []
				for idx, ConsTX in enumerate(self.ConsensusTransaction):
					if (MyConsGroup[0] == ConsTX[1]) and (MyConsGroup[4] == ConsTX[5]):
						Outdated.append(idx)

				# Remove selected Consensus Transaction of Requester
				for idx in reversed(Outdated):
					del self.ConsensusTransaction[idx]

				# Remove Request Transaction not used yet (with old PrevState)
				Outdated = []
				for idx, ReqTX in enumerate(self.RequestTransaction):
					if (MyConsGroup[0] == ReqTX[0]) and (MyConsGroup[4] == ReqTX[4]):
						Outdated.append(idx)

				# Remove selected Request Transaction of Requester
				for idx in reversed(Outdated):
					del self.RequestTransaction[idx]

				# Update Wallet of Publisher after Majority
				self.UpdateWallet(MyConsGroup)

			# Start SmartContract
			if (self.TX.getsockname()[0][10:] == MyConsGroup[0]):
				self.StartSmartContract(MyConsGroup[1], MyConsGroup[2])

			# For Next Majority
			return 0

		# No Majority
		else:
			return -1


	#############
	# NODE STOP #
	#############
	def Stop(self, Signum, Frame):

		# Stop all Sockets & Thread
		self.NodeRunning = False
		self.MySensor.SensorRunning = False
		self.TX.close()
		self.Receiver.join()
		self.MySensorTX.join()
		print("Node Closed")




#############################################################
#						  MAIN PART 						#
#############################################################

if __name__== "__main__":

	# Init Node (+ Sensor)
	MyNode = Node()

	# Main Loop
	while MyNode.NodeRunning:

		# Send Consensus Transaction
		while True:
			MyTX = []
			MyTX = MyNode.GenerateConsensusTransaction()

			if len(MyTX) == 0:
				break
			else:
				MyNode.SendConsensusTransaction(MyTX)

		# Compute Consensus Process
		while True:
			if MyNode.ConsensusProcess() == -1:
				break;

		# Waiting Time
		time.sleep(Node.SamplingTime)

	print("End of Node")