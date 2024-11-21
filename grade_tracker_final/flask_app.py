#Task6 понять почему можно добавлять одинаковые user_name хотя используется модификатор PRIMARY KEY
#Task4 добавить запись логов ошибок в текстовый файл
#Task7 у админов создаваемых сейчас автоматически одинаковые id, следует это исправить
from flask import Flask, request, render_template, jsonify
import sqlite3
from datetime import datetime

def datestr(type):
    if type == "string":
        datestring = datetime.now().strftime("%d/%m/%Y")
        return datestring
    if type == "date":
        return datetime.now()


class DatabaseManager:
    def __init__(self, database_file):
        self.database_file = database_file

    def initialize_database(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
            
                #**Пользователи**: хранит имена пользователей, пароли, электронную почту, номер телефона, адрес.
                # SQL запрос для создания таблицы users, если она не существует
                create_users_table_query = '''CREATE TABLE IF NOT EXISTS users (
                                            user_id INT,
                                            user_name VARCHAR,
                                            full_name VARCHAR,
                                            user_status VARCHAR,
                                            password VARCHAR,
                                            email VARCHAR,
                                            phone_number VARCHAR,
                                            adress VARCHAR,
                                            PRIMARY KEY (user_id, user_name))'''
                cursor.execute(create_users_table_query)

                # **Оценки**: содержит название курса, оценку, дату и имя преподавателя.
                # SQL запрос для создания таблицы courses, если она не существует
                create_courses_table_query = '''CREATE TABLE IF NOT EXISTS courses (
                                                course_id INT PRIMARY KEY,
                                                course_name VARCHAR,
                                                lecturer_id INT,
                                                FOREIGN KEY (lecturer_id) REFERENCES users(user_id))'''
                cursor.execute(create_courses_table_query)
                
                # SQL запрос для создания таблицы grades, если она не существует
                create_grades_table_query = '''CREATE TABLE IF NOT EXISTS grades (
                                                course_id INT,
                                                student_id INT,
                                                grade_date DATE,
                                                lecturer_id INT,
                                                grade INT)'''
                cursor.execute(create_grades_table_query)
                # SQL запрос для создания таблицы logs, если она не существует
                create_logs_table_query = '''CREATE TABLE IF NOT EXISTS logs (
                                                date DATE,
                                                action VARCHAR,
                                                success BIT)'''
                cursor.execute(create_logs_table_query)

                connection.commit()
        except sqlite3.Error as e:
            print("Error initializing database: ", e)
    
    def get_max_user_id(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()

                # SQL запрос для получения максимального user_id
                select_max_user_id_query = '''SELECT MAX(user_id) FROM users'''
                cursor.execute(select_max_user_id_query)
                result = cursor.fetchone()[0]

                if result:
                    return result
                else:
                    return 0
        except sqlite3.Error as e:
            print("Error getting max client id: ", e)
            return 0

    def get_user_by_name(self, user_name):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_user_query = '''SELECT * FROM users WHERE user_name = ?'''
                cursor.execute(select_user_query, (user_name,))
                user = cursor.fetchone()
                return user
        except sqlite3.Error as e:
            print("Error getting user by name: ", e)
            return None


    def get_user_id_by_full_name(self, full_name):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()

                select_user_id_query = '''SELECT user_id FROM users WHERE full_name = ?'''
                cursor.execute(select_user_id_query, (full_name,))
                result = cursor.fetchone()

                if result:
                    return result[0]
                else:
                    return None
        except sqlite3.Error as e:
            print("Error getting user id by full name: ", e)
            return None
    
    def get_max_course_id(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()

                # SQL запрос для получения максимального user_id
                select_max_user_id_query = '''SELECT MAX(course_id) FROM courses'''
                cursor.execute(select_max_user_id_query)
                result = cursor.fetchone()[0]

                if result:
                    return result
                else:
                    return 0
        except sqlite3.Error as e:
            print("Error getting max client id: ", e)
            return 0

    def add_user(self, user_name, full_name, password, email, phone_number, address, user_status):
        try:
            # Проверяем, существует ли уже пользователь с указанным user_name
            existing_user = self.get_user_by_name(user_name)
            if existing_user:
                return "This user_name already exists"
            
            if user_status == "lecturer":
                pass
            else:
                user_status = "student"

            # Если пользователь с таким user_name не существует, добавляем нового пользователя
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                user_id = self.get_max_user_id() + 1
                insert_user_query = '''INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
                cursor.execute(insert_user_query, (user_id, user_name, full_name, user_status, password, email, phone_number, address))
                connection.commit()
                return "Success"

        except sqlite3.Error as e:
            print("Error adding user: ", e)
            return "Error adding user"
    
    def add_course(self, course_name, lecturer_id):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                
                # Проверяем, существует ли уже курс с указанным названием
                select_course_query = '''SELECT course_id FROM courses WHERE course_name = ?'''
                cursor.execute(select_course_query, (course_name,))
                existing_course = cursor.fetchone()
                
                if existing_course:
                    # Если курс уже существует, возвращаем "Success" и его ID
                    return True, existing_course[0]
                
                # Если курс не существует, добавляем новый
                course_id = self.get_max_course_id() + 1
                insert_course_query = '''INSERT INTO courses (course_id, course_name, lecturer_id) VALUES (?, ?, ?)'''
                cursor.execute(insert_course_query, (course_id, course_name, lecturer_id))

                connection.commit()
                return True, course_id
        except sqlite3.Error as e:
            print("Error adding course: ", e)
            return "Error adding course", 0

    def add_grade(self, course_id, student_name, lecturer_id, grade, grade_date = datestr("date")):
        try:
            student_id = self.get_user_id_by_full_name(student_name)
            if student_id != None:
                pass
            else:
                return "This student doesn't exist"
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                #SQL запрос на добавление оценки за курс (course_id, student_id, grade_date, lecturer_id, grade)
                insert_course_query = '''INSERT INTO grades VALUES (?, ?, ?, ?, ?)'''
                cursor.execute(insert_course_query, (course_id, student_id, grade_date, lecturer_id, grade))

                connection.commit()
                return "Success"
        except sqlite3.Error as e:
            print("Error adding grade: ", e)
            return "Error adding grade"
    
    def authenticate_user(self, user_name, password):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()

                # Проверяем наличие user_name в таблице
                check_user_query = '''SELECT COUNT(*) FROM users WHERE user_name = ?'''
                cursor.execute(check_user_query, (user_name,))
                user_exists = cursor.fetchone()[0]

                if user_exists:
                    # Пользователь существует, проверяем пароль
                    select_user_query = '''SELECT user_id, user_status, password FROM users WHERE user_name = ?'''
                    cursor.execute(select_user_query, (user_name,))
                    result = cursor.fetchone()

                    user_id, user_status, db_password = result
                    if password == db_password:
                        return user_id, user_status
                    else:
                        return "wrong password"
                else:
                    return "wrong user_name"

        except sqlite3.Error as e:
            print("Error authenticating user: ", e)
            return None

    def get_grades_by_student_id(self, student_id):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_grades_query = '''SELECT g.course_id, c.course_name, u.full_name AS lecturer_name, g.grade_date, g.grade 
                                        FROM grades g
                                        INNER JOIN courses c ON g.course_id = c.course_id
                                        INNER JOIN users u ON g.lecturer_id = u.user_id
                                        WHERE g.student_id = ?'''
                cursor.execute(select_grades_query, (student_id,))
                grades = cursor.fetchall()
                return grades
        except sqlite3.Error as e:
            print("Error getting grades by student id: ", e)
            return None
    
    def create_admin_users(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                # Проверяем, существуют ли уже записи администраторов в таблице users
                select_admin_users_query = '''SELECT COUNT(*) FROM users WHERE user_status = 'admin' LIMIT 3'''
                cursor.execute(select_admin_users_query)
                admin_count = cursor.fetchone()[0]
                if admin_count >= 1:
                    print("Admin users already exist")
                    return
                
                user_id = 1
                user_name = "admin"
                full_name = "Admin"
                password = "qwerty"
                user_status = "admin"
                insert_user_query = '''INSERT INTO users (user_id, user_name, full_name, user_status, password) VALUES (?, ?, ?, ?, ?)'''
                cursor.execute(insert_user_query, (user_id, user_name, full_name, user_status, password))
                connection.commit()
                print("Admin users created successfully")
        except sqlite3.Error as e:
            print("Error creating admin users: ", e)
    
    def get_all_grades(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_all_grades_query = '''SELECT g.course_id, c.course_name, s.full_name AS student_name, u.full_name AS lecturer_name, g.grade_date, g.grade 
                                            FROM grades g
                                            INNER JOIN courses c ON g.course_id = c.course_id
                                            INNER JOIN users s ON g.student_id = s.user_id
                                            INNER JOIN users u ON g.lecturer_id = u.user_id'''
                cursor.execute(select_all_grades_query)
                all_grades = cursor.fetchall()
                return all_grades
        except sqlite3.Error as e:
            print("Error getting all grades: ", e)
            return None
        
    def get_student_users(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_student_users_query = '''SELECT full_name, user_name, email, phone_number FROM users WHERE user_status = ?'''
                cursor.execute(select_student_users_query, ("student",))
                student_users = cursor.fetchall()
                return student_users
        except sqlite3.Error as e:
            print("Error getting student users: ", e)
            return None
    
    def get_user_info_by_id(self, user_id):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_user_info_query = '''SELECT user_id, user_name, full_name, email, phone_number FROM users WHERE user_id = ?'''
                cursor.execute(select_user_info_query, (user_id,))
                user_info = cursor.fetchone()
                return user_info
        except sqlite3.Error as e:
            print("Error getting user info by id: ", e)
            return None
    
    def get_average_grades_by_course(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                # SQL-запрос для получения среднего значения оценки для каждого курса
                select_average_grades_query = '''SELECT g.course_id, c.course_name, AVG(g.grade) AS average_grade
                                                FROM grades g
                                                INNER JOIN courses c ON g.course_id = c.course_id
                                                GROUP BY g.course_id'''
                cursor.execute(select_average_grades_query)
                average_grades = cursor.fetchall()
                return average_grades
        except sqlite3.Error as e:
            print("Error getting average grades by course: ", e)
            return None
    
    def get_student_counts_by_course(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                # SQL-запрос для получения количества студентов для каждого курса
                select_student_counts_query = '''SELECT c.course_id, c.course_name, COUNT(u.user_id) AS student_count
                                                FROM courses c
                                                LEFT JOIN grades g ON c.course_id = g.course_id
                                                LEFT JOIN users u ON g.student_id = u.user_id
                                                WHERE u.user_status = 'student'
                                                GROUP BY c.course_id'''
                cursor.execute(select_student_counts_query)
                student_counts = cursor.fetchall()
                return student_counts
        except sqlite3.Error as e:
            print("Error getting student counts by course: ", e)
            return None

    def get_total_student_count(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                # SQL-запрос для получения общего количества студентов
                select_total_student_count_query = '''SELECT COUNT(*) FROM users WHERE user_status = 'student' '''
                cursor.execute(select_total_student_count_query)
                total_student_count = cursor.fetchone()[0]
                return total_student_count
        except sqlite3.Error as e:
            print("Error getting total student count: ", e)
            return None
    
    def add_log(self, action, success, date = datestr("date")):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                # SQL запрос на добавление записи в таблицу logs
                insert_log_query = '''INSERT INTO logs (date, action, success) VALUES (?, ?, ?)'''
                cursor.execute(insert_log_query, (date, action, success))
                connection.commit()
        except sqlite3.Error as e:
            print("Error adding log: ", e)
    
    def get_logs(self):
        try:
            with sqlite3.connect(self.database_file) as connection:
                cursor = connection.cursor()
                select_logs_query = '''SELECT date, action, success FROM logs'''
                cursor.execute(select_logs_query)
                logs = cursor.fetchall()
                return logs
        except sqlite3.Error as e:
            print("Error getting logs: ", e)
            return None




databasemanager = DatabaseManager("grade_tracker.db")
databasemanager.initialize_database()
databasemanager.create_admin_users()

app = Flask(__name__)


@app.route('/')
def start():
    databasemanager.add_log("start_page_active", True)
    return render_template("grade_tracker.html")

@app.route('/add_user', methods = ['POST'])
def add_user():
    req = request.json
    user_name = req['user_name']
    full_name = req['full_name']
    password = req['password']
    email = req['email']
    phone_number = req['phone_number']
    address = req['address']
    user_status = req['user_status']
    result = databasemanager.add_user(user_name, full_name, password, email, phone_number, address, user_status)
    if result == "Success":
        print("Adding user successful")
        databasemanager.add_log(f"adding {user_name} user", True)
        responce = {
            "success": True,
            "message": "Adding user successful"
        }
    else:
        databasemanager.add_log(f"adding {user_name} user", False)
        print(result)
        responce = {
            "success": False,
            "message": result
        }
    return jsonify(responce)

@app.route('/add_course', methods = ['POST'])
def add_course():
    req = request.json
    course_name = req['course_name']
    lecturer_id = req['lecturer_id']
    result = databasemanager.add_course(course_name, lecturer_id)
    success, course_id = result
    if success == True:
        databasemanager.add_log(f"adding {course_name} course", True)
        responce = {
            "success": True,
            "message": "Course added successful",
            "course_id": course_id
        }
    else:
        databasemanager.add_log(f"adding {course_name} course", False)
        responce = {
            "success": False,
            "message": "Error adding course",
            "course_id": course_id
        }
    return jsonify(responce)

@app.route('/add_grade', methods = ['POST'])
def add_grade():
    req = request.json
    course_id = req['course_id']
    student_name = req['student_name']
    lecturer_id = req['lecturer_id']
    grade = req['grade']
    result = databasemanager.add_grade(course_id, student_name, lecturer_id, grade)
    if result == "Success":
        databasemanager.add_log(f"adding course_id {course_id} grade", True)
        print("Adding grade successful")
        responce = {
            "success": True,
            "message": "Adding user successful"
        }
    else:
        databasemanager.add_log(f"adding course_id {course_id} grade", False)
        print(result)
        responce = {
            "success": False,
            "message": result
        }
    return jsonify(responce)

@app.route('/authenticate', methods=['POST'])
def authenticate_user():
    req = request.json
    user_name = req['user_name']
    password = req['password']
    result = databasemanager.authenticate_user(user_name, password)
    
    if isinstance(result, tuple):  # Если результат - кортеж (успешная аутентификация)
        databasemanager.add_log(f"authenticate {user_name} user", True)
        user_id, user_status = result
        response = {
            "success": True,
            "message": "Authentication successful",
            "user_id": user_id,
            "user_status": user_status
        }
    else:
        databasemanager.add_log(f"authenticate {user_name} user", False)
        response = {
            "success": False,
            "message": result  # Сообщение об ошибке
        }

    return jsonify(response)

@app.route('/get_student_grades')
def get_student_grades():
    user_id = request.args.get('user_id')
    result = databasemanager.get_grades_by_student_id(user_id)
    databasemanager.add_log(f"get_student_grades", True)
    print ([str(i) for i in result])
    return jsonify([str(i) for i in result])

@app.route('/get_grades')
def get_grades():
    result = databasemanager.get_all_grades()
    databasemanager.add_log(f"get_all_grades", True)
    return jsonify([str(i) for i in result])

@app.route('/get_students')
def get_students():
    result = databasemanager.get_student_users()
    databasemanager.add_log(f"get_students", True)
    return jsonify([str(i) for i in result])

@app.route('/get_avg_grades')
def get_avg_grades():
    result = databasemanager.get_average_grades_by_course()
    databasemanager.add_log(f"get_avg_grades", True)
    print ([str(i) for i in result])
    return jsonify([str(i) for i in result])

@app.route('/get_student_info')
def get_student_info():
    user_id = request.args.get('user_id')
    result = databasemanager.get_user_info_by_id(user_id)
    databasemanager.add_log(f"get_student_info {result[1]}", True)
    print (result)
    user_info = {
            "user_id": result[0],
            "user_name": result[1],
            "full_name": result[2],
            "email": result[3],
            "phone_number": result[4]
        }
    return jsonify(user_info)

@app.route('/get_student_counts_by_course')
def get_student_counts_by_course():
    result = databasemanager.get_student_counts_by_course()
    databasemanager.add_log(f"get_student_counts_by_course", True)
    return jsonify([str(i) for i in result])

@app.route('/get_total_student_count')
def get_total_student_count():
    result = databasemanager.get_total_student_count()
    databasemanager.add_log(f"get_total_studetn_count", True)
    return jsonify({"total_student_count": result})

@app.route('/get_logs')
def get_logs():
    result = databasemanager.get_logs()
    return jsonify([str(i) for i in result])

