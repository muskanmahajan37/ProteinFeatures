sed 's|-o |-o /n/groups/drad/I-TASSER4.3/BatchJobs/Final_Push/log_files/|' {} | sed 's|-e |-e /n/groups/drad/I-TASSER4.3/BatchJobs/Final_Push/log_files/|' | sed 's|main/|n/groups/drad/I-TASSER4.3/BatchJobs/Final_Push/main/|' | sed 's|js741|rlc18|' | sed 's|-/n/app/lmod/lmod/modulefiles/Core/java/jdk1.8.0_45 ||'