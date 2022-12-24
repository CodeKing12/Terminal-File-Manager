import curses

def main(stdscr):
	# Clear the screen
	stdscr.clear()

	# Initialize the menu options
	menu_options = ['Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5']
	submenu_options = [['Suboption 1', 'Suboption 2', 'Suboption 3'],
					   ['zsdsfd 1', 'ffsd 2', 'sfs 3'],
					   ['affsvs 1', 'lkn 2', 'Suboption 3'],
					   ['42 1', 'ob 2', 'ojb 3'],
					   ['Suboption 1', 'uityc 2', 'jgu  3']]
	selected_option = 0  # Keep track of the selected main menu option
	selected_suboption = 0  # Keep track of the selected submenu option

	# Display the menu
	while True:
		# Print the main menu options
		stdscr.addstr(1, 1, 'Menu:')
		for i, option in enumerate(menu_options):
			stdscr.move(i + 2, 1)  # Move the cursor to the position where the option should be printed
			if i == selected_option:
				stdscr.addstr(option, curses.A_REVERSE)
			else:
				stdscr.addstr(option)

		# Print the submenu options
		stdscr.addstr(1, 30, 'Submenu:')
		for i, option in enumerate(submenu_options[selected_option]):
			stdscr.move(i + 2, 30)  # Move the cursor to the position where the option should be printed
			if i == selected_suboption:
				stdscr.addstr(option, curses.A_REVERSE)
			else:
				stdscr.addstr(option)

		# Get user input
		key = stdscr.getch()
		
		# Navigate up and down through the main menu options
		if key == curses.KEY_UP and selected_option > 0:
			selected_option -= 1
		elif key == curses.KEY_DOWN and selected_option < len(menu_options) - 1:
			selected_option += 1
		# Navigate up and down through the submenu options
		elif key == curses.KEY_LEFT and selected_suboption > 0:
			selected_suboption -= 1
		elif key == curses.KEY_RIGHT and selected_suboption < len(submenu_options[selected_option]) - 1:
			selected_suboption += 1
		# Select the current option
		elif key == curses.KEY_ENTER or key == 10 or key == 13:
			stdscr.addstr(len(menu_options) + 2, 1, 'You selected "{}" from the main menu and "{}" from the submenu'.format(menu_options[selected_option], submenu_options[selected_option][selected_suboption]))
			stdscr.refresh()
			stdscr.getch()
			break

curses.wrapper(main)
