import configparser
import mysql.connector
import time
def connect_to_db():
    config = configparser.ConfigParser()
    config.read(r'C:\1Coding\1python\Projects\smallProjects\frontenddatabase\database.ini')
    mydb = mysql.connector.connect(
        host=config.get('dblogin', 'host'),
        user=config.get('dblogin', 'user'),
        password=config.get('dblogin', 'password'),
        database=config.get('dblogin', 'db')
    )
    return mydb
def search_db():
    while True:
        try:
            searchpass = input("Enter the password you want to search for: ")
            start = time.time()
            mydb = connect_to_db()
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT * FROM `leakedpasswords` WHERE password='{searchpass}';")
            myresult = mycursor.fetchall()
            end = time.time()
            for z in 'a':           
                for x in myresult:
                    print(f'{myresult.index(x)+1}: {x[0]}')
                print(f'duration: {round(end-start,2)} seconds')
        except mysql.connector.Error as err:
            print("Error:", err)
            break
if __name__ == "__main__":
    search_db()
