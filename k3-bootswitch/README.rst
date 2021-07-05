K3-bootswitch tool
==================

This tool allows to boot the board in any boot mode from command line.
This is useful for controlling the board remotely for individual developers
as well as test farm.

Hardware setup
--------------

* USB cable should be connected from the board to the Linux PC
* Note that on am65xx-evm, there is an adapter board for PCIe / USB.
  This should be used for connecting the USB cable.
  DFU boot is only supported from this port.
* UART cable should be connected from the main_uart to Linux PC
* Default switch settings should be for DFU boot mode
* Power supply to the board should be connected via phidget USB relay


Switch settings for DFU boot mode
---------------------------------

* j721e-evm settings  => SW8 = 1000 0000      SW9 = 0010 0000      SW3 = 0101 00 1010
* j7200-evm settings  => SW8 = 1000 0000      SW9 = 0010 0000      SW3 = 0101 00 1010
* am65xx-evm settings => SW2 = 0000 0000 00   SW3 = 0001 0000 00   SW4 = 11
* am64xx-evm settings => SW2 = 1100 1010      SW3 = 0011 0000

Phidget setup
-------------

This script uses phidget to control power for restarting the boards.
Since everyone has different configuration, the script parses the data from a
config file. You can copy the template as follows and then customize as required.

    cp k3bootswitch.conf ~/HOME/.config/

Usage
-----

* Install dfu-util package on the Linux PC with
    ``sudo apt-get install dfu-util``
* To boot the j721e-evm board in MMC bootmode, run following
    ``sudo ./dfu-boot.sh --j721e-evm --bootmode mmc``

  Currently supported bootmodes are: **mmc, emmc, ospi, uart, noboot**

* To mount the emmc from j721e-evm board to the Linux PC, run following
    ``sudo ./dfu-boot.sh --j721e-evm --mount 0``
* To mount the SD card from am65xx-evm board to the Linux PC, run following
    ``sudo ./dfu-boot.sh --am65xx-evm --mount 1``

Customization
-------------

Default setup assumes most common setup for Keystone3 EVM. In case you are using
differnent mechanism, update the **dfu-boot.sh** script with following:

* Update the **uart_dev** variable to reflect the correct tty device
  for main uart. (The one where all u-boot/SBL/kernel logs appear)
* Update the **switch** variable to reflect the correct switch number  which
  controls the power via phidget
* If you have a different mechanism to power the board, write your own implementation
  for **toggle_power** function instead of the default phidget commands

Limitatinos
-----------

* Do not use this mechanism to measure any boot time numbers
* The bootloader images are specific to TI EVMs. Different images are required
  to be able to mount the SD/eMMC from custom boards
* The u-boot will try to import the environment from eMMC. If that is broken,
  it will cause issues in mounting the devices using UMS
