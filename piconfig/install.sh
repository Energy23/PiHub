#!/bin/bash
sudo apt install -y hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo apt install -y dnsmasq
sudo apt install -y netfilter-persistent iptables-persistent
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
sudo echo "interface wlan0" >> /etc/dhcpcd.conf
sudo echo "\tstatic ip_address=10.10.1.1/24" >> /etc/dhcpcd.conf
sudo echo "\tnohook wpa_supplicant" >> /etc/dhcpcd.conf
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo echo "interface=wlan0" >> /etc/dnsmasq.conf
sudo echo "dhcp-range=10.10.0.2,10.10.0.100,255.255.255.0,24h" >> /etc/dnsmasq.conf
sudo echo "domain=wlan" >> /etc/dnsmasq.conf
sudo echo "address=/pi.lan/10.10.0.1" >> /etc/dnsmasq.conf
sudo rfkill unblock wlan:
sudo cp hostapd.conf /etc/hostapd/hostapd.conf
