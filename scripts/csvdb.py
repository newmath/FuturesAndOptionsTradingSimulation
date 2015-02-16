#ROUTINES FOR TREATING CSV FILES LIKE RELATIONAL DATABASE TABLES

#IMPORT OS FOR FILE I/O
import os.path
#IMPORT STRING FUNCTIONS
from stringFunctions import clean

def HashTableFromFileAsText(filename = '',sep=','):
    #INIT RESULT HASH
    _result = dict()

    #VALIDATE THAT FILE EXISTS
    if not os.path.isfile(filename):
        print 'file not found: ',filename
        return _result

    #READ DATA FROM FILE
    infile = open(filename,'r')
    linenum = 0
    col_headings = []
    for line in infile:
        linenum += 1
        line = clean(line)
        #print line
        if linenum == 1:
            col_headings = line.split(sep)
            for j in range(len(col_headings)):
                col_headings[j] = clean(col_headings[j])
            continue
        fields = line.split(sep)
        _id = fields[0]
        _result[_id] = dict()
        for j in range(len(fields)):
            _result[_id][col_headings[j]] = clean(fields[j])
            #print _id,col_headings[j],_result[_id][col_headings[j]]
    #RETURN COMPILED TABLE
    return _result
