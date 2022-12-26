from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

def makeData(data):
    out = []
    pos = 0
    ccol = ()
    while pos < len(data):
        if ord(data[pos]) == 27: #if it's a colour escape sequence
            pos += 2
            if data[pos] == "0": pos += 2; continue #tiv resets after every line, ignore that
            if data[pos] == "4": fg = False; bg = True
            else: fg = True; bg = False
            pos += 5 #skip 8;5;
            num = ""
            while data[pos] != "m":
                num += data[pos]
                pos += 1
            num = int(num)
            pos += 1
            ccol = (fg, bg, num)
            print(ccol)
        else: #otherwise, add the character with the current colour to the buffer
            out.append((ccol, data[pos]))
            pos += 1
    return out

code = 'print "Hello World"'
format = highlight(code, PythonLexer(), TerminalFormatter())
print(makeData(format))