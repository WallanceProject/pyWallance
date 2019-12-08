import os
import time

#############################################################
#					NESPRESSO SMARTCONTRACT 				#
#############################################################

print("Connection with Nespresso Machine");
os.system("sudo systemctl restart bluetooth.service");
time.sleep(1);
os.system("gatttool -t random -b D7:EB:B1:24:F1:43 --char-write-req --handle=0x0014 --value=85e6ba6a25c834c6; sleep 1; gatttool -t random -b D7:EB:B1:24:F1:43 --char-write-req --handle=0x0024 --value=03050704000000000000;");
print("By Nespresso_2");