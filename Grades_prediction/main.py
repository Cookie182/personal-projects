import mysql.connector as mysql
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold
from sklearn.metrics import f1_score, plot_confusion_matrix
from sklearn.linear_model import LinearRegression, LogisticRegressionCV, LogisticRegression
from sklearn.pipeline import make_pipeline

db = mysql.connect(host='localhost', user='root', password='', database='course_A')  # initializing
cursor = db.cursor(buffered=True)  # cursor


def teacher_session():  # teacher panel
    print("\nTeacher menu\n")
    print("1. Review grades")
    print("2. ")


def teacher_auth():  # checking if valid teacher login
    print("\nTeacher Login\n")
    user, passw = input("Enter username : ").strip(), input("Enter password : ").strip()
    cursor.execute("SELECT * from users WHERE username = %s and password = %s and permission ='teacher'", (user, passw))
    if cursor.rowcount == 0:
        print("Login not recognized\n")
    else:
        teacher_session()


def admin_session():  # admin panel
    print("\nAdmin menu\n")
    while 1:
        print("1. Register new account")
        print("2. Delete existing account")
        print("3. Add a subject")
        print("4. Show subjects")
        print("5. Delete a subject")
        print("6. Logout")
        choice = input("Option : ")
        if choice == '1':  # registering new account
            print("\nRegister new account")
            user, passw, perm = input("Enter username : "), input("Enter password : "), input("Enter permission : ")
            cursor.execute("INSERT INTO users (username, password, permission) VALUES (%s, %s, %s)", (user, passw, perm))
            db.commit()
            print(f"{user} has been registered as a {perm}\n")

        elif choice == '2':  # deleting existing account
            print("\nDeleting exiting account")
            user = input("Enter username : ")
            cursor.execute("DELETE FROM users WHERE username = %s", (user,))
            if cursor.rowcount == 0:
                print(f"{user} not found\n")
            else:
                db.commit()
                print(f"{user} has been deleted\n")

        elif choice == '3':  # dynamically creating grade sheet for a subject
            print("\nAdding a subject\n")

            # gathering subject details
            subj_name = input("Name of subject : ")
            test_type = tuple(input("Types of tests : ").split())
            test_amount = tuple(int(input(f"How many evaluations for {x}? : ")) for x in test_type)
            test_marks = tuple(int(input(f"How many marks is {x} out of? : ")) for x in test_type)
            while True:
                weightage = tuple(float(input(f"What is the weightage for {x}?: "))/100 for x in test_type)
                if np.sum(weightage) == 1.0:
                    break
                else:
                    print("Make sure the weightage for all tests add up to 1.0!\n")
            pass_percent = int(input("What is the overall subject passing percent? : "))
            while True:
                final_test_name = input(f"Which of these tests {test_type} is the final test?: ")
                if final_test_name in test_type:
                    break
                else:
                    print("Make sure the name of the final test is enterred correctly!\n")

            # dynamically creating sql table
            df = pd.DataFrame(index=range(1, int(input("How many students? : "))))
            for x in range(len(test_type)):
                if test_amount[x] > 1:
                    for y in range(1, test_amount[x]+1):
                        df[f"{test_type[x]} {y}"] = [0] * len(df)
                else:
                    df[test_type[x]] = [np.nan] * len(df)
            df.to_sql(con=create_engine("mysql://root:@localhost/course_a").connect(), name=subj_name)
            print(f"Grade sheet for {subj_name} created\n ")

        elif choice == '4':  # show tables
            print("\nShowing subjects\n")
            cursor.execute("SHOW tables")
            for table in cursor.fetchall():
                print(table[0])
            print('')

        elif choice == '5':  # drop a table
            print("\nDelete subject\n")
            table = input("Table to delete : ")
            cursor.execute("DROP TABLE " + table)
            db.commit()
            print(f"{table} has been deleted\n")

        elif choice == '6':  # logging out
            print("Logging out\n")
            break
        else:
            print("No valid input entered\n")


def admin_auth():  # checking if valid admin login
    print("\nAdmin Login\n")
    username, password = input("Enter username : ").strip(), input("Enter password : ").strip()
    if username == 'Ashwin' and password == '3431':
        admin_session()
    else:
        print("Invalid login details")


def main():
    while 1:
        # main opening screen before login
        print("Welcome to the college system\n")
        print("1. Login as student")
        print("2. Login as teacher")
        print("3. Login as admin")
        print("4. Exit")

        choice = input("Option : ")
        if choice == '1':
            print("Logging in as student")
        elif choice == '2':
            teacher_auth()
        elif choice == '3':
            admin_auth()
        elif choice == '4':
            print("Bye!")
            break
        else:
            print("Valid input has not been entered\n")


main()
