import curses

def curses_wrapper(normal_text, clickable_text, clickable_function):
    def main(stdscr):
        # Initialize curses
        curses.curs_set(0)  # Hide the cursor
        stdscr.clear()      # Clear the screen

        # Function to execute when clickable text is clicked
        def on_click():
            clickable_function()

        # Function to print normal text
        def print_normal_text(stdscr, text):
            # Clear the screen
            stdscr.clear()

            # Get the dimensions of the window
            max_y, max_x = stdscr.getmaxyx()

            # Calculate the center coordinates for the text
            start_y = max_y // 2 - 1
            start_x = (max_x - len(text)) // 2

            # Print the text in the middle of the window
            stdscr.addstr(start_y, start_x, text)

            # Refresh the screen to display changes
            stdscr.refresh()

        # Function to print clickable text
        def print_clickable_text(stdscr, text):
            # Get the dimensions of the window
            max_y, max_x = stdscr.getmaxyx()

            # Calculate the center coordinates for the text
            start_y = max_y // 2
            start_x = (max_x - len(text)) // 2

            # Print the text
            stdscr.addstr(start_y, start_x, text, curses.A_UNDERLINE)

            # Listen for mouse events
            curses.mousemask(curses.BUTTON1_CLICKED)

            while True:
                # Get mouse event
                event = stdscr.getch()

                # Check for mouse click event
                if event == curses.KEY_MOUSE:
                    _, mouse_x, mouse_y, _, _ = curses.getmouse()

                    # Check if clicked on the clickable text
                    if start_y <= mouse_y <= start_y and start_x <= mouse_x <= start_x + len(text):
                        on_click()
                        break

        # Print normal text
        print_normal_text(stdscr, normal_text)

        # Print clickable text
        print_clickable_text(stdscr, clickable_text)

        # Refresh the screen to display changes
        stdscr.refresh()

        # Wait for user input to exit
        stdscr.getch()

    # Run the curses application
    curses.wrapper(main)

# Example usage
def my_function():
    print("Clickable text clicked!")

curses_wrapper("Normal Text", "Click Me!", my_function)
