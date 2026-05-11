from flask import Flask,render_template,redirect,url_for,request
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
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
    id INTEGER PRIMARY KEY      AUTOINCREMENT, 
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
    admission TEXT)
    ''')   

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logininfo( 
         id INTEGER PRIMARY KEY      AUTOINCREMENT, 
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

        hashed_password = generate_password_hash(password) 

        conn=sqlite3.connect('student.db')
        cursor=conn.cursor() 

        cursor.execute(''' 
        INSERT INTO logininfo
        (username,password,rollno,email) 
        VALUES (?,?,?,?)
      ''',(
        username,
        hashed_password,
        rollno,
        email
      ))  
        
        conn.commit()
        conn.close() 

        return redirect(url_for('login'))

    return  render_template('signup.html') 


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        conn=sqlite3.connect('student.db')
        cursor=conn.cursor() 

        cursor.execute('''
            SELECT username ,password from logininfo 
                       where username=?       
           ''',(username,))   
        
        db_user=cursor.fetchone()
        conn.close() 

        if db_user and check_password_hash(db_user[1],password):
            user_obj=User(username)
            login_user(user_obj) 
            return redirect(url_for('dashboard'))
        else:
            return "login failed" 
        
    return render_template('login.html') 


@app.route('/dashboard')
@login_required
def dashboard():

    return render_template(
        'dashboard.html',
        username=current_user.id
    ) 

@app.route('/addstudent', methods=['GET','POST'])
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

        cursor.execute(''' 
        INSERT INTO studentinfo (fullname,rollno,phno,dob,age,email,admission,year,department,cou,addr,gender)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
       ''',(fullname,rollno,phno,dob,age,email,admission,year,department,cou,addr,gender,)) 
        
        conn.commit()
        conn.close() 

        return "form saved successfully" 
    
    return render_template('addstudent.html') 

@app.route('/students')
@login_required
def students():
    conn=sqlite3.connect('student.db')
    cursor=conn.cursor() 

    cursor.execute('''
      SELECT  * FROM studentinfo
    ''') 

    student_data=cursor.fetchall() 

    conn.close()

    return render_template('students.html', students=student_data)


@app.route('/logout')
@login_required
def logout():

    logout_user()
 
    return redirect(url_for('login')) 

if __name__ == "__main__":

    ini_db()

    app.run(debug=True) 


