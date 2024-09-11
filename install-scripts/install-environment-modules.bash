#!/bin/bash

apt -y install curl tcl-dev tk-dev

curl -LJO https://github.com/cea-hpc/modules/releases/download/v5.3.1/modules-5.3.1.tar.gz
tar -xvzf modules-5.3.1.tar.gz
cd modules-5.3.1

./configure –prefix=/opt/modules –modulefilesdir=/opt/modulefiles
make
make install

ln -s /opt/modules/init/profile.sh /etc/profile.d/modules.sh
ln -s /opt/modules/init/profile.csh /etc/profile.d/modules.csh
