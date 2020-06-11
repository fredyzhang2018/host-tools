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
COL_RES_COUNT = 3
COL_RES_START = 4
COL_HOST_START = 5

ROW_HOST_ID = 0
ROW_RES_START = 1

comments = {}
resasg = {}
host_list = []

def gen_rmcfg_data(sharing):
	global comments
	rmcfg = []
	for res in range(ROW_RES_START, sheet.nrows):

		comment = sheet.cell_value(res, COL_COMMENT)
		restype = sheet.cell_value(res, COL_RES_TYPE)
		subtype = sheet.cell_value(res, COL_SUB_TYPE)
		count = sheet.cell_value(res, COL_RES_COUNT)
		start = sheet.cell_value(res, COL_RES_START)
		if (restype == '' or subtype == '' or start == '' or count == ''):
			continue
		start = int(start)
		count = int(count)
		comments[(restype, subtype)] = comment

		if (args.allow_all):
			rmcfg.append((start, count, restype, subtype, "HOST_ID_ALL"))
			continue

		for host in range(COL_HOST_START, sheet.ncols):

			#print ("##v(%d, %d) = '%s'" % (res, host, sheet.cell_value(res, host)))
			host_id = sheet.cell_value(ROW_HOST_ID, host).split('\n')[0]
			if (re.match("HOST_ID_.*", host_id) == None):
				continue

			num = sheet.cell_value(res, host)
			if (num == '' or int(num) == 0):
				continue
			num = int(num)

			if (host_id not in host_list):
				host_list.append(host_id)

			key = (restype, subtype, host_id)
			value = (start, num)
			if (key in resasg):
				print ("WARNING: Ignoring multiple entries for (%s,%s,%s)" % key)
				#resasg[key].append(value)
			else:
				resasg[key] = [value]
				rmcfg.append((start, num, restype, subtype, host_id))

			for pair in sharing:
				if (host_id != pair[0]):
					continue

				shared_host = pair[1]
				rmcfg.append((start, num, restype, subtype, shared_host))

			start += int(num)

	return rmcfg

def print_rmcfg(rmcfg, prefix=""):
	comment_templ = '''
		/* %s */\n'''
	kig_rmconfig_templ = '''\
		{
			.start_resource = %d,
			.num_resource = %d,
			.type = RESASG_UTYPE (%s,
					%s),
			.host_id = %s,
		},\n'''
	sciclient_rmconfig_templ = '''\
        {
            .start_resource = %d,
            .num_resource = %d,
            .type = RESASG_UTYPE (%s, %s),
            .host_id = %s,
        },\n'''

	if (args.format == "boardcfg_kig"):
		rmconfig_templ = kig_rmconfig_templ
	elif (args.format == "boardcfg_sciclient"):
		rmconfig_templ = sciclient_rmconfig_templ
		comment_templ = comment_templ.replace('\t', '    ')

	output = ""
	rmconfig_templ = rmconfig_templ.replace("RESASG_UTYPE", "%sRESASG_UTYPE" % prefix)

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

		# Quirk to add prefix for every dev/subtype macro (SCIclient uses TISCI prefix)
		if (prefix):
			dev_prefix = "%s_DEV" % args.soc.upper()
			if (args.soc == "am6x" or args.soc == "am65x_sr2"):
				dev_prefix = "AM6_DEV"

			subtype = subtype.replace("RESASG", "%sRESASG" % prefix)
			restype = restype.replace(dev_prefix, "%sDEV" % prefix)
			host = "%s%s" % (prefix, host)

		output += rmconfig_templ % (start, num, restype, subtype, host)
	return output

def print_per_host_id(rmcfg, prefix=""):
	print host_list
	for h_id in  host_list:
		print (">>>>>> For host %s" % h_id)
		for entry in rmcfg:
			(start, num, restype, subtype, host) = entry
			if (host == h_id):
				print ("%s: %s start = %d, count = %d " % (restype, subtype, start, num))

################################################################################
##                          Main program starts here                          ##
################################################################################

parser = argparse.ArgumentParser(prog='RM-autogen.py', formatter_class=argparse.RawTextHelpFormatter,
	description='RM-autogen.py - Auto generate the Resource Management data')
required    = parser.add_argument_group('required arguments')
optional    = parser.add_argument_group('optional arguments')
conditional = parser.add_argument_group('conditional arguments')

required.add_argument('-s', '--soc', required=True, dest='soc',
	action='store', choices=['j721e', 'am6x', 'am65x_sr2'],
	help='SoC name')
required.add_argument('-o', '--output', required=True, dest='output',
	action='store',
	help='output file name')
required.add_argument('-f', '--format', required=True, dest='format',
	action='store', choices=['boardcfg_kig', 'boardcfg_sciclient'],
	help='format to select the output file')
required.add_argument('workbook',
	help='Input excel sheet with assigned resources')

optional.add_argument('--share', dest='share', default=[],
	action='append', nargs=2, metavar=('HOST_ID_A', 'HOST_ID_B'),
	help='Share resource with HOST_ID_A for HOST_ID_B')
optional.add_argument('--perhost', dest='perhost',
	action='store_true',
	help='Print the resource assignment per host')
optional.add_argument('--allow_all', dest='allow_all',
	action='store_true',
	help='Create the minimal boardconfig to allow all hosts to access all resources')


args = parser.parse_args()
print(args)

soc = __import__(args.soc)
workbook = xlrd.open_workbook(args.workbook)
sheet = workbook.sheet_by_name(args.soc)

#sheet.nrows = 9
if (args.format == 'boardcfg_kig'):
	boardconfig = gen_rmcfg_data(args.share)
	print ("Total entries = %d" % len(boardconfig))
	data = print_rmcfg(boardconfig)
elif (args.format == 'boardcfg_sciclient'):
	boardconfig = gen_rmcfg_data(args.share)
	print ("Total entries = %d" % len(boardconfig))
	data = print_rmcfg(boardconfig, prefix="TISCI_")
else:
	print ("ERROR: format %s not supported" % args.format)
	exit(1)

if (args.perhost):
	print_per_host_id(boardconfig, prefix="TISCI_")

ofile = open(args.output, "w")
ofile.write(data)
ofile.close()

# END OF FILE
