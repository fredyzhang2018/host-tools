#!/bin/bash
# Utility script to select the bootmode from command line
# Author: Nikhil Devshatwar

SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`
prefix=$SCRIPTPATH/bin
boot_select=$SCRIPTPATH/boot_select
user=`logname`

UMS_part1=/dev/disk/by-id/usb-Linux_UMS_disk*part1
UMS_part2=/dev/disk/by-id/usb-Linux_UMS_disk*part2

# Customize this as required
uart_dev=/dev/ttyUSB0
dev=1

usage()
{
	echo "Usage:"
	echo "  dfu-boot.sh - Utility script to select bootmode and mount MMC to PC"
	echo "  sudo ./dfu-boot.sh --mount DEV"
	echo "      DEV: 1 for MMC, 0 for eMMC"
	echo "  sudo ./dfu-boot.sh --bootmode MODE"
	echo "      MODE: " `ls $boot_select/spl* | awk -F"." 'BEGIN{ORS=" "} { print $2 }'`
}

# Bootloader takes time to initialize
# wait till then
wait_till_ready() {
msg=$1
	for i in `seq 30`; do
		dfu-util -l | grep "Found DFU" >/dev/null 2>&1
		if [ $? -eq "0" ]; then
			>&2 echo "    >>>> dfu ready $msg after $i tries"
			return
		fi
		sleep 0.2
	done
	>&2 echo "    >>>> ERROR: Timeout waiting for dfu"
	>&2 echo "    >>>>        Make sure to connect Type-C cable to EVM and host machine"
	>&2 echo "    >>>>        Bootswitch settings fot DFU boot:"
	>&2 echo "    SW8 = 1000 0000    SW9 = 0010 0000    SW3 = 0101 00 1010"
	exit 1
}

# Use dfu to send all bootloaders till you get to the
# A72 u-boot prompt
boot_till_uboot() {
	wait_till_ready "for tiboot3.bin"
	2>&1 dfu-util -R -a bootloader -D $prefix/tiboot3.bin
	wait_till_ready "for sysfw.itb"
	2>&1 dfu-util -R -a sysfw.itb -D $prefix/sysfw.itb
	wait_till_ready "for tispl.bin"
	2>&1 dfu-util -R -a tispl.bin -D $prefix/tispl.bin
	wait_till_ready "for u-boot.img"
	2>&1 dfu-util -R -a u-boot.img -D $prefix/u-boot.img
}

# Detect and mount the partitions
try_mount() {
	for i in `seq 1 100`; do
		echo "ums 0 mmc $1" > $uart_dev
		sleep 0.1
		if [ -b $UMS_part1 ] && [ -b $UMS_part2 ]; then
			mkdir -p /media/$user/UMS-boot
			mkdir -p /media/$user/UMS-rootfs
			mount $UMS_part1 /media/$user/UMS-boot
			mount $UMS_part2 /media/$user/UMS-rootfs
			echo "    >>>> Mounted partions at /media/$user/UMS-boot and /media/$user/UMS-rootfs"
			return
		fi
	done
	>&2 echo "    >>>> ERROR: Could not find partitions $UMS_part1"
	exit 1
}

toggle_power()
{
	echo "    >>>> Toggling phidget..."
	(phidget-switch 0 0 && sleep 0.5 && phidget-switch 0 1 && sleep 0.1) >/dev/null 2>&1
	if [ $? -ne 0 ]; then
		echo -n "ERROR: phidget not found, Reboot manually and press enter.. "
		read DUMMY
	fi
}

# Main script starts from here
if [ `whoami` != "root" ]; then
	echo "This script should be called with sudo!!"
	usage
	exit 1
fi

if [ "$1" = "--mount" ]; then
	if [ ! -z "$2" ]; then
		dev=$2
	fi
	toggle_power
	boot_till_uboot >/dev/null
	try_mount $dev
elif [ "$1" = "--bootmode" ]; then
	if [ ! -z "$2" ]; then
		bootmode=$2
	fi
	if [ ! -f $boot_select/spl.$bootmode ]; then
		echo "Invalid bootmode $bootmode"
		usage
		exit 2
	fi

	toggle_power
	wait_till_ready
	echo "    >>>> Selecting bootmode: $bootmode"
	dfu-util -R -a bootloader -D $boot_select/spl.$bootmode >/dev/null 2>&1
	if [ $? -eq 0 ]; then
		echo "    >>>> SUCCESS"
	else
		echo "    >>>> FAILED"
	fi
else
	echo " Invalid usage"
	usage
fi
