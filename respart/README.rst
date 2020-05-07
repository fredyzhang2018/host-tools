Resource Partitioning Auto gen script
=====================================

When a system integrator has to combine multiple software components
into one system, one of the crucial aspect is managing global resources.

System firmware helps protect Navigator Subsystem resource across different
hosts using firewalls. For this, a  boardconfig needs to be passed to it
while booting up the system. The SDK comes with a default board cofig, which
caters to the SDK demos and applications.

However, for running customer applications, it will be necessary to modify
this boardconfig to suit the resource requirements of the desired applocation.
This host tool can is used for customizring the resource allocation
across different hosts in the system.

Typical RM board config file is described as an array of following data structure:

    {
        .start_resource = %d,
        .num_resource = %d,
        .type = RESASG_UTYPE (J721E_DEV_XXXX, RESASG_SUBTYPE_XXXXX),
        .host_id = HOST_ID_XXXXXXXX,
    }

*SYSFW-NAVSS-ResAssg.xlsx* is a simple Excel sheet which is easy to describe
the resource allocation across different hosts. Here, each cell represents
the count of resource (row) allocated to a host (col)

*RM-autogen.py* is a python script useful for automatically generating
the Resource partitioning data for different software components.

Setup
=====

* Install required packages by running `sudo apt-get install python-xlrd python-xlwt`
* Modify the excel sheet as per the usecase requirements
* Run the script `RM-autogen.py` to generate the entries for RM board config
* Update the board config data strucure `resasg_entries`
* Update the count of entries in board config data structure `resasg_entries_size`

Usage
=====

Use the --help option to get the latest information on the usage.

To generate the entries in the k3-image-gen boardconfig format, run following:

    ./RM-autogen.py -s j721e -o entries.txt -f boardcfg_kig SYSFW-NAVSS-ResAssg.xlsx

To generate the entries in RTOS sciclient boardconfig format, run following:

    ./RM-autogen.py -s j721e -o entries.txt -f boardcfg_sciclient SYSFW-NAVSS-ResAssg.xlsx

To print the assigned resource **per host_id**, use the --perhost option.
This is useful for syncing the PDK udma_rmcfg data structures easily

Use the **--share** option for sharing resources between two hosts.
This option will copy resource assignments of one host to other.
This is especially useful in case secure and non secure host_ids are
being used. e.g. u-boot uses secure host id for MCU_R5 and later the
SDK software uses non secure host_id

    # For J721E, use --share HOST_ID_MCU_0_R5_0 HOST_ID_MCU_0_R5_1
