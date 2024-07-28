nodes=$(scontrol show node | grep 'NodeName' | awk '{print $1}' | cut -d'=' -f2)
echo $nodes

nodes_pdsh=$(echo $nodes | sed 's/ /,/g')
pdcp -w $nodes_pdsh /etc/slurm/slurm.conf /etc/slurm/slurm.conf
pdsh -w $nodes_pdsh "service slurmd restart"

service slurmdbd restart
service slurmctld restart
