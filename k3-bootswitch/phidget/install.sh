#!/bin/bash -e
topdir=`git rev-parse --show-toplevel`
sudo cp -r $topdir/phidget/* /
