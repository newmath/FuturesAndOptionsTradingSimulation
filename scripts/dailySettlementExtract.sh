#!/bin/bash  
cd ~/MarketData/scripts  
./downloadCmeSettlementFiles.py  
python ./constructCurvesAndSurfacesFromSettlementDataFiles.py  

