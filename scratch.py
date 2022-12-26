from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from ansi import text_with_fg_bg_attr

with open('try6.py') as file:
    lines = file.read()
    lines =  highlight(lines, PythonLexer(), TerminalFormatter())

    # for index, line in enumerate(lines):
    #     lines[index] =  highlight(line, PythonLexer(), TerminalFormatter())

for chunk in text_with_fg_bg_attr(lines):
    print(chunk)

# Look into the _draw_line(function) in ranger
# Look into the ansi folder in ranger

