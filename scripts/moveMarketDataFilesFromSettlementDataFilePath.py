# Move market data files to location separate from settlement data files so
# they can be easily backed up and transferred separately.  This is probably a
# write-once, run-once routine, but it's worth saving

import os

settle_base = '../settlement_data_files'
market_base = '../market_data_files'

# FOR EACH SUBDIRECTORY IN SETTLEMENT DATA FILES DIRECTORY
#   CREATE NEW MARKET SUBDIRECTORY IF NECESSARY
#   MOVE MARKET DATA FILES FROM SETTLE DIR TO MARKET DIR

for list_item in os.listdir(settle_base):
        dir_path = settle_base + '/' + list_item
        if os.path.isdir(dir_path):
            #DETERMINE AND/OR CREATE OUTPUT FOLDER
            out_path = market_base + '/' + list_item
            if not os.path.exists(out_path): os.mkdir(out_path)
            #MOVE MARKET DATA FILES
            for filename in os.listdir(dir_path):
                header = filename[:7]
                if header == 'mktdata':
                    settle_file = dir_path + '/' + filename 
                    market_file = out_path + '/' + filename
                    os.rename(settle_file,market_file)
