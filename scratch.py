from pprint import PrettyPrinter

fileprint = PrettyPrinter(
    indent=4,
    width=100
)

def display_content(file):
    y_coord = 3
    with open(file) as content:
        lines = content.readlines()
    x = fileprint.pprint(lines)

display_content('/home/egyptian-overlord/Documents/File-Manager/data.json')

# import os

# dir_name = '/home/egyptian-overlord/Documents'
# contents = os.listdir(dir_name)
# files = []
# folders = []

# for index, item in enumerate(contents):
#     path = dir_name + '/' + item
#     print(index, " -> ", path)
#     if os.path.isdir(path):
#         folders.append(item)
#     else:
#         files.append(item)

# print(len(contents))
# print(sorted(folders), "\n")
# print(sorted(files), "\n")
# print(sorted(contents))