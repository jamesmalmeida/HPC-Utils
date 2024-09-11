#!/bin/bash

wget https://download.schedmd.com/slurm/slurm-23.02.4.tar.bz2
bunzip2 slurm-23.02.4.tar.bz2
tar -xvf slurm-23.02.4.tar
cd slurm-23.02.4

mkdir -p /etc/slurm
./configure --with-hdf5=no -sysconfdir=/etc/slurm
make -j8
make install

useradd slurm
usermod -u 997 slurm
groupmod -g 997 slurm
mkdir -p /etc/slurm  /var/spool/slurmctld /var/spool/slurmd /var/log/slurm
chown slurm /var/spool/slurmctld /var/spool/slurmd /var/log/slurm

cp etc/slurmd.service /etc/systemd/system/.
systemctl enable slurmd

apt -y install pdsh

