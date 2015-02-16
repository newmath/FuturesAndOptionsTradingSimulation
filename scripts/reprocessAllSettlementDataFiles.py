#!/opt/local/bin/python  

import os
import sys

settlement_file_path = '../settlement_data_files'  
data_process_script = 'constructCurvesAndSurfacesFromSettlementDataFiles.py'  

firstDate = '19000101'
lastDate = '30001231'
if len(sys.argv) > 1:
        firstDate = sys.argv[1]
if len(sys.argv) > 2:
        lastDate = sys.argv[2]
        
for o in os.listdir(settlement_file_path):
	# EACH SUBDIRECTORY OF THE SETTLEMENT FILE PATH IS NAMED BY A DATE, BUT CHECK ANYWAY 
	if os.path.isdir(os.path.join(settlement_file_path,o)):
                if o >= firstDate and o <= lastDate:
                        command = 'python ./' + data_process_script + ' ' + o
                        os.system(command) 
