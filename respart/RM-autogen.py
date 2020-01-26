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

def gen_rmcfg_data(sharing):

	rmcfg = ''
	num_entries = 0
	rmconfig_comment = '''
		/* %s */\n'''
	rmconfig_templ = '''\
		{
			.start_resource = %d,
			.num_resource = %d,
			.type = RESASG_UTYPE (%s,
					%s),
			.host_id = %s,
		},\n'''

	for res in range(ROW_RES_START, sheet.nrows):

		comment = sheet.cell_value(res, COL_COMMENT)
		restype = sheet.cell_value(res, COL_RES_TYPE)
		subtype = sheet.cell_value(res, COL_SUB_TYPE)
		start = sheet.cell_value(res, COL_RES_START)
		if (restype == '' or subtype == '' or start == ''):
			continue

		for host in range(COL_HOST_START, sheet.ncols):

			#print ("##v(%d, %d) = '%s'" % (res, host, sheet.cell_value(res, host)))
			host_id = sheet.cell_value(ROW_HOST_ID, host).split('\n')[0]
			if (re.match("HOST_ID_.*", host_id) == None):
				continue

			num = sheet.cell_value(res, host)
			if (num == '' or int(num) == 0):
				continue

			if (comment != None):
				rmcfg += rmconfig_comment % comment
				comment = None

			rmcfg += (rmconfig_templ % (start, num, restype, subtype, host_id))
			num_entries += 1

			for pair in sharing:
				if (host_id != pair[0]):
					continue

				shared_host = pair[1]
				rmcfg += (rmconfig_templ % (start, num, restype, subtype, shared_host))
				num_entries += 1

			start += int(num)
	return (rmcfg, num_entries)


################################################################################
##                          Main program starts here                          ##
################################################################################

parser = argparse.ArgumentParser(prog='RM-autogen.py', formatter_class=argparse.RawTextHelpFormatter,
	description='RM-autogen.py - Auto generate the Resource Management data')

parser.add_argument('-f', '--format', required=True, dest='format',
	action='store', choices=["boardconfig", "rtos_rmcfg", "jailhouse_cell_config"],
	help='format to select the output file')

parser.add_argument('-o', '--output', dest='output',
	action='store',
	help='output file name')

parser.add_argument('-s', '--share', dest='share', default=[],
	action='append', nargs=2, metavar=('HOST_ID_A', 'HOST_ID_B'),
	help='Share resource with HOST_ID_A for HOST_ID_B')

parser.add_argument('workbook', help='Input excel sheet with assigned resources')

args = parser.parse_args()
print(args)

workbook = xlrd.open_workbook(args.workbook)
sheet = workbook.sheet_by_index(0)

#sheet.nrows = 9
if (args.format == 'boardconfig'):
	(rmcfg, num_entries) = gen_rmcfg_data(args.share)
	print ("Total entries = %d" % num_entries)
	msg = "Generated rm-cfg.c"
	data = rmcfg
elif (args.format == 'rtos_rmcfg'):
	(rtos_rmcfg, num_entries) = gen_rtos_rmcfg_data()
	msg = "Generated udma_rm-cfg.c"
	data = rtos_rmcfg
else:
	print ("ERROR: format %s not supported")


if (args.output):
	ofile = open(args.output, "w")
	ofile.write(data)
	ofile.close()
else:
	print ("%s\n%s" % (msg, data))

# END OF FILE
