import curses
from curses import wrapper
import math
import os
import json

# Let there be 3 windows
# Their content is determined by the past, present and future directories

win1_scroll = 0
win2_scroll = 0
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
    padding = final_len - len(str) - 4
    return "  " + str + end_str.rjust(padding, ' ') + "  "

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

def main(screen):
    def refresh_win1(down=True):
        # Prevent scrolling if at the end of the menu
        if selected_option == len(previous_files) - 1:
            global win1_scroll
            if win1_scroll == 0:
                win1_scroll = (len(previous_files) - (curses.LINES - 1)) + 3
            window1.refresh(win1_scroll, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        elif selected_option >= math.floor(curses.LINES / 2):
            # Rotate prevents the pad from scrolling twice at once
            global rotate
            stop_scrolling = False
            if selected_option >= (len(previous_files) - (curses.LINES / 2) + 3):
                stop_scrolling = True
            # Revert scrolling to original state when the highlighted item loops back to the start
            if win1_scroll >= math.floor(curses.LINES / 2) and selected_option <= math.floor(curses.LINES / 2):
                win1_scroll = 0
            # Go up if the up signal is received, and vice-versa
            if rotate and not stop_scrolling:
                if down:
                    win1_scroll += 1
                else:
                    win1_scroll -= 1
            rotate = not rotate
            # Update the screen to scroll
            window1.refresh(win1_scroll, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        else:
            # Udate the screen normally if scrolling is not needed
            window1.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)

    # Clear screen
    # screen.clear()
    curses.curs_set(0)
    curses.cbreak()
    # curses.init_pair(1, curses.COLOR_WHITE, -1)
    curses.use_default_colors()
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

    window1Width = math.floor(curses.COLS * 1.0/3.0)
    window1Height = 300
    # window1 = curses.newwin(window1Height, window1Width, 0, 0)
    window1 = curses.newpad(window1Height, window1Width)

    window2Width = window1Width
    window2Height = 300
    # window2 = curses.newwin(window2Height, window2Width, 0, window1Width)
    window2 = curses.newpad(window2Height, window2Width)

    window3Width = window2Width
    window3Height = curses.LINES
    # window3 = curses.newwin(window3Height, window3Width, 0, window2Width+window1Width)
    window3 = curses.newpad(window3Height, window3Width)

    screen.refresh()
    # window1.bkgd(h)
    # window2.bkgd(h)
    # window3.bkgd(h)

    current_dir = os.getcwd()
    previous_dir = os.path.dirname(current_dir)
    # previous_files = previous_files[1:20]
    selected_option = 0  # Keep track of the selected main menu option
    selected_suboption = 0  # Keep track of the selected submenu option

    while True:
        current_files = arrange_folder(current_dir, os.listdir(current_dir))
        previous_files = arrange_folder(previous_dir, os.listdir(previous_dir))
        # Erase all windows anytime changes are made to properly show changes
        window1.erase()
        window2.erase()
        window3.erase()

		# Print the main menu options
        y_coord = 3
        window1.addstr(1, 2, 'Menu:')
        # window1.addstr(2, 2, f'{math.floor(curses.COLS/3)}')
        for i, option in enumerate(previous_files):
            y_coord += 1
            file_path = previous_dir + '/' + option
            file_size = os.path.getsize(file_path)
            file_is_dir = False
            if os.path.isdir(file_path):
                file_is_dir = True
                append_str = str(len(os.listdir(file_path)))
            else:
                append_str = convert_bytes(file_size)
            if y_coord <= window1Height: # curses.LINES - 2
                if i == selected_option:
                    color_scheme = get_color_scheme(option, file_is_dir, highlight=True)
                    window1.addstr(y_coord, 0, expand_str(option, append_str, window1Width), color_scheme)
                else:
                    color_scheme = get_color_scheme(option, file_is_dir, highlight=False)
                    window1.addstr(y_coord, 0, expand_str(option, append_str, window1Width), color_scheme)
            else:
                pass
        
        refresh_win1()

        # Print the children of the parent directory
        y_coord2 = 3
        if type(current_files) == list:
            window2.addstr(1, 2, f'Submenu: {current_dir}')
            for i, option in enumerate(current_files):
                y_coord2 += 1
                file_path = current_dir + '/' + option
                file_size = os.path.getsize(file_path)
                file_is_dir = False
                if os.path.isdir(file_path):
                    file_is_dir = True
                    append_str = str(len(os.listdir(file_path)))
                else:
                    append_str = convert_bytes(file_size)
                if y_coord2 <= window2Height: # curses.LINES - 2
                    if i == selected_suboption:
                        color_scheme = get_color_scheme(option, file_is_dir, highlight=True)
                        window2.addstr(y_coord2, 0, expand_str(option, append_str, window2Width), color_scheme)
                    else:
                        color_scheme = get_color_scheme(option, file_is_dir, highlight=False)
                        window2.addstr(y_coord2, 0, expand_str(option, append_str, window2Width), color_scheme)
                else:
                    pass
        else:
            window2.addstr(y_coord2, 0, current_files)
        window2.refresh(0, 0, 0, window1Width, curses.LINES - 1, curses.COLS - 1)
        window3.refresh(0, 0, 0, window1Width+window2Width, window3Height, window3Width+window2Width+window1Width)

        # Get user input
        key = screen.getch()

        # Navigate up and down through the main menu options
        if key == curses.KEY_UP or key == 38:
            if selected_option > 0:
                selected_option -= 1
            else:
                selected_option = len(previous_files) - 1

            file = previous_dir + '/' + previous_files[selected_option]
            if os.path.isdir(file):
                current_dir = file
            # else:
            #     window2.addstr(3, 2, str(open(file, 'rt', errors='ignore').read()))
            # window2.refresh(0, 0, 0, window1Width, window2Height, window2Width+window1Width)

            window1.addstr(curses.LINES - 1, 1, "Up Key works")
            refresh_win1(False)
            
        elif (key == curses.KEY_DOWN or key == 40):
            if selected_option < len(previous_files) - 1:
                selected_option += 1
            else:
                selected_option = 0

            file = previous_dir + '/' + previous_files[selected_option]
            if os.path.isdir(file):
                current_dir = file
            # else:
            #     window2.addstr(2, 1, str(open(file, 'rb').read()))
                
            window1.addstr(15, 1, "Down Key Works")
            refresh_win1(True)
        # Navigate up and down through the submenu options
        elif (key == curses.KEY_LEFT or key == 37) and selected_suboption > 0:
            selected_suboption -= 1
        elif (key == curses.KEY_RIGHT or key == 39) and selected_suboption < len(current_files) - 1:
            selected_suboption += 1
        # Select the current option
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            window1.addstr(len(previous_files) + 4, 1, 'You selected "{}" from the main menu and "{}" from the submenu'.format(previous_files[selected_option], current_files[selected_suboption]))
            refresh_win1()
            window1.getch()
            break

    # window1.addstr(previous_dir)
    # window1.refresh()
    

    # window2.addstr(current_dir)
    # y_coord = 3
    # for file_name in current_files:
    #     y_coord += 1
    #     window2.addstr(2, 0, f"{y_coord}", h)
    #     if y_coord >= curses.LINES:
    #         pass
    #     else:
    #         window2.addstr(y_coord, 0, file_name)
        

    # window2.refresh()

    # window3.addstr(0, 0, "Test window 3")
    # window3.refresh()


    # input = window2.getch()

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