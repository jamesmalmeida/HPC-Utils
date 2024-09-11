apt -y install libmunge-dev libmunge2 munge
scp work0:/etc/munge/munge.key /etc/munge/.
chown munge:munge /etc/munge/munge.key
chmod 400 /etc/munge/munge.key

systemctl restart munge

munge -n | unmunge | grep STATUS
munge -n | ssh work0 unmunge | grep STATUS

