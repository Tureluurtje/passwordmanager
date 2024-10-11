import face_recognition
import cv2
import configparser
import io
import mysql.connector
import hashlib
import string
import base64
import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyboard
import time
import curses
import os
import random
import pyperclip
import pyotp
os.system('cls')
ConfigLocation = 'database~2024-05-18~arthu.ini'
config = configparser.ConfigParser()
config.read(ConfigLocation)
mydb = mysql.connector.connect(
    host=config.get('dblogin', 'host'),
    user=config.get('dblogin', 'user'),
    password=config.get('dblogin', 'password'),
    database=config.get('dblogin', 'db')
)
mycursor = mydb.cursor()
class terminal:
    def print_text(stdscr, text):
        curses.curs_set(0)
        # Clear the screen
        stdscr.clear()

        # Get the dimensions of the window
        max_y, max_x = stdscr.getmaxyx()

        # Calculate the center coordinates for the text
        start_y = max_y // 2
        start_x = (max_x - len(text)) // 2

        # Print the text in the middle of the window
        stdscr.addstr(start_y, start_x, text)

        # Refresh the screen to display changes
        stdscr.refresh()

        # Wait for user input
        stdscr.getch()
    def generate_password():
        # Define the character sets
        lowercase_chars = string.ascii_lowercase
        uppercase_chars = string.ascii_uppercase
        digits = string.digits
        special_chars = string.punctuation

        # Create a list of characters to choose from
        all_chars = lowercase_chars + uppercase_chars + digits + special_chars

        # Generate four groups of four characters
        password_parts = []
        for _ in range(4):
            part = ''.join(random.choices(all_chars, k=4))
            password_parts.append(part)

        # Join the parts with hyphens
        password = '-'.join(password_parts)

        return password
    def get_masked_input(stdscr, prompt):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        x = w // 2 - len(prompt) // 2
        y = h // 2
        stdscr.addstr(y, x, prompt)
        stdscr.refresh()

        curses.noecho()  # Turn off input echoing
        input_str = ""
        while True:
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                break
            elif key == ord('\b'):
                if input_str:  # Check if input_str is not empty
                    input_str = input_str[:-1]  # Remove the last character
            else:
                input_str += chr(key)  # Convert the key code to a character and append it to the input string
            stdscr.clear()
            stdscr.addstr(y, x, prompt)
            stdscr.addstr(y + 1, x, '*' * len(input_str))  # Display asterisks instead of characters
            stdscr.refresh()

        curses.echo()  # Turn on input echoing
        return input_str
    def clickable_text(normal_text, clickable_text, clickable_function, *args, **kwargs):
        def main(stdscr):
            # Initialize curses
            curses.curs_set(0)  # Hide the cursor
            stdscr.clear()      # Clear the screen

            # Function to execute when clickable text is clicked
            def on_click():
                terminal.clickable_function(*args, **kwargs)

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
            print_normal_text(stdscr, terminal.normal_text)

            # Print clickable text
            print_clickable_text(stdscr, terminal.clickable_text)

            # Refresh the screen to display changes
            stdscr.refresh()

            # Wait for user input to exit
            stdscr.getch()

        # Run the curses application
        curses.wrapper(main)
    def main(stdscr, prompt):
        password = terminal.get_masked_input(stdscr, prompt)
        return password

    def get_password(stdscr, prompt):
        curses.curs_set(0)  # Hide cursor
        password = terminal.main(stdscr, prompt)
        stdscr.refresh()
        return password
    def get_input(stdscr, prompt):
        curses.curs_set(0)
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        x = w//2 - len(prompt)//2
        y = h//2
        stdscr.addstr(y, x, prompt)
        stdscr.refresh()
        curses.echo()  # Turn on input echoing
        input_str = stdscr.getstr(y + 1, x).decode(encoding="utf-8")
        curses.noecho()  # Turn off input echoing
        return input_str
    def print_menu(stdscr, selected_row_idx, menu):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        stdscr.border()
        for idx, option in enumerate(menu):
            x = w//2 - len(option)//2
            y = h//2 - len(menu)//2 + idx
            if idx == selected_row_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, x, option)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, x, option)

        stdscr.refresh()
    def text_menu(stdscr, menu):
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

        current_row = 0

        terminal.print_menu(stdscr, current_row, menu)

        while 1:
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(menu)-1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return menu[current_row]
            terminal.print_menu(stdscr, current_row, menu)



    def copy(text):
        pyperclip.copy(text)      


def connect_to_database():
    '''Connects to an sql database.\n
    Use: connect_to_database(db)
    parameters:\n
    db - database that needs to be connected to'''
    return mydb
class logup:
    def login(username, password):
        db = connect_to_database()
        mycursor = db.cursor()
        masterpassword = hashlib.sha256(username.encode()+password.encode()).hexdigest()    
        checkLoginHisQuery = f"""
            SELECT COUNT(*) 
            FROM log 
            WHERE user = '{username}' 
            AND action = 'attemptLogin'
            AND verify = 0
            AND date >= DATE_SUB(NOW(), INTERVAL 10 HOUR_MINUTE)
            """
        mycursor.execute(checkLoginHisQuery)
        failed_attempts = mycursor.fetchone()[0]
        if failed_attempts > 5:
            print("Too many failed login attempts. Please try again in an 10 minutes from now.")
            exit()  
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        sql_query = f"SELECT * FROM users WHERE username = '{username.lower()}' AND password = '{hashed_password}'"
        mycursor.execute(sql_query)
        myresult = mycursor.fetchall()
        if myresult:
            return True, masterpassword
        else:
            return False
    def log(username, verify, logReason):
        db = connect_to_database()
        mycursor = db.cursor()
        now = datetime.datetime.now()
        query = f"INSERT INTO log(user, action, date, verify) VALUES(%s, %s, %s, %s)"
        values = (username, logReason, now, verify,)
        mycursor.execute(query, values)
        db.commit()
        

    def register(username, password):
        face_image_bytes = logup.capture_face_image()
        sql_query = "INSERT INTO users (username, password, face_image) VALUES (%s, %s, %s)"
        values = (username, password, face_image_bytes)
        mycursor.execute(sql_query, values)
        mydb.commit()
        print("Registered")
    def capture_face_image():
        # Capture image from the camera
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        # Convert the frame to RGB (face_recognition library expects RGB images)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Release the camera
        cap.release()
        cv2.destroyAllWindows()

        # Convert the RGB frame to a byte stream
        _, encoded_image = cv2.imencode('.jpg', rgb_frame)
        face_image_bytes = encoded_image.tobytes()

        return face_image_bytes
    def compare_faces(known_face_image_path, unknown_face_image_path):
        # Load the known face image and encode it
        known_image = face_recognition.load_image_file(known_face_image_path)
        known_face_encoding = face_recognition.face_encodings(known_image)[0]

        # Load the unknown face image and encode it
        unknown_image = face_recognition.load_image_file(unknown_face_image_path)
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]

        # Calculate the face distance between known and unknown face encodings
        face_distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding)

        # Convert face distance to similarity percentage (smaller distance = higher similarity)
        max_distance = 1.0
        similarity_percent = (max_distance - face_distance[0]) * 100.0 / max_distance

        return similarity_percent
    def capture_and_compare(known_face_image_path):
        # Capture image from the camera
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        # Convert the frame to RGB (face_recognition library expects RGB images)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the RGB frame to a byte stream
        _, encoded_image = cv2.imencode('.jpg', rgb_frame)
        unknown_image_bytes = io.BytesIO(encoded_image)

        # Compare faces
        similarity_percent = logup.compare_faces(known_face_image_path, unknown_image_bytes)

        # Release the camera
        cap.release()
        cv2.destroyAllWindows()

        return similarity_percent
    def facereg(imagepath=None):
        if imagepath is None:
            return print("No image path provided")
        similarity_percent = logup.capture_and_compare(imagepath)
        return similarity_percent
    def login_with_face(face_image_bytes):
        # Load the user's face image and encode it
        unknown_image = face_recognition.load_image_file(io.BytesIO(face_image_bytes))
        unknown_face_encodings = face_recognition.face_encodings(unknown_image)
        if len(unknown_face_encodings) > 0:
            unknown_face_encoding = unknown_face_encodings[0]
        else:
            print("No face detected in the image.")
        # Retrieve the stored face encodings from the database
        mycursor.execute("SELECT username, face_image FROM users")
        users = mycursor.fetchall()

        for user in users:
            username, stored_face_image_bytes = user

            # Load the known face image and encode it
            known_image = face_recognition.load_image_file(io.BytesIO(stored_face_image_bytes))
            known_face_encoding = face_recognition.face_encodings(known_image)[0]

            # Calculate the face distance between known and unknown face encodings
            face_distance = face_recognition.face_distance([known_face_encoding], unknown_face_encoding) #ERROR

            # Convert face distance to similarity percentage (smaller distance = higher similarity)
            max_distance = 1.0
            similarity_percent = (max_distance - face_distance[0]) * 100.0 / max_distance

            # If the similarity is above the threshold, log in the user
            if similarity_percent >= 60.0:
                print(f"Logged in as {username}")
                return

        print("Face not recognized")
   
class managepasswords:


    def addpass(user, masterpass):
        try:
            db = connect_to_database()
            mycursor = db.cursor()
            name = curses.wrapper(terminal.get_input, "Please enter the name of the password: ")
            action = curses.wrapper(terminal.text_menu, ['random password', 'custom password'])
            if action.lower() == 'random password':
                password = terminal.generate_password()
            else:
                password = curses.wrapper(terminal.get_password, prompt="Please enter the password: ")
            def generate_key(master_password):
                salt = b'salt_'  # You should generate a secure salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,  # You can adjust the number of iterations based on your security needs
                    backend=default_backend()
                )
                key = kdf.derive(master_password.encode())
                key_base64 = base64.urlsafe_b64encode(key)
                return key_base64
            def encrypt_password(password, key_base64):
                f = Fernet(key_base64)
                encrypted_password = f.encrypt(password.encode())
                return encrypted_password
            encrypted_password = encrypt_password(password, generate_key(masterpass))
            query = "INSERT INTO passwords(user, namepass, encrypted_password) VALUES (%s, %s, %s)"
            values = (user, name, encrypted_password,)
            mycursor.execute(query, values)
            db.commit()
            logup.log(user, 1, 'attemptAddPass')
            terminal.clickable_text(('This is your password: '+password+'    |   press a key to return'), "Click to copy to clipboard", lambda: terminal.copy(password))
            loggedin(user.lower(), masterpass)
        except mysql.connector.Error as error:
            logup.log(user, 0, 'attemptAddPass')
            print(error)
    def view_password(stdscr, user, masterpass):
        curses.curs_set(0)  # Hide cursor

        try:
            db = connect_to_database()
            mycursor = db.cursor()
            name = curses.wrapper(terminal.get_input, "Please enter the name of the password: ")
            query = "SELECT user, namepass, encrypted_password FROM passwords WHERE user = %s And namepass = %s"
            values = (user, name,)
            mycursor.execute(query, values)
            myresult = mycursor.fetchall()

            def generate_key(master_password):
                salt = b'salt_'  # You should generate a secure salt
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,  # You can adjust the number of iterations based on your security needs
                    backend=default_backend()
                )
                key = kdf.derive(master_password.encode())
                key_base64 = base64.urlsafe_b64encode(key)
                return key_base64

            def decrypt_password(encrypted_password, key_base64):
                f = Fernet(key_base64)
                decrypted_password = f.decrypt(encrypted_password)
                return decrypted_password.decode()

            if myresult:
                for row in myresult:
                    encrypted_password = row[2]
                    key_base64 = generate_key(masterpass)
                    decrypted_password = decrypt_password(encrypted_password, key_base64)
                    stardecrypted_password = '*'*len(decrypted_password)

                    # Clear the screen
                    stdscr.clear()

                    # Calculate position for printing
                    rows, cols = stdscr.getmaxyx()
                    y_center = rows // 2
                    x_center = (cols - len(f"User: {row[0]}")) // 2

                    stdscr.addstr(y_center - 2, x_center, f"User: {row[0]}")
                    stdscr.addstr(y_center - 1, x_center, f"Name: {row[1]}")
                    stdscr.addstr(y_center, x_center, f"Password: {stardecrypted_password} | Press s to show the password and h to hide it again, to return type e")
                    stdscr.refresh()

                    while True:
                        if keyboard.is_pressed("s"):
                            stdscr.addstr(y_center, x_center, " " * cols)  # Clear the line
                            stdscr.addstr(y_center, x_center, f"Password: {decrypted_password} | Press s to show the password and h to hide it again, to return type e")
                            stdscr.refresh()
                        elif keyboard.is_pressed("h"):
                            stdscr.addstr(y_center, x_center, " " * cols)  # Clear the line
                            stdscr.addstr(y_center, x_center, f"Password: {stardecrypted_password} | Press s to show the password and h to hide it again, to return type e")
                            stdscr.refresh()
                        elif keyboard.is_pressed("e"):
                            stdscr.addstr('\n')
                            stdscr.refresh()
                            time.sleep(1)
                            logup.log(user, 1, 'attemptViewPass')
                            loggedin(user.lower(), masterpass)
            else:
                logup.log(user, 0, 'attemptViewPass')
                stdscr.addstr("Password not found.")
                stdscr.refresh()

        except mysql.connector.Error as err:
            logup.log(user, 0, 'attemptViewPass')
            stdscr.addstr(f"Error accessing database: {err}")
            stdscr.refresh()
    def deletepass(user, masterpass):
        try:
            db = connect_to_database()
            mycursor = db.cursor()
            name = curses.wrapper(terminal.get_input, "Please enter the name of the password: ")
            query = "DELETE FROM passwords WHERE user = %s And namepass = %s"
            values = (user, name,)
            mycursor.execute(query, values)
            db.commit()
            print("Password deleted")
            logup.log(user, 1, 'attemptDeletePass')
            loggedin(user.lower(), masterpass)
        except mysql.connector.Error as err:
            logup.log(user, 0, 'attemptDeletePass')
            print(f"Error accessing database: {err}")


def loggedin(user, masterpass):
    menu = ['add password', 'view password', 'delete password', 'exit']
    action = curses.wrapper(terminal.text_menu, menu)
    os.system('cls')
    if action == 'add password':
        managepasswords.addpass(user, masterpass)
    elif action == 'view password':
        curses.wrapper(managepasswords.view_password, user, masterpass)
    elif action == 'delete password':
        managepasswords.deletepass(user, masterpass)
    elif action == 'exit':
        print("Exiting program...")
        time.sleep(1)
        exit()
    else:
        print("Invalid input")
        print('Try again')
        loggedin(user, masterpass)







def startprogram():
    menu = ['login', 'register', 'exit']
    asklogin = curses.wrapper(terminal.text_menu, menu)	
    if asklogin.lower() == 'login':
        logReason = 'attemptLogin'
        userName = curses.wrapper(terminal.get_input, "Please enter your username: ")
        password = curses.wrapper(terminal.get_password, "Please enter your password: ")
        try:
            logged, masterpassword = logup.login(userName, password)
        except TypeError:
            logged = False
        if logged:
            #face_image_bytes = capture_face_image() #TODO 
            #login_with_face(face_image_bytes)
            verify = 1
            logup.log(userName, verify, logReason)
            loggedin(userName.lower(), masterpassword)
        else:
            verify = 0
            logup.log(userName, verify, logReason)
            print("Not logged in\nUsername or password incorrect")
            print('Exiting...')
            exit()
    elif asklogin.lower() == 'exit':
        exit()
    elif asklogin.lower() == 'register':
        userName = curses.wrapper(terminal.get_input, "Please enter your username: ")
        password = curses.wrapper(terminal.get_password, prompt="Please enter your password: ")
        passwordconfirm = curses.wrapper(terminal.get_password, prompt="Please confirm your password: ")
        if password == passwordconfirm:
            logup.register(userName, password)
        else:
            print("Passwords do not match")
            print('Try again')
            startprogram()
    else:
        print("Invalid input")
        print('Try again')
        startprogram()   

        
if __name__ == "__main__":
    startprogram()



