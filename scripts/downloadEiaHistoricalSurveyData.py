import os  
import urllib2
#import shutil
from datetime import date

# READ URL LIST FROM CONFIG FILE
urlFile = '../config/eia_file_list.txt'  
block_sz = 8192  
f = open(urlFile, 'r')  
url_list = f.readlines()  
f.close() 

dest_dir = '../eia_survey_data'

#DOWNLOAD EACH OF THE FILES TO THE TEMP DIRECTORY
for url in url_list: 
	url = url.strip().split(',')[0]
	print 'Downloading ' + url 
	u  = urllib2.urlopen(url)  
	file_name = dest_dir + '/' + url.split('/')[-1]  
	f = open(file_name, 'wb')  
	while 1:  
		buffer = u.read(block_sz)  
		if not buffer: 
			break  
		f.write(buffer)  
	f.close()  

#CONVERT ALL FILES TO CSV  

