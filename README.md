# PiHub
The intention of this repository is to run a Raspberry Pi as a Jupyterhub.  
This setup provides so called classrooms, where students can connect to a wireless access point, spawned by the Pi.  
Therefore the integrated wireless card is set in access point mode.  
There's also a GUI implemented to manage the containers easier.
For further informations around different Jupyterhub setups, check out this repository <https://github.com/Energy23/JupyterHub>
## Setup
Rasbian is recommended as OS!  
**There will be a script doing all these things for you, but it's still in testing**
**If you don't want to use it, follow the instructions starting with Install Docker**
**Run the script with sudo privileges**
Install script is in the piconfig folder.
Run with:
````bash
sudo ./install.sh
````

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
sudo apt install -y dnsmasq hostapd netfilter-persistent iptables-persistent
````
Allow serices to run at startup
````bash
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
````
Backup your original dhcpd.conf
````bash
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
````
Add the followin lines to your /etc/dhcpcd.conf
````bash
interface wlan0
static ip_address=10.10.1.1/24
nohook wpa_supplicant
````
Backup your original dnsmasq.conf and add these lines
````bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
interface=wlan0
dhcp-range=10.10.0.2,10.10.0.100,255.255.255.0,24h
domain=wlan
address=/pi.lan/10.10.1.1
````

Unblock wlan for hostapd
````bash
sudo rfkill unblock wlan
````
Copy the hostapd.conf from this repo to /etc/hostapd/
````bash
sudo cp piconfig/hostapd.conf /etc/hostapd/hostapd.conf

````
### Route internet traffic
Please use the script internet-access.sh

### Build your Classroom container
Change into folder with Dockerfile inside:  
````bash
docker build -t jupyterhub/classroom:0.1 .
````
