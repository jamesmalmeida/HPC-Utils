# HPC-Utils

Starting a repository for HPC utilities and scripts.

* espresso-forces: Bash script to check for the highest force on Quantum Espresso relaxation. Takes into account fixed atoms, discarting their forces. The fixed atoms need to be specified with the sting "0 0 0", just one space between the zeros.
** espresso-forces-last: The same as before, but prints only the last force.
** espresso-forces-last-3: The same as before, but prints only the last three forces.
* espresso-iteration-times: Prints the iteration times for each SCF step, by getting the difference between the cpu time of the steps.
* resources: Bash script to show which nodes are allocated, and how many cores are available on each node. Works with slurm job scheduler.
