#DEFINE FUNCTIONS FOR USE IN PARSING FILES
def clean(string = ''):
    return string.strip(' \t\n\r"')

def left(string = '',c = 0):
    return string[:c]

def right(string = '',c = 0):
    return string[len(string)-c:]

def mid(string = '',start = 0, c = 0):
    return string[start:start+c]
