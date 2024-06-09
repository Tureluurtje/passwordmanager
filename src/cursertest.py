import curses

def print_prompt(stdscr, input_prompt):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    # Add a border around the screen
    stdscr.border()

    # Print input prompt with styling
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(h//2 - 2, w//2 - len(input_prompt)//2, input_prompt)
    stdscr.attroff(curses.color_pair(1))

    stdscr.refresh()

def main(stdscr):
    curses.curs_set(1)  # Show cursor
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Set colors for input prompt

    input_prompt = "Enter something:"
    print_prompt(stdscr, input_prompt)

    # Calculate the position for user input
    h, w = stdscr.getmaxyx()
    input_y = h // 2
    input_x = w // 2 - len(input_prompt) // 2 + len(input_prompt) + 1

    curses.echo()  # Enable echoing of keystrokes
    stdscr.move(input_y, input_x)  # Move cursor to input position
    user_input = stdscr.getstr().decode('utf-8')  # Get user input

    return user_input

user_input = curses.wrapper(main)
print("You entered:", user_input)
