#!/bin/bash
sudo apt install -y hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo apt install -y dnsmasq
sudo apt install -y netfilter-persistent iptables-persistent
dhcpd = /etc/dhcpcd.conf.orig
if [ ! -f "$dhcpcd" ]; then
    sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
fi
sudo echo "interface wlan0" >> /etc/dhcpcd.conf
sudo echo "\tstatic ip_address=10.10.1.1/24" >> /etc/dhcpcd.conf
sudo echo "\tnohook wpa_supplicant" >> /etc/dhcpcd.conf
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo echo "interface=wlan0" >> /etc/dnsmasq.conf
sudo echo "dhcp-range=10.10.0.2,10.10.0.100,255.255.255.0,24h" >> /etc/dnsmasq.conf
sudo echo "domain=wlan" >> /etc/dnsmasq.conf
sudo echo "address=/pi.lan/10.10.1.1" >> /etc/dnsmasq.conf
sudo rfkill unblock wlan
sudo cp hostapd.conf /etc/hostapd/hostapd.conf
## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker Pi
## Build Container
cd ../docker/IDE/ && docker build -t classroom/ide:0.1 .
cd ../../docker/NBGrader/ && docker build -t classroom/nbgrader:0.1 .
cd ../../
## Install Packages for PiHub Management Tool
sudo apt-get install -y python3-pip
python3 -m pip install tk docker pyhostapdconf numpy
echo "Wollen Sie den Ethernet Port als Internetzugang nutzen? (Y/N)"
read net -n 1
if [[$net = "Y"]] || [[$net = "Y"]]
then sudo sh install.sh
fi
echo "Das System muss neu gestartet werden."
sudo reboot now
