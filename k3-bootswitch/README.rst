K3-bootswitch tool
==================

This tool allows to boot the J7-EVM in any boot mode from command line.
This is useful for controlling the board remotely for individual developers
as well as test farm.

Hardware setup
--------------

* Type-C cable should be connected from the board to the Linux PC
* UART cable should be connected from the main_uart to Linux PC
* Default switch settings should be for DFU boot mode
* SW8 = 1000 0000    SW9 = 0010 0000    SW3 = 0101 00 1010
* Power supply to the board should be connected via phidget USB relay

Usage
-----

* Install dfu-util package on the Linux PC with
    ``sudo apt-get install dfu-util``
* To boot the board in MMC bootmode, run following
    ``sudo ./dfu-util.sh --bootmode mmc``

  Currently supported bootmodes are: **mmc, emmc, ospi, uart, noboot**

* To mount the emmc from the board to the Linux PC, run following
    ``sudo ./dfu-util.sh --mount 0``
* To mount the SD card from the board to the Linux PC, run following
    ``sudo ./dfu-util.sh --mount 1``


Advantages
----------

* Allows to remotely control the board by eliminating need to physically
  change the switch settings
* Can be used for regular development flow, where it removes the need
  to physically plug out the SD card for updating images.
* Makes it very easy to partition, format and update contents of the
  eMMC device.
* Can be used for factory flashing of the OSPI/eMMC images using
  automated scripts

How it works
------------
The DFU bootmode allows to pass any custom bootloader to the board. By keeping
the switch settings in DFU mode, board always waits for the Linux PC to send
a bootloader. In J721E SoC, the BOOTMODE and MCU_BOOTMODE registers reflect the
values of the boot switches at the cold boot. This register can be modified and
the values written are retained through the warm reset. These two features
allows to set the bootmode from the command line PC tool.

In the **boot_select** directory of this tool, there are many files which act
as the custom bootloader every time the board boots with DFU-boot mode.
The custom bootloader does only two important things; First it overwrites the
BOOTMODE and MCU_BOOTMODE registers to change to the desired boot mode and then
it issues a soft reset to the SoC causing it to boot the second time with new
bootmode.

All of this happens very fast when run from a script that it does not add
considerable amount of time for developer bootflow.

The mount of SD card or eMMC is achieved using the u-boot's
UMS (USB Mass Storage) feature. In this case, the tool sends a real R5 u-boot as
bootloader, System firmware ITB, A72 u-boot images and then runs the ums command.
Note that all the binaries are being sent from the Linux PC, so there is
absolutely no dependency on the contents of SD card.


Customization
-------------

Default setup assumes most common setup for J7EVM. In case you are using
differnent mechanism, update the **dfu-boot.sh** script with following:

* Update the **uart_dev** variable to reflect the correct tty device
  for main uart. (The one where all u-boot/SBL/kernel logs appear)
* Update the function **toggle_power** to use your custom method to toggle_power
  remote power switch instead of the default phidget commands



Limitatinos
-----------

* Do not use this mechanism to measure any boot time numbers
* The bootloader images are specific to TI J7 EVM. Different images are required
  to be able to mount the SD/eMMC from custom boards

