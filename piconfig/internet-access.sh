#!/bin/bash
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
line=awk '/exit 0/{ print NR; exit }' /etc/rc.local
let "line -= 1"
mv /etc/rc.local /etc/rc.local.old
awk -v l="$line" 'NR==l{print "iptables-restore < /etc/iptables.ipv4.nat"}1' /etc/rc.local.old > /etc/rc.local