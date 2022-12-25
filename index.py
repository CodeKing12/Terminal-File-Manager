import curses
from curses import wrapper
import math
import os
import json

# Let there be 3 windows
# Their content is determined by the past, present and future directories

win2_scroll = 0
win3_scroll = 0
rotate = True

def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            if type(size) == float:
                if size.is_integer():
                    return "%d %s" % (size, x)
                else:
                    return "%3.1f %s" % (size, x)
            elif type(size) == int:
                return "%d %s" % (size, x)
        size /= 1024.0
    return size

def expand_str(str, end_str, final_len):
    """ Expand the file name string up to the maximum width of the pad """
    str_maxlength = math.floor(final_len-len(end_str) * 4.0/5.0)
    if len(str) > str_maxlength:
        split_str = str.split(".")
        if len(split_str) > 1:
            name = '.'.join(split_str[:-1])
            extension = split_str[-1]
        else:
            name = ''.join(split_str[0])
            extension = ''
        max_name = str_maxlength - len(extension) - 10
        name = name[:max_name] + '~'
        if str.find('.') == -1:
            str = name
        else:
            str = name + "." + extension
    padding = final_len - len(str) - 3
    return " " + str + end_str.rjust(padding, ' ') + " "

def arrange_folder(folder, items):
    folders = []
    files = []
    for file in items:
        path = folder + '/' + file
        if os.path.isdir(path):
            folders.append(file)
        else:
            files.append(file)
    
    folders.sort()
    files.sort()
    arrangement = folders + files
    return arrangement

def display_content(window, file, windowHeight):
    y_coord = 3
    with open(file) as file:
        try:
            lines = file.readlines()
        except UnicodeDecodeError:
            lines = []
    for line in lines:
        y_coord += 1
        if y_coord <= windowHeight - 2: # curses.LINES - 2
            window.addstr(y_coord, 0, line)

def main(screen):
    def refresh_win2(down=True, scroll=False):
        # Prevent scrolling if at the end of the menu
        if selected_option == len(current_files) - 1 and len(current_files) > curses.LINES - 2:
            global win2_scroll
            if win2_scroll == 0 or selected_option >= math.floor(curses.LINES / 2):
                win2_scroll = (len(current_files) - (curses.LINES - 1)) + 3
            window2.refresh(win2_scroll, 0, 0, window1Width, curses.LINES - 1, curses.COLS - 1)
        elif selected_option >= math.floor(curses.LINES / 2):
            # Rotate prevents the pad from scrolling twice at once
            global rotate
            stop_scrolling = False
            if selected_option >= (len(current_files) - (curses.LINES / 2) + 3):
                stop_scrolling = True
            # Revert scrolling to original state when the highlighted item loops back to the start
            if win2_scroll >= math.floor(curses.LINES / 2) and selected_option <= math.floor(curses.LINES / 2):
                win2_scroll = 0
            # Go up if the up signal is received, and vice-versa
            if rotate and not stop_scrolling and scroll:
                if down:
                    win2_scroll += 1
                else:
                    win2_scroll -= 1
            rotate = not rotate
            # Update the screen to scroll
            window2.refresh(win2_scroll, 0, 0, window1Width, curses.LINES - 1, curses.COLS - 1)
        else:
            # Udate the screen normally if scrolling is not needed
            window2.refresh(0, 0, 0, window1Width, curses.LINES - 1, curses.COLS - 1)

    def display_window(window, windowHeight, windowWidth, window_dir, window_data, selector):
        y_coord = 3
        for i, option in enumerate(window_data):
            y_coord += 1
            file_path = window_dir + '/' + option
            if not os.path.islink(file_path):
                file_size = os.path.getsize(file_path)
            else:
                sym_path = os.readlink(file_path)
                try:
                    file_size = os.stat(file_path).st_size
                except FileNotFoundError:
                    try:
                        file_size = os.stat(sym_path).st_size
                    except FileNotFoundError:
                        file_size = 4096
            
            # Specify file as a non directory
            file_is_dir = False

            # If the file is a directory, specify file as a directory and let the output state the number of items in the file
            if os.path.isdir(file_path):
                file_is_dir = True
                append_str = str(len(os.listdir(file_path)))
            else:
                append_str = convert_bytes(file_size)
            if y_coord <= windowHeight: # curses.LINES - 2
                if i == selector:
                    color_scheme = get_color_scheme(option, file_is_dir, highlight=True)
                    properties = color_scheme + curses.A_BOLD
                    window.addstr(y_coord, 0, expand_str(option, append_str, windowWidth), properties)
                else:
                    color_scheme = get_color_scheme(option, file_is_dir, highlight=False)
                    properties = color_scheme
                    if file_is_dir:
                        properties = color_scheme + curses.A_BOLD
                    window.addstr(y_coord, 0, expand_str(option, append_str, windowWidth), properties)
            else:
                pass
    # Clear screen
    # screen.clear()
    curses.curs_set(0)
    curses.cbreak()
    # curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.use_default_colors()
    curses.start_color()
    curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background 
    curses.init_pair(2,curses.COLOR_BLUE, -1)
    curses.init_pair(3,curses.COLOR_RED, -1)
    curses.init_pair(4,curses.COLOR_YELLOW, -1)
    curses.init_pair(5,curses.COLOR_GREEN, -1)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_GREEN)
    h = curses.color_pair(1) #h is the coloring for a highlighted menu option
    folder_color = curses.color_pair(2)
    compressed_color = curses.color_pair(3)
    image_color = curses.color_pair(4)
    document_color = curses.color_pair(5)
    highlight_folder_color = curses.color_pair(6)
    highlight_compressed_color = curses.color_pair(7)
    highlight_image_color = curses.color_pair(8)
    highlight_document_color = curses.color_pair(9)
    n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

    def get_color_scheme(file_name, is_dir=False, highlight=False):
        if highlight:
            color_scheme = curses.A_REVERSE
            if is_dir:
                color_scheme = highlight_folder_color
            elif(file_name.endswith(('.html', '.pdf', '.css', '.js', '.docx', '.txt'))):
                color_scheme = highlight_document_color
            elif(file_name.endswith(('.zip', '.rar', '.7z'))):
                color_scheme = highlight_compressed_color
            elif(file_name.endswith(('.png', '.svg', '.jpg', 'jpeg', 'ico'))):
                color_scheme = highlight_image_color
        else:
            color_scheme = curses.A_NORMAL
            if is_dir:
                color_scheme = folder_color
            elif(file_name.endswith(('.html', '.pdf', '.css', '.js', '.docx', '.txt'))):
                color_scheme = document_color
            elif(file_name.endswith(('.zip', '.rar', '.7z'))):
                color_scheme = compressed_color
            elif(file_name.endswith(('.png', '.svg', '.jpg', 'jpeg', 'ico'))):
                color_scheme = image_color
        
        return color_scheme

    # Create the second window (the window that shows the current directory and it's content)
    window2Width = math.floor(curses.COLS * 4.0/12.0)
    window2Height = 20000
    window2 = curses.newpad(window2Height, window2Width)

    # Create the third window (the window that shows the next directory files or the contents of a readable document)
    window3Width = math.floor(curses.COLS * 5.0/12.0)
    window3Height = 20000
    window3 = curses.newpad(window3Height, window3Width)

    # Create the first window (the window that shows the previous files)
    window1Width = math.floor(curses.COLS * 3.0/12.0)
    window1Height = 20000
    window1 = curses.newpad(window1Height, window1Width)

    screen.refresh()
    # window2.bkgd(h)
    # window3.bkgd(h)
    # window1.bkgd(h)

    current_dir = os.getcwd()
    previous_dir = os.path.dirname(current_dir)
    # previous_files = previous_files[1:20]
    selected_option = 0  # Keep track of the selected main menu option (the current directory)

    # For now, current_dir is the current directory, previous_dir is the parent directory and future_dir is the current_dir

    while True:
        current_files = arrange_folder(current_dir, os.listdir(current_dir))
        # Don't show the previous files if at the root directory
        if previous_dir == None:
            previous_files = []
        else:
            previous_files = arrange_folder(previous_dir, os.listdir(previous_dir))

        if previous_dir == None:
            slash = ''
        else:
            slash = '/'
        future_dir = current_dir + slash + current_files[selected_option]
        if os.path.isdir(future_dir):
            future_files = arrange_folder(future_dir, os.listdir(future_dir))
        else:
            future_files = []

        selected_suboption = 0  # Keep track of the selected option in window 3 (the next directory)
        preselected_option = 0  # Keep track of the previously selected option in window 1 (the previous directory)

        # If there are previous files to show, split the path of the current directory by the '/'
        if len(previous_files) > 0:
            split_path = current_dir.split('/')
            # If we're not at the root directory, make the selected option of the previous directory to be the current directory (identified by the name which is at the end of the path)
            if split_path[-1] != '':
                preselected_option = previous_files.index(split_path[-1])

        # Erase all windows anytime changes are made to properly show changes
        window2.erase()
        window3.erase()
        window1.erase()

		# Print the main menu options
        window1.addstr(1, 2, f'Previous Directory: {previous_dir}')
        window2.addstr(1, 2, f'Current Directory: {current_dir}')
        # window2.addstr(2, 2, f'{math.floor(curses.COLS/3)}')
        display_window(window2, window2Height, window2Width, current_dir, current_files, selected_option)        
        refresh_win2()

        # Print the children of the parent directory
        window3.addstr(1, 1, f'Next Directory: {future_dir}')
        if os.path.isdir(future_dir):
            display_window(window3, window3Height, window3Width, future_dir, future_files, selected_suboption)
        else:
            display_content(window3, future_dir, window3Height)
        # window3.refresh(0, 0, 0, window2Width, curses.LINES - 1, curses.COLS - 1)
        window3.refresh(0, 0, 0, window1Width+window2Width, curses.LINES - 1, curses.COLS - 1)

        display_window(window1, window1Height, window1Width, previous_dir, previous_files, preselected_option)
        window1.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 2)

        # Get user input
        key = screen.getch()

        # Navigate up and down through the main menu options
        if key == curses.KEY_UP or key == 38:
            if selected_option > 0:
                selected_option -= 1
            else:
                selected_option = len(current_files) - 1

            file = current_dir + '/' + current_files[selected_option]
            if os.path.isdir(file):
                future_dir = file
            # else:
            #     window3.addstr(3, 2, str(open(file, 'rt', errors='ignore').read()))
            # window3.refresh(0, 0, 0, window2Width, window3Height, window3Width+window2Width)

            window2.addstr(curses.LINES - 1, 1, "Up Key works")
            refresh_win2(False, scroll=True)
            
        elif (key == curses.KEY_DOWN or key == 40):
            if selected_option < len(current_files) - 1:
                selected_option += 1
            else:
                selected_option = 0

            # file = current_dir + '/' + current_files[selected_option]
            # if os.path.isdir(file):
            #     future_dir = file
            # else:
            #     window3.addstr(2, 1, str(open(file, 'rb').read()))
                
            # window2.addstr(15, 1, "Down Key Works")
            refresh_win2(True, scroll=True)
        # Navigate up and down through the submenu options
        elif (key == curses.KEY_LEFT or key == 37):
            if previous_dir != None:
                prev_dir_name = previous_dir.split('/')[-1]
                current_dir = previous_dir
                if prev_dir_name == "":
                    previous_dir = None
                else:
                    previous_dir = os.path.dirname(current_dir)
                selected_option = preselected_option
                global win2_scroll
                win2_scroll = math.floor(selected_option - (curses.LINES / 2) + 3)
                if not win2_scroll >= 0:
                    win2_scroll = 0
            refresh_win2()
        elif (key == curses.KEY_RIGHT) or (key == 39) or (key == curses.KEY_ENTER) or (key == 10) or (key == 13):
            if os.path.isdir(future_dir) and len(os.listdir(future_dir)) > 0:
                previous_dir = current_dir
                current_dir = future_dir
                selected_option = 0
            refresh_win2()
        # Select the current option
        elif key == curses.KEY_BACKSPACE:
            # window2.addstr(len(previous_files) + 4, 1, 'You selected "{}" from the main menu and "{}" from the submenu'.format(previous_files[selected_option], current_files[selected_suboption]))
            # refresh_win2()
            window2.getch()
            break

    # window2.addstr(previous_dir)
    # window2.refresh()
    

    # window3.addstr(current_dir)
    # y_coord = 3
    # for file_name in current_files:
    #     y_coord += 1
    #     window3.addstr(2, 0, f"{y_coord}", h)
    #     if y_coord >= curses.LINES:
    #         pass
    #     else:
    #         window3.addstr(y_coord, 0, file_name)
        

    # window3.refresh()

    # window1.addstr(0, 0, "Test window 3")
    # window1.refresh()


    # input = window3.getch()

    # if input >= ord('1') and input <= ord(str(optioncount+1)):
    #     position = input - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
    # elif input == 258: # down arrow
    #     if position < optioncount:
    #         position += 1
    #     else: pos = 0
    # elif input == 259: # up arrow
    #     if position > 0:
    #         position += -1
    #     else: position = optioncount
    # elif input != ord('\n'):
    #     curses.flash()

    # screen.getch()

wrapper(main)