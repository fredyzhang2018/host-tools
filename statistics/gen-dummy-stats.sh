#!/bin/bash

cpuload() {
	while true
	do
		#echo "WS-cpuload: 1 RANDOM "`shuf -i 1-100 -n 1`
		echo "WS-cpuload: 4 R50" `shuf -i 1-15 -n 1` "C6x" `shuf -i 10-45 -n 1` "A72" `shuf -i 9-42 -n 1` "GPU" `shuf -i 33-82 -n 1`
		sleep 0.4
	done
}

ddrbw() {
	while true
	do
		echo "WS-ddrbw: 4 Read_avg" `shuf -i 900-1300 -n 1` "Write_avg" `shuf -i 1500-1800 -n 1` "Read_peak" `shuf -i 2100-2200 -n 1` "Write_peak" `shuf -i 2700-2800 -n 1`
		sleep 0.4
	done
}

cluster-fps() {

	while true
	do
		echo "WS-cluster-fps:" `shuf -i 45-60 -n 1`
		sleep 0.4
	done
}

cpuload &
ddrbw &
cluster-fps &
