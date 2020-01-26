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

*SYSFW-NAVSS-ResAssg.xlsx* is a simple Excel sheet which is easy to describe
the resource allocation across different hosts

*RM-autogen.py* is a python script useful for automatically generating
the Resource partitioning data for different software components.