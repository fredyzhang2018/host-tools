#!/usr/bin/python
import subprocess, time, os, sys
import argparse, string, re
import xlrd, xlwt
from xlwt.Utils import rowcol_to_cell

COL_COMMENT = 0
COL_RES_TYPE = 1
COL_SUB_TYPE = 2
COL_RES_FIELD = 3
COL_RES_COUNT = 5
COL_RES_START = 6
COL_HOST_START = 7

ROW_HOST_ID = 0
ROW_RES_START = 2

dict_dev = {}
dict_subtype = {}
dict_host = {}
utypes = []

def evalcmd(cmd):
	out = subprocess.check_output(cmd, shell=True).decode("utf-8")
	return out

def gen_soc_py_data(soc):
	output = '''%s

RESASG_TYPE_SHIFT = 6
RESASG_SUBTYPE_SHIFT = 0

const_values  = {
%s
%s
%s}'''
	header = "# %s.py - Auto generated SoC data\n" % soc
	devs = ""
	for i in dict_dev:
		devs += '"%s" : %d,\n' % (i, dict_dev[i])
	subtypes = ""
	for i in dict_subtype:
		subtypes += '"%s" : %d,\n' % (i, dict_subtype[i])
	hosts = ""
	for i in dict_host:
		hosts += '"%s" : %d,\n' % (i, dict_host[i])
	return output % (header, devs, subtypes, hosts)

def gen_rm_resasg_sheet(sheet):

	fmt_header = xlwt.easyxf('font: color-index blue, bold on')
	fmt_grayed = xlwt.easyxf('font: bold on; align: horiz center; pattern: pattern solid, fore-colour gray25')

	sheet.write(0, COL_RES_TYPE, "Type", fmt_header)
	sheet.write(0, COL_SUB_TYPE, "Subtype", fmt_header)
	sheet.write(0, COL_RES_COUNT, "Availalbe count", fmt_header)
	sheet.write(0, COL_RES_START, "start", fmt_header)
	col = COL_HOST_START
	for item in sorted(dict_host.items(), key=lambda x: x[1]):
		(host, host_id) = item
		sheet.write(0, col, host, fmt_header)
		if (host == "HOST_ID_ALL"):
			COL_BALANCE = col
		col = col + 1
	row = 1
	for entry in utypes:
		(dev, subtype, start, count) = entry
		sheet.write(row, COL_RES_TYPE, dev)
		sheet.write(row, COL_SUB_TYPE, subtype)
		sheet.write(row, COL_RES_START, start)
		sheet.write(row, COL_RES_COUNT, count)
		formula = xlwt.Formula('%s - SUM(%s:%s)' % (
			rowcol_to_cell(row, COL_RES_COUNT),
			rowcol_to_cell(row, COL_HOST_START),
			rowcol_to_cell(row, COL_BALANCE - 1)
		))
		sheet.write(row, COL_BALANCE, formula, fmt_grayed)
		row = row + 1


################################################################################
##                          Main program starts here                          ##
################################################################################

parser = argparse.ArgumentParser(prog='RM-autogen.py', formatter_class=argparse.RawTextHelpFormatter,
	description='RM-autogen.py - Auto generate the Resource Management data')

parser.add_argument('-s', '--soc', required=True, dest='soc',
	action='store', choices=['j721e', 'am65x'],
	help='SoC name')

parser.add_argument('-o', '--output', required=True, dest='output',
	action='store',
	help='output file name')

parser.add_argument('--sysfw_path', required=True, dest='prefix',
	action='store',
	help='Path to system firmware repo')

args = parser.parse_args()
print(args)

# Parse docuemntation and extract host_id defines
output = evalcmd('cat %s/output/%s/sec_proxy/hosts.h | grep "#define HOST_ID" | awk -F"[ ()]*" \'{print $2" " $3}\'' % (args.prefix, args.soc))
for line in output.split('\n'):
	if (line == ''):
		continue
	(host, host_id) = line.split(' ')
	host_id = int(host_id.strip(string.ascii_letters), 0)
	dict_host[host] = host_id

# Parse docuemntation and extract dev_id and subtype defines
output = evalcmd('cat %s/output/%s/rm/resasg_types.rst | grep SUBTYPE | awk -F" " \'{ print $2" "$4" "$6" "$8" "$10 }\'' % (args.prefix, args.soc))
dev = dev_id = None
for line in output.split('\n'):
	if (line == ''):
		continue
	array = line.split(' ')
	#print(array)
	if (array[0] != '|'):
		(dev, dev_id, subtype, subtype_id, utype_id) = array
	else:
		(dummy, subtype, subtype_id, utype_id, dummy) = array

	#print (dev, dev_id, subtype, subtype_id, utype_id)
	dict_dev[dev] = int(dev_id, 0)
	dict_subtype[subtype] = int(subtype_id, 0)
	# TODO Add raneg parsing when documentation supports
	'''
	utypes.append((dev, subtype))
	'''

#Parse bordconfig to extract the dev, subtype and range of resources
output = evalcmd('cat %s/output/%s/rm/boardcfg_rm_data.c | grep -A100000 "resasg_entries" | awk \'BEGIN { FS="\\n"; RS="{" } { print $2 " " $3 " " $4 }\' | awk -F" " \'{print $3 " " $4 " " $7 " " $10}\'' % (args.prefix, args.soc))
for line in output.split('\n'):
	if (line == ''):
		continue
	match = re.match("RESASG_UTYPE.(.*), (.*)., (.*)U, (.*)U,.*", line)
	if (match == None):
		continue
	(dev, subtype, start, count) = match.groups(0)
	start = int(start)
	count = int(count)
	#print((dev, subtype, start, count))
	utypes.append((dev, subtype, start, count))

#print(dict_dev)
#print(dict_subtype)
#print(utypes)

#Generate the soc data defines
data = gen_soc_py_data(args.soc)
ofile = open("%s.py" % args.soc, "w")
ofile.write(data)
ofile.close()

#Generate the excel sheet with default values
workbook = xlwt.Workbook()
sheet = workbook.add_sheet(args.soc)
gen_rm_resasg_sheet(sheet)
workbook.save(args.output)
