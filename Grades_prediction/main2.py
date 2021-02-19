import mysql.connector as mysql
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import pickle
import scipy.stats as ss
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold
from sklearn.metrics import f1_score, plot_confusion_matrix
from sklearn.linear_model import LinearRegression, LogisticRegressionCV, LogisticRegression
from sklearn.pipeline import make_pipeline

database = input("Which database to look at? : ")  # choosing which database to access
db = mysql.connect(host='localhost', user='Ashwin', password='3431', database=database)  # initializing
cursor = db.cursor(buffered=True)  # cursor


def grades(test_type, test_amount, max_mark, weightage, pass_percent, final_test_name, n=1000, graphs=False):  # grades generator
    """Func that generates train/test data for the classifier/regressor and returns the trained classifer/regressor"""
    df = pd.DataFrame(index=range(1, n+1))  # making the dataframe and generating dummy marks
    df.index.name = 'Student'
    print("\nGenerating mock data\n")
    for x in range(len(test_type)):
        m = max_mark[x]  # storing max marks for each type of test
        if test_amount[x] > 1:  # generating random marks in marking range with a gaussian weight distribution to each mark
            # mew = 65% of max mark and sigma = a third of max mark
            for y in range(1, test_amount[x] + 1):
                df[f"{test_type[x]} {y}"] = [round(x) for x in (ss.truncnorm.rvs(((0 - int(m * 0.65)) / (m//3)),
                                                                                 ((m - int(m * 0.65)) / (m//3)),
                                                                                 loc=round(m * 0.65, 0), scale=(m//3), size=n))]
        else:
            for y in range(1, test_amount[x] + 1):
                df[f"{test_type[x]}"] = [round(x) for x in (ss.truncnorm.rvs(((0 - int(m * 0.65)) / (m//3)),
                                                                             ((m - int(m * 0.65)) / (m//3)),
                                                                             loc=round(m * 0.65, 0), scale=(m//3), size=n))]

    # calculating total grade weight weightage
    df['Total %'] = [0] * len(df)
    for x in range(len(test_type)):
        df['Total %'] += round((df.filter(regex=test_type[x]).sum(axis=1) / (test_amount[x] * max_mark[x])) * weightage[x], 2)

    # determining pass/fail
    df['Pass/Fail'] = ["Pass" if x >= pass_percent else "Fail" for x in df['Total %']]
    print("Generated mock data!\n")

    print(f"\nStudents passed -> {len(df[df['Pass/Fail'] == 'Pass'])}\
    \nStudents Failed -> {len(df[df['Pass/Fail'] == 'Fail'])}\n")

    X = df.drop(['Pass/Fail', 'Total %', 'final'], axis=1)
    y = df[['Pass/Fail', 'Total %']].copy()
    y['Pass/Fail'] = LabelEncoder().fit_transform(y['Pass/Fail'])

    print("Creating and fitting models\n")
    # making train and test data for models
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=y['Pass/Fail'])

    # passing probability predictor
    passfail = make_pipeline(StandardScaler(), LogisticRegressionCV(Cs=np.arange(0.1, 0.6, 0.1),
                                                                    cv=RepeatedStratifiedKFold(n_splits=10, random_state=7),
                                                                    max_iter=1000, n_jobs=-1, refit=True,
                                                                    random_state=7,
                                                                    class_weight='balanced')).fit(X_test,
                                                                                                  y_test['Pass/Fail'])

    if graphs == True:
        for x in range(len(test_type)):
            if test_amount[x] > 1:  # plotting grade distribution for tests with more than one evaluation of that type
                if test_amount[x] % 2 != 0:
                    y = test_amount[x]+1
                else:
                    y = test_amount[x]

                fig = plt.figure(figsize=(10, 7), constrained_layout=True)
                grid = gs(nrows=int(y/2), ncols=2, figure=fig)
                for y in range(test_amount[x]):
                    ax = fig.add_subplot(grid[y])
                    sns.distplot(df.filter(regex=test_type[x]).iloc[:, y], fit=ss.norm, ax=ax, norm_hist=True, color='red',
                                 hist_kws=dict(edgecolor='black', align='right', color='red'),
                                 bins=max_mark[x]//2)
                    plt.xticks(size=10)
                    plt.yticks(size=12)
                    plt.xlabel('Marks', fontdict={'size': 13})
                    plt.ylabel('Density', fontdict={'size': 13})
                    plt.title(f"{test_type[x]} {y+1}", fontsize=14)
                    plt.tight_layout()
                fig.suptitle(f"Grade for {test_type[x]}", fontsize=15)
                grid.tight_layout(fig)
                if graphs == True:
                    plt.show()
            else:  # plotting grade distribution for singular evaluation test
                plt.figure(figsize=(8, 5))
                sns.distplot(df[test_type[x]], fit=ss.norm, norm_hist=True, color='red',
                             hist_kws=dict(edgecolor='black', align='right', color='red'),
                             bins=max_mark[x]//2)
                plt.title(f"Grade for {test_type[x]}", fontsize=14)
                plt.xlabel('Marks', fontdict={'size': 13})
                plt.xticks(size=12)
                plt.yticks(size=12)
                plt.ylabel('Density', fontdict={'size': 13})
                plt.tight_layout()
                plt.show()

        fig, ax = plt.subplots()
        plot_confusion_matrix(passfail, X_test, y_test['Pass/Fail'], labels=[0, 1],
                              display_labels=['Fail', 'Pass'], cmap='afmhot', ax=ax)
        plt.rcParams.update({'font.size': 18})
        ax.set_title('Confusion Matrix')
        plt.show()

    # final overall grade predictor
    overallgrade = make_pipeline(StandardScaler(), LinearRegression(n_jobs=-1)).fit(X_test, y_test['Total %'])
    print("Models created")

    print("LogisticRegressionCV classifer:-")
    print(f"Accuracy -> {round(passfail.score(X_test, y_test['Pass/Fail'])*100, 2)}%")
    print(f"f1_score -> {round(f1_score(y_test['Pass/Fail'], passfail.predict(X_test))*100, 2)}%\n")

    print("LinearRegression regressor:-")
    print(f"Accuracy -> {round(overallgrade.score(X_test, y_test['Total %'])*100, 2)}%")
    print("Models created")

    return passfail, overallgrade


def admin_session():
    while True:
        print("\nWelcome to the admin menu\n")
        print("1. View all tables")
        print("2. Create new student table")
        print("3. Add student to a student record")
        print("4. Delete student from student record")
        print("5. Create new teacher table")
        print("6. Add teacher to the teacher record")
        print("7. Delete teacher to the teacher record")
        print("8. Create subject table")
        print("9. Adding a subject to the subject table")
        print("10. Delete a subject")
        print("11. Logout")
        choice = input("Choice : ")

        if choice == '1':
            print("\nShowing all tables\n")
            cursor.execute("""SHOW tables""")
            tables = list(enumerate(cursor.fetchall(), start=1))
            print("TABLES\n")
            for table in tables:
                print(f"{table[0]}. {table[1][0]}")
            choice = input("Option : ")
            if int(choice) in [x[0] for x in tables]:
                # showing pandas view of sql table
                print(pd.read_sql(tables[int(choice)-1][1][0],
                                  con=create_engine(f"mysql://root:@localhost/{database}").connect()))
                print(f"Records in {tables[int(choice)-1][1][0]} shown\n")
            else:
                print("No valid option entered\n")
            print("\nAll tables shown\n")

        elif choice == '2':  # creating student account records table
            print("\nCreating new students table\n")
            enroll_year = input("Enter enrollment year : ")
            cursor.execute(f"SHOW TABLES LIKE 'students_{enroll_year}'")
            if len(cursor.fetchall()) > 0:
                cursor.execute(
                    f"CREATE TABLE `course_a`.`students_2019` (`student_id` INT NOT NULL AUTO_INCREMENT ,  `username` VARCHAR(20) NOT NULL ,  `password` VARCHAR(20) NOT NULL ,  `enroll_year` YEAR NOT NULL DEFAULT '{enroll_year}' ,    INDEX  `student_id` (`student_id`))")
                db.commit()
                print(f"Student table for {enroll_year} created\n")
            else:
                print("Student table for year {enroll_year} already exists\n")

        elif choice == '3':  # adding student to a record table
            print("\nAdding student to a student record\n")
            enroll_year = int(input("Enter enrollment year : "))
            cursor.execute(f"SHOW TABLES LIKE 'students_{enroll_year}'")
            if len(cursor.fetchall()) > 0:
                student_id = input("Enter username of student to add : ")
                cursor.execute(f"SELECT username FROM students_{enroll_year} WHERE username = '{student_id}'")
                if len(cursor.fetchall()) < 1:
                    cursor.execute(f"INSERT INTO students_{enroll_year} (username, password) VALUES ('{student_id}', 'pass')")
                    db.commit()
                    print(f"{student_id} has been added to students_{enroll_year}\n")
                else:
                    print(f"{student_id} already exists in students_{enroll_year}\n")
            else:
                print(f"Table records for enrollment year {enroll_year} does not exist\n")

        elif choice == '4':  # deleting student from a record table
            print("\nDeleting student from student record\n")
            enroll_year = int(input("Enter enrollment year : "))
            cursor.execute(f"SHOW TABLES LIKE 'students_{enroll_year}'")
            if len(cursor.fetchall()) > 0:
                student_id = input("Enter username of student to delete : ")
                cursor.execute(f"SELECT username FROM students_{enroll_year} WHERE username = '{student_id}'")
                if len(cursor.fetchall()) > 0:
                    cursor.execute(f"DELETE FROM students_{enroll_year} WHERE username = '{student_id}'")
                    db.commit()
                    print(f"{student_id} has been deleted from students_{enroll_year}\n")
                else:
                    print(f"{student_id} does not exist in students_{enroll_year}\n")
            else:
                print(f"Table records for enrollment year {enroll_year} does not exist\n")

        elif choice == '5':  # creating a teachers table
            print("\nCreating teacher table\n")
            cursor.execute("CREATE TABLE `course_a`.`teachers` ( `teacher_id` INT(11) NOT NULL AUTO_INCREMENT , `username` VARCHAR(20) NOT NULL , `password` VARCHAR(20) NOT NULL , PRIMARY KEY (`teacher_id`))")
            db.commit()
            print("New teacher table created\n")

        elif choice == '6':  # adding a teacher to the teacher record
            print("\nAdding a teacher to the teacher record\n")
            user = input("Enter username : ")
            passw = input("Enter password : ")
            cursor.execute(f"INSERT INTO teachers (username, password) VALUES ('{user}', '{passw}')")
            db.commit()
            print(f"{user} has been added as a teacher\n")

        elif choice == '7':  # deleting teacher from teachers table
            print("\nDeleting a teacher\n")
            user = input("Enter username of teacher to delete : ")
            cursor.execute(f"DELETE FROM teachers WHERE username = '{user}'")
            db.commit()
            print(f"{user} has been removed from the teachers table")

        elif choice == '8':  # creating subjects table
            print("\nCreating subjects table\n")
            cursor.execute("SHOW TABLES LIKE 'teachers'")
            if len(cursor.fetchall()) > 0:
                cursor.execute("DROP TABLE IF EXISTS subjects")
                db.commit()

                cursor.execute("CREATE TABLE `course_a`.`subjects` ( `subj_name` VARCHAR(255) NOT NULL , `test_types` TEXT NOT NULL , `test_amounts` TEXT NOT NULL , `max_mark` TEXT NOT NULL , `weightage` TEXT NOT NULL , `pass_threshold` INT(2) NOT NULL , `final_name` VARCHAR(30) NOT NULL , `teacher` VARCHAR(20) NOT NULL , `semester` INT(1) NOT NULL , PRIMARY KEY (`subj_name`))")
                db.commit()

                cursor.execute("ALTER TABLE subjects ADD FOREIGN KEY (teacher) REFERENCES teachers(username)")
                db.commit()
                print("New subjects table has been created\n")
            else:
                print("Create a teachers records table first\n")

        elif choice == '9':  # adding a subject
            print("\nAdding a subject\n")
            cursor.execute("SHOW TABLES")
            if 'subjects' in [x[0] for x in cursor.fetchall()]:
                subj_name = input("Enter name of subject : ")
                test_types = input("Enter types of tests (space seperated) : ")
                if len(test_types.split()) < 1:
                    print("Enter valid test types\n")
                    continue

                test_amounts = input(f"How many evaluations for each test? : ")
                if len(test_amounts.split()) != len(test_types.split()):
                    print("Enter valid corresponding test amounts\n")
                    continue

                max_mark = input(f"How many marks is each test type out of? : ")
                if len(max_mark.split()) != len(test_types.split()):
                    print("Enter valid corresponding test marks\n")
                    continue

                while True:
                    weightage = " ".join([str(float(x)/100)
                                          for x in input("What is the weightages of each type of test : ").split()])
                    if np.sum([float(x) for x in weightage.split()]) == 1.0 and len(weightage.split()) == len(test_types.split()):
                        break
                    else:
                        print("Make sure the weightage for all tests add up to 100 and are corresponding to the test type\n")
                        continue

                pass_percent = int(input("What is the overall subject passing percent? : "))/100

                while True:
                    final_test_name = input(f"Which of these tests {test_types} is the final test? : ")
                    if final_test_name in test_types.split():
                        break
                    else:
                        print("Make sure the name of the final test is enterred correctly!\n")
                        continue

                teacher_id = input("Enter teacher id : ")
                semester = int(input("Which semester is the subject in? : "))
                cursor.execute(
                    f"INSERT INTO subjects VALUES ('{subj_name}', '{test_types}', '{test_amounts}', '{max_mark}', '{weightage}' , {pass_percent}, '{final_test_name}', '{teacher_id}', {semester})")
                db.commit()
                print(f"{subj_name} has been added\n")

        elif choice == '10':
            print("\nDeleting a subject\n")

            subj_name = input("Enter subject to delete : ")
            cursor.execute(f"DELETE FROM subjects WHERE subj_name = '{subj_name}'")
            db.commit()
            print(f"{subj_name} has been removed\n")

        elif choice == '11':
            print("Logging out")
            break

        else:
            print("No valid option entered\n")


def admin_auth():  # checking if valid admin login
    print("\nAdmin Login\n")
    username, password = input("Enter username : ").strip(), input("Enter password : ").strip()
    if username == 'Ashwin' and password == '3431':
        admin_session()
    else:
        print("Invalid login details")


def main():
    while True:
        print("\nMain Menu\n")
        print("1. Log in as admin")
        print("2. Log in as student")
        print("3. Log in as teacher")
        print("4. Exit")
        choice = input("Choice : ")

        if choice == '1':
            admin_auth()

        elif choice == '4':
            print("Bye!")
            break


# war begins
main()
