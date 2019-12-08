import time
import socket
import struct
from random import randrange


#############################################################
#						SENSOR CLASS 						#
#############################################################


class Sensor():


	#####################
	# SENSOR PARAMETERS #
	#####################
	MulticastIP = "224.168.0.2"
	MulticastPort = 10000
	DataDelimiter = "_"

	# Sensor Transaction:
	# [0]: Publisher ID
	# [1]: Topic Name ("SENSOR")
	# [2]: Value

	#########################
	# SENSOR INITIALIZATION #
	#########################
	def __init__(self):
		
		self.TX = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.TX.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
		self.TX.connect((Sensor.MulticastIP, Sensor.MulticastPort))
		self.MyID = self.TX.getsockname()[0][10:]

		self.SensorRunning = True


	##################
	# SENSOR TX LOOP #
	##################
	def SensorLoop(self):
		SensorData = 0

		while self.SensorRunning:
			SensorTransaction = self.MyID + Sensor.DataDelimiter + "SENSOR" + Sensor.DataDelimiter + str(SensorData)
			self.TX.sendto(SensorTransaction.encode("utf8"), (Sensor.MulticastIP, Sensor.MulticastPort))
			SensorData += 1
			time.sleep(randrange(1,10))

		self.TX.close()
		print("End of Sensor")