# PiHub
The intention of this repository is to run a Raspberry Pi as a Jupyterhub.  
This setup provides so called classrooms, where students can connect to a wireless access point, spawned by the Pi.  
Therefore the integrated wireless card is set in access point mode.  
There's also a GUI implemented to manage the containers easier.
For further informations around different Jupyterhub setups, check out this repository <https://github.com/Energy23/JupyterHub>
## Setup
Rasbian is recommended as OS!  
**There will be a script doing all these things for you, but it's still in testing** 

### Install Docker 
First you have to install Docker on your Raspberry Pi:  
````bash
curl -fsSL https://get.docker.com -o get-docker.sh
````
Then add the current user (Pi) to Docker group, so that you're able to work with Docker as non-root user
````bash
sudo usermod -aG docker Pi
````

### Setup Pi as Access Point
Now you're already set for making your Raspberry Pi an access point.  
Therefore you need the packages ...
+ hostapd to manage your access point settings like encryption, password and frequency.    
+ dnsmasq to do your DHCP management for the users connecting to the access point.  
+ iptables to bridge your ethernet controller with wireless lan, so that the users are also connected to the internet.  
Install Packages:  
````bash
sudo apt install dnsmasq hostapd
````

### Build your Classroom container


## To-Do

