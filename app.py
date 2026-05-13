from flask import Flask,render_template,redirect,url_for,request,flash,send_file
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
) 

import csv 
 
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import sqlite3

app=Flask(__name__, template_folder="mytemplets")

app.secret_key="mysecretkey"

login_manager=LoginManager()

login_manager.init_app(app)

login_manager.login_view="login"


class User(UserMixin):

    def __init__(self,id):

        self.id=id


@login_manager.user_loader
def load_user(user_id):

    return User(user_id)


def ini_db():

    conn=sqlite3.connect('student.db')

    cursor=conn.cursor()

    cursor.execute('''

    CREATE TABLE IF NOT EXISTS studentinfo(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        rollno INTEGER UNIQUE,

        fullname TEXT,

        age NUMBER,

        phno TEXT,

        addr TEXT,

        gender TEXT,

        dob TEXT,

        cou TEXT,

        department TEXT,

        year NUMBER,

        email TEXT UNIQUE,

        admission TEXT
    )

    ''')

    cursor.execute('''

    CREATE TABLE IF NOT EXISTS logininfo(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        rollno NUMBER,

        username TEXT,

        password TEXT,

        email TEXT
    )

    ''')

    conn.commit()

    conn.close()


@app.route('/', methods=['GET','POST'])
def signup():

    if request.method=='POST':

        username=request.form.get('username')

        password=request.form.get('password')

        rollno=request.form.get('rollno')

        email=request.form.get('email')

        conn=sqlite3.connect('student.db')

        cursor=conn.cursor()

        # Username Validation

        cursor.execute(
            '''
            SELECT * FROM logininfo
            WHERE username=?
            ''',
            (username,)
        )

        existing_user=cursor.fetchone()

        if existing_user:

            conn.close()

            flash("Username already exists ❌")

            return redirect(url_for('signup'))

        # Email Validation

        cursor.execute(
            '''
            SELECT * FROM logininfo
            WHERE email=?
            ''',
            (email,)
        )

        existing_email=cursor.fetchone()

        if existing_email:

            conn.close()

            flash("Email already registered ❌")

            return redirect(url_for('signup'))

        # Password Validation

        if len(password) < 6:

            conn.close()

            flash("Password must be at least 6 characters ❌")

            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        cursor.execute(
            '''
            INSERT INTO logininfo
            (username,password,rollno,email)

            VALUES (?,?,?,?)
            ''',

            (
                username,
                hashed_password,
                rollno,
                email
            )
        )

        conn.commit()

        conn.close()

        flash("Signup Successful ✅")

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method=='POST':

        username=request.form.get('username')

        password=request.form.get('password')

        # Empty Field Validation

        if username == "" or password == "":

            flash("Please fill all fields ❌")

            return redirect(url_for('login'))

        conn=sqlite3.connect('student.db')

        cursor=conn.cursor()

        cursor.execute(
            '''
            SELECT username,password
            FROM logininfo
            WHERE username=?
            ''',
            (username,)
        )

        db_user=cursor.fetchone()

        conn.close()

        if db_user and check_password_hash(db_user[1],password):

            user_obj=User(username)

            login_user(user_obj)

            return redirect(url_for('dashboard'))

        else:

            flash("Invalid Username or Password ❌")

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():

    conn = sqlite3.connect('student.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT COUNT(*) FROM studentinfo
        '''
    )

    total_students = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(DISTINCT cou)
        FROM studentinfo
        '''
    )

    total_courses = cursor.fetchone()[0]

    cursor.execute(
        '''
        SELECT COUNT(DISTINCT department)
        FROM studentinfo
        '''
    )

    total_departments = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',

        total_students=total_students,

        total_courses=total_courses,

        total_departments=total_departments
    )


@app.route('/addstudent', methods=['GET','POST'])
@login_required
def addstudent():

    if request.method=='POST':

        fullname=request.form.get('fullname')

        rollno=request.form.get('rollno')

        phno=request.form.get('phno')

        dob=request.form.get('dob')

        age=request.form.get('age')

        email=request.form.get('email')

        admission=request.form.get('admission')

        year=request.form.get('year')

        department=request.form.get('department')

        cou=request.form.get('cou')

        addr=request.form.get('addr')

        gender=request.form.get('gender')

        conn=sqlite3.connect('student.db')

        cursor=conn.cursor()

        # Roll Number Validation

        cursor.execute(
            '''
            SELECT * FROM studentinfo
            WHERE rollno=?
            ''',
            (rollno,)
        )

        existing_rollno=cursor.fetchone()

        if existing_rollno:

            conn.close()

            flash("Roll Number already exists ❌")

            return redirect(url_for('addstudent'))

        # Email Validation

        cursor.execute(
            '''
            SELECT * FROM studentinfo
            WHERE email=?
            ''',
            (email,)
        )

        existing_email=cursor.fetchone()

        if existing_email:

            conn.close()

            flash("Email already exists ❌")

            return redirect(url_for('addstudent'))

        # Phone Validation

        if len(phno) != 10:

            conn.close()

            flash("Phone Number must be 10 digits ❌")

            return redirect(url_for('addstudent'))

        # Age Validation

        if int(age) <= 0:

            conn.close()

            flash("Invalid Age ❌")

            return redirect(url_for('addstudent'))

        cursor.execute(
            '''
            INSERT INTO studentinfo
            (fullname,rollno,phno,dob,age,email,admission,year,department,cou,addr,gender)

            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            ''',

            (
                fullname,
                rollno,
                phno,
                dob,
                age,
                email,
                admission,
                year,
                department,
                cou,
                addr,
                gender
            )
        )

        conn.commit()

        conn.close()

        flash("Student Added Successfully ✅")

        return redirect(url_for('students'))

    return render_template('addstudent.html')


@app.route('/students')
@login_required
def students(): 

    rno = request.args.get('rollno')

    conn = sqlite3.connect('student.db')

    cursor = conn.cursor()

    if rno:

        cursor.execute(
            '''
            SELECT * FROM studentinfo
            WHERE rollno=?
            ''',
            (rno,)
        )

    else:

        cursor.execute(
            '''
            SELECT * FROM studentinfo
            '''
        )

    student_data = cursor.fetchall()

    conn.close()

    return render_template(
        'students.html',
        students=student_data
    ) 

@app.route('/exportcsv')
@login_required
def export_csv():

    conn = sqlite3.connect('student.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT * FROM studentinfo
        '''
    )

    students = cursor.fetchall()

    conn.close()

    with open(
        'students.csv',
        'w',
        newline='',
        encoding='utf-8'
    ) as file:

        writer = csv.writer(file)

        # Column Names

        writer.writerow([
            'ID',
            'Roll No',
            'Full Name',
            'Age',
            'Phone',
            'Address',
            'Gender',
            'DOB',
            'Course',
            'Department',
            'Year',
            'Email',
            'Admission'
        ])

        # Student Data

        writer.writerows(students)

    return send_file(
        'students.csv',
        as_attachment=True
    )


@app.route('/delete/<int:rollno>', methods=['GET','POST'])
@login_required
def delete_student(rollno):

    conn = sqlite3.connect('student.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        DELETE FROM studentinfo
        WHERE rollno=?
        ''',
        (rollno,)
    )

    conn.commit()

    conn.close()

    flash("Student Deleted Successfully ✅")

    return redirect(url_for('students'))


@app.route('/edit/<int:rollno>', methods=['GET', 'POST'])
@login_required
def edit_student(rollno):

    conn = sqlite3.connect('student.db')

    cursor = conn.cursor()

    if request.method == 'POST':

        fullname = request.form.get('fullname')

        age = request.form.get('age')

        phno = request.form.get('phno')

        addr = request.form.get('addr')

        gender = request.form.get('gender')

        dob = request.form.get('dob')

        cou = request.form.get('cou')

        department = request.form.get('department')

        year = request.form.get('year')

        email = request.form.get('email')

        admission = request.form.get('admission')

        # Phone Validation

        if len(phno) != 10:

            flash("Phone Number must be 10 digits ❌")

            return redirect(url_for('edit_student', rollno=rollno))

        # Age Validation

        if int(age) <= 0:

            flash("Invalid Age ❌")

            return redirect(url_for('edit_student', rollno=rollno))

        cursor.execute(
            '''
            UPDATE studentinfo

            SET
                fullname=?,
                age=?,
                phno=?,
                addr=?,
                gender=?,
                dob=?,
                cou=?,
                department=?,
                year=?,
                email=?,
                admission=?

            WHERE rollno=?
            ''',

            (
                fullname,
                age,
                phno,
                addr,
                gender,
                dob,
                cou,
                department,
                year,
                email,
                admission,
                rollno
            )
        )

        conn.commit()

        conn.close()

        flash("Student Updated Successfully ✅")

        return redirect(url_for('students'))

    cursor.execute(
        '''
        SELECT * FROM studentinfo
        WHERE rollno=?
        ''',
        (rollno,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        'editstudent.html',
        student=student
    )


@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


if __name__ == "__main__":

    ini_db()

    app.run(debug=True)