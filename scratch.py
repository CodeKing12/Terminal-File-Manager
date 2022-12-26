from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

code = 'print "Hello World"'
format = highlight(code, PythonLexer(), TerminalFormatter())