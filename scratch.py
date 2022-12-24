import os

dir_name = '/home/egyptian-overlord/Documents'
contents = os.listdir(dir_name)
files = []
folders = []

for index, item in enumerate(contents):
    path = dir_name + '/' + item
    print(index, " -> ", path)
    if os.path.isdir(path):
        folders.append(item)
    else:
        files.append(item)

print(len(contents))
print(sorted(folders), "\n")
print(sorted(files), "\n")
print(sorted(contents))