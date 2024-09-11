apt -y install openssh-server

sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/g' /etc/ssh/sshd_config

systemctl restart ssh

mkdir -p /root/.ssh

scp 172.20.60.33:/root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

