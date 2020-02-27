#!/usr/bin/python
#
# Author: Nikhil Devshatwar <nikhil.nd@ti.com>
# Python script to auto generate the Resource Management data
# Parses excel sheet and generates different files which need
# to be in sync for correct functionality
#
import argparse
import xlrd
import xlwt
import re

COL_COMMENT = 0
COL_RES_TYPE = 1
COL_SUB_TYPE = 2
COL_RES_FIELD = 3
COL_RES_START = 6
COL_HOST_START = 7

ROW_HOST_ID = 0
ROW_RES_START = 2

comments = {}

def gen_rmcfg_data(sharing):
	global comments
	rmcfg = []
	for res in range(ROW_RES_START, sheet.nrows):

		comment = sheet.cell_value(res, COL_COMMENT)
		restype = sheet.cell_value(res, COL_RES_TYPE)
		subtype = sheet.cell_value(res, COL_SUB_TYPE)
		start = sheet.cell_value(res, COL_RES_START)
		if (restype == '' or subtype == '' or start == ''):
			continue
		start = int(start)
		comments[(restype, subtype)] = comment

		for host in range(COL_HOST_START, sheet.ncols):

			#print ("##v(%d, %d) = '%s'" % (res, host, sheet.cell_value(res, host)))
			host_id = sheet.cell_value(ROW_HOST_ID, host).split('\n')[0]
			if (re.match("HOST_ID_.*", host_id) == None):
				continue

			num = sheet.cell_value(res, host)
			if (num == '' or int(num) == 0):
				continue
			num = int(num)

			rmcfg.append((start, num, restype, subtype, host_id))

			for pair in sharing:
				if (host_id != pair[0]):
					continue

				shared_host = pair[1]
				rmcfg.append((start, num, restype, subtype, shared_host))


			start += int(num)
	return rmcfg

def print_rmcfg(rmcfg):
	comment_templ = '''
		/* %s */\n'''
	rmconfig_templ = '''\
		{
			.start_resource = %d,
			.num_resource = %d,
			.type = RESASG_UTYPE (%s,
					%s),
			.host_id = %s,
		},\n'''
	output = ""

	def custom_key(entry):
		(start, num, restype, subtype, host) = entry
		restype = soc.const_values[restype]
		subtype = soc.const_values[subtype]
		host = soc.const_values[host]
		utype = (restype << soc.RESASG_TYPE_SHIFT) | (subtype << soc.RESASG_SUBTYPE_SHIFT)
		val = (utype << 24) | (start << 8) | (host << 0)
		return val

	sorted_rmcfg = sorted(rmcfg, key=custom_key)

	comment = None
	for entry in sorted_rmcfg:
		(start, num, restype, subtype, host) = entry

		if (comment != comments[(restype, subtype)]):
			comment = comments[(restype, subtype)]
			output += comment_templ % comment
		output += rmconfig_templ % (start, num, restype, subtype, host)
	return output

################################################################################
##                          Main program starts here                          ##
################################################################################

parser = argparse.ArgumentParser(prog='RM-autogen.py', formatter_class=argparse.RawTextHelpFormatter,
	description='RM-autogen.py - Auto generate the Resource Management data')

parser.add_argument('-s', '--soc', required=True, dest='soc',
	action='store', choices=['j721e', 'am65x'],
	help='Share resource with HOST_ID_A for HOST_ID_B')

parser.add_argument('-o', '--output', required=True, dest='output',
	action='store',
	help='output file name')

parser.add_argument('-f', '--format', required=True, dest='format',
	action='store', choices=['boardconfig', 'jailhouse_cell_config'],
	help='format to select the output file')

parser.add_argument('--share', dest='share', default=[],
	action='append', nargs=2, metavar=('HOST_ID_A', 'HOST_ID_B'),
	help='Share resource with HOST_ID_A for HOST_ID_B')

parser.add_argument('workbook', help='Input excel sheet with assigned resources')

args = parser.parse_args()
print(args)

soc = __import__(args.soc)
workbook = xlrd.open_workbook(args.workbook)
sheet = workbook.sheet_by_name(args.soc)

#sheet.nrows = 9
if (args.format == 'boardconfig'):
	boardconfig = gen_rmcfg_data(args.share)
	print ("Total entries = %d" % len(boardconfig))
	data = print_rmcfg(boardconfig)
else:
	print ("ERROR: format %s not supported")
	exit(1)


ofile = open(args.output, "w")
ofile.write(data)
ofile.close()

# END OF FILE
