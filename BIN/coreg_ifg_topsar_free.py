
### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Date: 21/06/2018
# Version: 1.0

# Updated by Yusen DONG, dongyusen@gmail.com
# Date: 22/03/2020
# for coregistration, interferometry, moscia and subset data. 
# it's Working fun.

# Step 1 : preparing slaves in folder structure
# Step 2 : TOPSAR Splitting (Assembling) and Apply Orbit
# Step 3 : Coregistration and Interferogram generation
# Step 4 : StaMPS export

# Added option for CACHE and CPU specification by user
# Planned support for DEM selection and ORBIT type selection 


  

import os
from pathlib import Path
# import pathlib
import sys
import glob
import subprocess
import shlex
import time
import shutil
import multiprocessing
from multiprocessing import Pool

bar_message='#####################################################################'
PROJECT = []
MASTER = []
GRAPH = []
GPT = []
CACHE = []
CPU = []
IWlist = []
slavefolder = []
splitfolder = []
graphfolder = []
splitmasterfolder=[]
splitslavefolder=[]
coregfolder=[]
ifgfolder=[]
tempfolder=[]
SOURCEFOLDER=[]
polygon=''
slavelist = [[] for i in range(500)]
total_slave=0

finishedfile=''
finishedlist=[]

error_flag = 0


# data process part: 
def interferometry(inlist):
	files = slavelist[inlist]
	slavedate = files[0]
	masterdate = MASTER[0]
	masterdate = masterdate[17:25]
	timeStarted_func = time.time()
	error_flag = 0

	print '\033[1;35m Processing ... \033[0m' + str(inlist+1) + ' of ' + str(total_slave) + ' dataset..............'
	print ' Processing ...' + masterdate + '_' + slavedate + '.....................'

	## checking dataset in processed list:
	with open(finishedfile, 'r') as file :
		filedata = file.read()
	tempfilename = masterdate + '_' + slavedate  + '.dim'
	# print tempfilename 
	if tempfilename in filedata:
		print ' Alreay processed, Skip it, or Delete the file in ifg/finished.txt to Reprocess it? ..............'
		return

	## start processing:

	for IW in IWlist:
		graphxml=GRAPH+'/topsar_1iw.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + IW + '.xml' #will be changed in mergering !
		print '\n*****' + IW + ' of ' + str(len(IWlist)) +'IWs :'+ masterdate + '_' + slavedate + ' coregistration and interferometry\n'
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('MASTER',	splitmasterfolder + '/' + masterdate + '_' + IW 		+ '.dim')
			filedata = filedata.replace('SLAVE', 	splitslavefolder  + '/' + slavedate  + '_' + IW 		+ '.dim')
			filedata = filedata.replace('OUTCOREG',	tempfolder   	  + '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTIFG', 	tempfolder     	  + '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'ifg.dim')
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  coreg_ifg2run\n'
			return
	
	print '\n*****' + masterdate + '_' + slavedate + ' will be mosaicing and subsetting  ........'

	if len(IWlist) == 1: 
		IW=IWlist[0]
		print '***** One Swath Used ***** \n'
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f1sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f1.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportifg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + masterdate + '_' + slavedate  + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f1\n'
			return

		graphxml=GRAPH+'/topsar_1iw-f1c.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportcoreg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IW  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + masterdate + '_' + slavedate  + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f1c\n'
			return


	if len(IWlist) == 2:
		print '***** Two Swathes Used ***** \n'
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f2sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f2.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportifg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[0]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[1]  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + masterdate + '_' + slavedate + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f2\n'
			return


		graphxml=GRAPH+'/topsar_1iw-f2c.xml' #will be changed in mergering !
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportcoreg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[0]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[1]  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + masterdate + '_' + slavedate + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f2c\n'
			return

	if len(IWlist) == 3:
		print '***** Three Swathes Used ***** \n'
		if SMOOTH=='1':
			graphxml=GRAPH+'/topsar_1iw-f3sm.xml' #will be changed in mergering !
		else:
			graphxml=GRAPH+'/topsar_1iw-f3.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportifg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[0]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[1]  + '_' + 'ifg.dim')
			filedata = filedata.replace('INPUT2',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[2]  + '_' + 'ifg.dim')
			filedata = filedata.replace('OUTPUT0', 	ifgfolder  + '/' + masterdate + '_' + slavedate + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f3\n'
			return

		graphxml=GRAPH+'/topsar_1iw-f3c.xml'
		graph2run=PROJECT+'/graphs/coreg_ifg2run'  + '_' + masterdate + '_' + slavedate + '_' + '_exportcoreg' + '.xml' #will be changed in mergering !
		with open(graphxml, 'r') as file :
			filedata = file.read()
			filedata = filedata.replace('INPUT0',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[0]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT1',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[1]  + '_' + 'coreg.dim')
			filedata = filedata.replace('INPUT2',	tempfolder + '/' + masterdate + '_' + slavedate + '_' + IWlist[2]  + '_' + 'coreg.dim')
			filedata = filedata.replace('OUTPUT0', 	coregfolder+ '/' + masterdate + '_' + slavedate + '.dim')
			filedata = filedata.replace('POLYGON', 	polygon)
			filedata = filedata.replace('RGLOOK', 	RGLOOK)
			filedata = filedata.replace('AZLOOK', 	AZLOOK)
		with open(graph2run, 'w') as file:
			file.write(filedata)
		args=[GPT, graph2run, '-q', CPU, '-c', CACHE]
		process = subprocess.Popen(args, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
		for line in iter(process.stdout.readline, b''):
			print line.rstrip()
		process.stdout.close()
		process.wait()
		if process.returncode != 0 :
			error_flag = 1
			print '033[1;35m Error in processing ... \033[0m  topsar_1iw-f3c\n'
			return

	##########################
	shutil.rmtree(tempfolder)
	os.mkdir(tempfolder) 
	
	if error_flag == 0:
		with open(finishedfile, 'a') as file :
			file.write(masterdate + '_' + slavedate +'.dim\n')
			
	print time.asctime( time.localtime(time.time()))
	timeDelta = time.time() - timeStarted_func
	print '\n\033[1;35m Finished coregistration, interferometry, mosaic and subset processing of \033[0m'+ masterdate + '_' + slavedate +' in ' +  str(timeDelta/60.0) + ' mins.\n'
	print bar_message
	print '\n'

## main part:
if __name__ == "__main__":

	# Getting configuration variables from inputfile
	inputfile = sys.argv[1]
	print '\n\033[1;35m Some necessary information of this work:\033[0m \n'
	try:
		in_file = open(inputfile, 'r')
		for line in in_file.readlines():
			if "SOURCEFOLDER" in line:
				SOURCEFOLDER = line.split('=')[1].strip()
				print 'Source Path:   ', SOURCEFOLDER 
			if "MASTER" in line:
				MASTER = line.split('=')[1].strip()
				MASTER = MASTER.replace(' ','')
				MASTER = MASTER.split(',')
				print 'Master data: ', MASTER 
			if "PROJECTFOLDER" in line:
				PROJECT = line.split('=')[1].strip()
				print 'Project path:  ', PROJECT
			if "IW1" in line:
				IWlist = line.split('=')[1].strip()
				IWlist = IWlist.replace(' ','')
				IWlist = IWlist.split(',')
				print 'Used IW:  ', IWlist
			if "LONMIN" in line:
				LONMIN = line.split('=')[1].strip()
			if "LATMIN" in line:
				LATMIN = line.split('=')[1].strip()
			if "LONMAX" in line:
				LONMAX = line.split('=')[1].strip()
			if "LATMAX" in line:
				LATMAX = line.split('=')[1].strip()
			if "GRAPHSFOLDER" in line:
				GRAPH = line.split('=')[1].strip()
			if "RGLOOK" in line:
				RGLOOK = line.split('=')[1].strip()
			if "AZLOOK" in line:
				AZLOOK = line.split('=')[1].strip()
			if "SMOOTH" in line:
				SMOOTH = line.split('=')[1].strip()
				# print GRAPH
			if "GPTBIN_PATH" in line:
				GPT = line.split('=')[1].strip()
				# print GPT			
			if "CACHE" in line:
				CACHE = line.split('=')[1].strip()
				# print CACHE
			if "CPU" in line:
				CPU = line.split('=')[1].strip()
				# print CPU
			if "Multiproc" in line:
				Multiproc = int(line.split('=')[1].strip())
				# print Multiproc				
	finally:
		in_file.close()
polygon='POLYGON (('+LONMIN+' '+LATMIN+','+LONMAX+' '+LATMIN+','+LONMAX+' '+LATMAX+','+LONMIN+' '+LATMAX+','+LONMIN+' '+LATMIN+'))'
print 'AOI: ', polygon
print 'Mulitlook, Ra:Az = ', RGLOOK + ':' + AZLOOK
	#############################################################################
	### TOPSAR Splitting (Assembling) and Apply Orbit section ####
	############################################################################
splitmasterfolder=PROJECT+'/MasterSplit'
splitslavefolder=PROJECT+'/SlaveSplit'
graphfolder=PROJECT+'/graphs'
coregfolder=PROJECT+'/coreg'
ifgfolder=PROJECT+'/ifg'
tempfolder=PROJECT+'/temp'
finishedfile=ifgfolder+'/finished.txt'

if not os.path.exists(splitslavefolder):
	os.makedirs(splitslavefolder)
if not os.path.exists(graphfolder):
	os.makedirs(graphfolder)
if not os.path.exists(coregfolder):
	os.makedirs(coregfolder)
if not os.path.exists(ifgfolder):
	os.makedirs(ifgfolder)
if not os.path.exists(tempfolder):
	os.makedirs(tempfolder)	
if not os.path.exists(finishedfile):
	Path(finishedfile).touch()

print bar_message
print '## TOPSAR coregistration, interferometry, moscia and subset for all the Project @@ ##'
print bar_message

## get the slavelist
slavedatelist = []
for filename in sorted(os.listdir(splitslavefolder)):
	if filename.endswith(".dim") : 
		slavedatelist.append(filename)
k=0
for datelist in slavedatelist:
	if  k == 0 :
		slavelist[k].append(datelist[0:8])
		slavelist[k].append(datelist)
		k = k + 1
	else :
		mflag = 0
		for i in range(k):
			if (datelist[0:8] in slavelist[i]):
				slavelist[i].append(datelist)
				mflag = 1
		if mflag == 0 :
			slavelist[k].append(datelist[0:8])
			slavelist[k].append(datelist)
			k = k + 1
print '\n*****  Totally ' + str(k) + ' slaves!!!  ****\n'
newlist = [x for x in slavelist if x] 
slavelist = newlist
del newlist
total_slave = k
# print slavelist

# multiprocessing:
inputlist  = range(k)

pool = Pool(processes = Multiproc)
result = pool.map(interferometry, inputlist)
# print result

