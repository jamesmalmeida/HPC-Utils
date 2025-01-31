#!/bin/bash

jobs=$(squeue --states=running | grep [0-9] | awk '{print $1}')

for job in $jobs;do
	node=$(squeue -o "%.18R" --job $job | tail -n 1 | xargs)
	user=$(squeue -o "%.30u" --job $job | tail -n 1)
	cpus=$(squeue -o "%.3C" --job $job  | tail -n 1)
	used_cpu=$(pdsh -w $node "ps -U $user -o user,pcpu | grep [0-9] | awk  '{sum=sum+\$2}END{print sum}'" | awk '{print $NF/100}')
	cpu_usage=$(awk "BEGIN {print $used_cpu/$cpus}")
	echo JOB NUMBER $job OF USER $user IS RUNNING ON NODE $node WITH $cpus CPUS, the CPU usage is $cpu_usage
	if [ "$node" = "work1" ] || [ "$node" = "work2" ] || [ "$node" = "work7" ] || [ "$node" = "work8" ] ; then
		pids=$(pdsh -w $node "ps -U $user -o pid | grep [0-9]" | awk '{print $2}')
		for pid in $pids;do
			#echo "  checking if process $pid of user $user is running at any GPU"
			used_gpu=$(pdsh -w $node "nvidia-smi" | grep $pid | awk '{print $3}' | tr '\n' ' ')
			if [ ! -z "${used_gpu}" ]; then
				#echo "		$pid seem to be running at GPU $used_gpu"
				for gpu in $used_gpu;do
					#echo "			Checking GPU $gpu"
					gpu_usage=$(pdsh -w $node "nvidia-smi" | grep -A1 "$gpu  NVIDIA" | tail -n1 | awk '{print $14}')
					echo "		job $job is using $gpu_usage of the GPU $gpu"
				done
			#else
				#echo "		it is not running at any GPUs"
			fi
		done
	fi
done
