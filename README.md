# SNAP2STAMPS
All of scripts are based on the script of Jose Manuel Delgado Blasco and Michael Foumelis, please find detail in:
https://github.com/mdelgadoblasco/snap2stamps

This script working on:
1. multi-sw, multi-look for Sentinel
2. multi-threaded for slave prepare, coreg&ifg, NOT for stamps_export.
3. can stop and continue processing in slave prepare and coreg&ifg by modify finished.txt in /ifg and /slaves 



######### CONFIGURATION FILE ######
###################################
# PROJECT DEFINITION
SOURCEFOLDER=/Volumes/DATA/ylnuclear2/org: all the .zip files are here.

PROJECTFOLDER=/Volumes/DATA/ylnuclear2/psinsar: the results files

GRAPHSFOLDER=/Users/ysdong/Software/my_snap/graphs: the graphs files

##################################
# PROCESSING PARAMETERS

IW1=IW3 : SHOULD be IW1,IW2,IW3 or you can put your SWs here. it can be one, two or three SWs. which depend on your AOI. if you don't know your AOI coverage, just set it to IW1,IW2,IW3.  

MASTER=S1A_IW_SLC__1SDV_20180220T023028_20180220T023055_020684_0236DF_0435.zip,S1A_IW_SLC__1SDV_20180220T023052_20180220T023119_020684_0236DF_C5C3.zip  :the master files, it could be one or two .zip

##################################
# AOI AREA 
LONMIN=50.810
LATMIN=28.700
LONMAX=51.310
LATMAX=29.300
##################################
# Multilook $ Smoothing 
RGLOOK=4
AZLOOK=1 
SMOOTH=1: if SMOOTH=1, the ifg will be filted.  
##################################
# SNAP GPT 
GPTBIN_PATH=/Applications/snap/bin/gpt
##################################
# COMPUTING RESOURCES TO EMPLOY
CPU=12
CACHE=32G
Multiproc=1: Note: this can be set to 1, 2 or 3, which depend on your memory 
##################################
