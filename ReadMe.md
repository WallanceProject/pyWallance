# Wallance, an Alternative to Blockchain for IoT (Tutorial)


## Introduction

We propose a lightweight alternative to blockchain, called *Wallance* to secure interactions in a decentralized IoT infrastructure. Taking into account all its constraints as memory, computing power and energy, our proof of concept promotes the sharing of data and the utilization of services as a real IoT network, in a secure way.

In this tutorial, we will install step by step *pyWallance* Node (on Raspberry Pi3 Model B+) and *pyWallance* User Interface (on PC) based on Grafana. A complete description of our protocol is available on our paper "*Wallance, an Alternative to Blockchain for IoT*". *pyWallance* is a python implementation of *Wallance* using standard socket library.
<br><br>


## Prerequisites

- A Linux environment
- At least 3 Raspberry Pi are required
- An internet connection is required
<br><br>


## Install *pyWallance*

Download and launch the installer *Install_pyWallance.sh*. In a terminal on your **PC**:
<pre><code>wget https://raw.githubusercontent.com/WallanceProject/pyWallance/master/Install_pyWallance.sh
chmod +x Install_pyWallance.sh
./Install_pyWallance.sh</code></pre>

At the end of the process, you should see the "WallanceProject" directory in your $HOME with the *pyWallance* directory, described below:
<br><br>
![](ReadMeImages/pyWallance.PNG)

| **File** | **Description** |
| :--------------: | :-----------: |
| Install_pyWallance.sh | Script to install *pyWallance* |
| Interface.py | Source code of *pyWallance* User Interface using Grafana (PC only) |
| Node.py | Source code of *pyWallance* Node (Raspberry only) |
| pyWallance_Dashboard.js | *pyWallance* User Interface Dashboard for Grafana (PC only) |
| pyWallance_DataSource.yaml | *pyWallance* User Interface Data Source for Grafana (PC only) |
| pyWallance_Node.service | *pyWallance* Node service launcher (Raspberry only) |
| pyWallance_Node.zip | *pyWallance* Node installer (Raspberry only) |
| pyWallance_RequestTransaction.desktop | Plug-in to generate Request Transaction from Grafana (PC only) |
| ReadMe.md | Readme of the *pyWallance* |
| Sensor.py | Source code of *pyWallance* Virtual Sensor (Raspberry only) |
| Shutdown_Node.sh | Script to shutdown *pyWallance* Node from PC (using SSH) |
| Update_Node.sh | Script to update *pyWallance* Node from PC , with the updated pyWallance_Node.zip(using SSH) |

| **Directory** | **Description** |
| :--------------: | :-----------: |
| ReadMeImages/ | Images of ReadMe.md file |
| SmartContract/ | Source codes of all Smart Contracts (Services) |

Note: the *pyWallance_Node.zip* archive contains all executables and libraries for the *pyWallanceDDS* Node version (Raspberry). **This archive must be copied on each Raspberry to be deployed on the network (see next section).**<br>

**WARNING: Before continuing, make sure your PC and Raspberry are on the same network.**
<br><br>


## Install *pyWallance* Node (Raspberry)

### Prerequisites

- Ensure an image of a Linux distribution is already available on Raspberry.<br>
- An internet connection is required
- For a best experience, copy your Public RSA key into each Raspberry to enable the automatic login through SSH

### Installation

In a terminal on your **PC**:
<pre><code>cd $HOME/WallanceProject/pyWallance
./Update_Node.sh</code></pre>

This command automatically install the *pyWallance* Node in the $HOME directory (typically */home/pi/*) in each connected Raspberry through SSH connection.<br>

At the end of the installation, the *pyWallance* directory in Raspberry is as follow:
<br><br>
![](ReadMeImages/RPI.PNG)

| **Directory/File** | **Description** |
| :--------------: | :-----------: |
| Node.py | Source code of *pyWallance* Node (Raspberry only) |
| Sensor.py | Source code of *pyWallance* Virtual Sensor (Raspberry only) |
| SmartContract/ | Source codes of all Smart Contracts (Services) |

<br>


## Run *pyWallance*

In a terminal on your **PC**:
<pre><code>cd $HOME/WallanceProject/pyWallance
./Run_Grafana_Interface.sh</code></pre>

This command start the *pyWallance* Node on each Raspberry and the *pyWallance* User Interface on PC. The Grafana dashboard is opened into a Firefox window. The first connection login is “admin” and the password is “admin”. You can change the password after logging in:
<br><br>
![](ReadMeImages/Grafana1.PNG)

Finally, the *pyWallance* User Interface is ready.
<br><br>
![](ReadMeImages/Grafana2.PNG)

(1): Select Node(s) to display<br>
(2): Information of Node (1 Node per Line)<br>
(3): Button to purchase a service<br>
(4): Node's purchase in process (*Request Transaction*)<br>
(5): Node's Wallet (*DCoin*)<br>
(6): List of available Smart Contracts (Services)<br>
(7): Select Smart Contract (Services) to purchase<br>
(8): *Consensus Transactions*<br>
<br>


## Utilization of *pyWallance* User Interface (PC)

On Grafana, a service can be purchase on behalf of a Raspberry, by clicking on the button "Buy Service" under the selected Raspberry. The service will be purchased only when the Raspberry will have enough DCoins.
<br><br>
![](ReadMeImages/GrafanaButton.PNG)

By default, the ID of each Raspberry is the last byte of the IP Address.<br>

Note: the list of Node is updated when the Raspberry sends data. Consequently, it can take time to display all Raspberry, according to their sending.<br>

During the first purchase, the pop-up window below appears. Firefox asks the permission to open the launcher of purchase application from Grafana.<br>
Select "Remember my choice for app links" and click on "Open link".
<br><br>
![](ReadMeImages/Grafana3.PNG)

Once a purchase is executed, a *Request Transaction* is generated and displayed on the User Interface in "Node x - *Request Transactions*" panel.<br>

After that, if all conditions are met, the other Nodes send their agreement thanks to a *Consensus Transaction*, displayed on "*Consensus Transactions*" panel.<br>

Below, an example of the interface, showing 'Node1' and 'Node2' with:<br>
- *Request Transaction* of Node1 (in "Node1 - *Request Transactions*" panel)<br>
- *Consensus Transaction* of Node 2 for the *Request Transaction* of Node1 (in "*Consensus Transactions*" panel)

![](ReadMeImages/Grafana4.PNG)

Finally, the consensus process is computed, the *Request Transaction* / *Consensus Transactions* are removed and wallets are updated.
<br><br>


## Stop *pyWallance*

Close the Firefox window.<br>
Stop the Run_Grafana_Interface instance in your PC with <Ctrl+C>.<br>
The *pyWallance* Node instance on each Raspberry will be stopped automatically (using SSH)
<br><br>


## *pyWallance* IDE

The *pyWallance* installation provides a complete Integrated Development Environment (IDE) of *pyWallance*.

The text editor *Sublime Text* is available to edit the *pyWallance* source codes.

In a terminal on your **PC**:
<pre><code>subl $HOME/WallanceProject/pyWallance</code></pre>

**If you edit the source code of *Node*, *Sensor* or *SmartContract*, the updated *pyWallanceDDS_Node.zip* archive must be copied to each Raspberry deployed on the network.**

### Update *pyWallance* Node (Raspberry)

In a terminal on your **PC**:
<pre><code>cd $HOME/WallanceProject/pyWallance/Update_Node.sh</code></pre>

This command updates the *pyWallanceNode.zip* archive with your modifications and updates all connected Raspberry with your modifications.
