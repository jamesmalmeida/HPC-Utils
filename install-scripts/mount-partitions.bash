#!/bin/bash

apt -y install nfs-common

echo "172.20.10.15:/home /home nfs nfsvers=3,nodev,nosuid 0 0" >> /etc/fstab
echo "172.20.60.33:/opt /opt nfs nfsvers=3,nodev,nosuid 0 0
" >> /etc/fstab

mount -a

df -h
