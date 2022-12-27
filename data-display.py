import curses
from curses import wrapper
import math
import os
import logging

# Let there be 3 windows
# Window 1 shows the contents of the previous directory
# Window 2 displays the contents of the current directory
# Window 3 displays the contents of the currently selected directory in the second window (or the contents of the file if it's a file that is selected)

# These values manage the scroll location of window 1 and window 2
win1_scroll = 0
win2_scroll = 0
win3_scroll = 0
rotate = True

# first_data = {"key1": "Fruits", "key2": "Veggies","key3": "Meats",}
data = {"Fruits": ["apple", "pear"],"Veggies": ["carrot", "tomato"],"Meats": ["chicken", "fish"]}
data_info = {"fruits": ["peel", "eat"],"veggies": ["cook", "clean"],"meats": ["cook", "trim"]}

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
    padding = final_len - len(str)
    return " " + str.ljust(padding, ' ') + " "

def arrange_folder(folder, items):
    """Arranges the contents of a directory by putting the folders first, and the files next. The folders and files are separately sorted by name and combined"""
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
    """Displays the contents of a file in the chosen window."""
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
    logger = logging.getLogger(__file__)
    hdlr = logging.FileHandler(__file__ + ".log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)


    def refresh_win2(down=True, scroll=False):
        # Prevent scrolling if at the end of the menu
        if selected_option == len(second_data) - 1 and len(second_data) > curses.LINES - 2:
            global win2_scroll
            if win2_scroll == 0 or selected_option >= math.floor(curses.LINES / 2):
                win2_scroll = (len(second_data) - (curses.LINES - 1)) + 3
            window2.refresh(win2_scroll, 0, 0, window1Width, curses.LINES - 1, curses.COLS - 1)
        elif selected_option >= math.floor(curses.LINES / 2):
            # Rotate prevents the pad from scrolling twice at once
            global rotate
            stop_scrolling = False
            if selected_option >= (len(second_data) - (curses.LINES / 2) + 3):
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

    def display_window(window, windowHeight, windowWidth, window_data, selector):
        # Displays the contents of a directory in the chosen window with color styles
        y_coord = 0
        logger.info(f"Window Data: {window_data}")
        for i, option in enumerate(window_data):
            y_coord += 1
            # Add data to the pad/window as long as we don't pass the limit for adding data
            if y_coord <= windowHeight - 1: # curses.LINES - 2
                if i == selector:
                    window.addstr(y_coord, 1, expand_str(option, '', windowWidth), curses.A_REVERSE + curses.A_BOLD)
                else:
                    window.addstr(y_coord, 1, expand_str(option, '', windowWidth))
            else:
                pass
    
    
    curses.curs_set(0)
    curses.cbreak()

    # Tell the terminal to use the default colors (to allow using the white background) 
    curses.use_default_colors()
    curses.start_color()

    # Initialize all color pairs to be used in the program
    # curses.init_pair(1, curses.COLOR_WHITE, -1)

    # Create the first window (the window that shows the previous files)
    window1Width = math.floor(curses.COLS * 1.0/3.0)
    window1Height = 20000
    window1 = curses.newpad(window1Height, window1Width)

    # Create the second window (the window that shows the current directory and it's content)
    window2Width = math.floor(curses.COLS * 1.0/3.0)
    window2Height = 20000
    window2 = curses.newpad(window2Height, window2Width)

    # Create the third window (the window that shows the next directory files or the contents of a readable document)
    window3Width = math.floor(curses.COLS * 1.0/3.0)
    window3Height = 20000
    window3 = curses.newpad(window3Height, window3Width)

    screen.refresh()

    # current_dir = os.getcwd()
    # previous_dir = os.path.dirname(current_dir)
    preselected_option = 0
    selected_option = 0  # Keep track of the selected main menu option (the current directory)
    selected_suboption = 0  # Keep track of the selected option in window 3 (the next directory)


    while True:
        # Collect the data based on the selected option in the terminal
        first_data = list(data.keys())
        second_data = list(data.values())[preselected_option]
        third_data = data_info[first_data[preselected_option].lower()]
        
        # Erase all windows anytime changes are made to properly show changes
        window1.erase()
        window2.erase()
        window3.erase()
        

        # Print first_data in the first column and refresh
        display_window(window1, window1Height, window1Width, first_data, preselected_option)
        window1.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 2)

		# Print the data in second_data in the second column and refresh
        display_window(window2, window2Height, window2Width, second_data, selected_option)        
        refresh_win2()

        # Print the data (corresponding with the currently selected menu option on window1) on the third window and refresh
        display_window(window3, window3Height, window3Width, third_data, selected_suboption)
        window3.refresh(0, 0, 0, window1Width+window2Width, curses.LINES - 1, curses.COLS - 1)


        # Get user input
        key = screen.getch()

        # Move the highlighted menu entry up (in column 1) if the down key is pressed
        if key == curses.KEY_UP or key == 38:
            if preselected_option > 0:
                preselected_option -= 1
            else:
                preselected_option = len(first_data) - 1
            
            # Refresh the first window/column to properly reflect changes
            selected_option = 0
            window1.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 2)
            
        # Move the highlighted menu entry down (in column 1) if the down key is pressed
        elif (key == curses.KEY_DOWN or key == 40):
            if preselected_option < len(first_data) - 1:
                preselected_option += 1
            else:
                preselected_option = 0
            # Refresh the first window/column to properly reflect changes
            selected_option = 0
            window1.refresh(0, 0, 0, 0, curses.LINES - 1, curses.COLS - 2)            

        # Navigate up through the submenu options (in column 2)
        elif (key == curses.KEY_LEFT) or (key == 37):
            if selected_option < len(second_data) - 1:
                selected_option -= 1
            else:
                selected_option = 0
            # Refresh the second window
            refresh_win2(down=False, scroll=True)

        # Navigate down through the submenu options (in column 2)
        elif (key == curses.KEY_RIGHT) or (key == 39):
            if selected_option < len(second_data) - 1:
                selected_option += 1
            else:
                selected_option = 0
            # Refresh the second window
            refresh_win2(down=True, scroll=True)
        
        # If the escape key is pressed twice, quit the program
        elif (key == curses.KEY_BACKSPACE) or (key == 8):
            second_key = screen.getch()
            if (second_key == curses.KEY_BACKSPACE) or (second_key == 8):
                break

wrapper(main)