from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='kusumachandashwini'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/resultdbms'
db=SQLAlchemy(app)

# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))



class Attendence(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    attendance=db.Column(db.Integer())

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))





class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(50),unique=True)
    sname=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    physics=db.Column(db.Float)
    chemistry=db.Column(db.Float)
    maths=db.Column(db.Float)
    english=db.Column(db.Float)
    computer=db.Column(db.Float)
    total=db.Column(db.Float)
    percent=db.Column(db.Float)
    
    

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/studentdetails')
def studentdetails():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    query=Student.query.all() 
    return render_template('studentdetails.html',query=query)

@app.route('/triggers')
def triggers():
    # query=db.engine.execute(f"SELECT * FROM `trig`") 
    query=Trig.query.all()
    return render_template('triggers.html',query=query)



@app.route('/addattendance',methods=['POST','GET'])
@login_required
def addattendance():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    query=Student.query.all()
    if request.method=="POST":
        rollno=request.form.get('rollno')
        attend=request.form.get('attend')
        print(attend,rollno)
        atte=Attendence(rollno=rollno,attendance=attend)
        db.session.add(atte)
        db.session.commit()
        flash("Attendance added","warning")

        
    return render_template('attendance.html',query=query)

@app.route('/search',methods=['POST','GET'])
def search():
    if request.method=="POST":
        rollno=request.form.get('roll')
        bio=Student.query.filter_by(rollno=rollno).first()
        attend=Attendence.query.filter_by(rollno=rollno).first()
        return render_template('search.html',bio=bio,attend=attend)
        
    return render_template('search.html')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    post=Student.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    # db.engine.execute(f"DELETE FROM `student` WHERE `student`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/studentdetails')


    
@app.route("/edit/<string:id>", methods=['POST', 'GET'])
@login_required
def edit(id):
    if request.method == "POST":
        rollno = request.form.get('rollno')
        sname = request.form.get('sname')
        gender = request.form.get('gender')
         # Convert subject marks to float, defaulting to 0 if not provided
        physics = min(float(request.form.get('physics', 0)), 100)  # Limit to 100
        chemistry = min(float(request.form.get('chemistry', 0)), 100)  # Limit to 100
        maths = min(float(request.form.get('maths', 0)), 100)  # Limit to 100
        english = min(float(request.form.get('english', 0)), 100)  # Limit to 100
        computer = min(float(request.form.get('computer', 0)), 100)  # Limit to 100
        
        # Calculate total
        total = physics + chemistry + maths + english + computer
        percent = (total / 500) * 100  # Assuming total marks for all subjects is 500
        
        try:
            post = Student.query.filter_by(id=id).first()
            post.rollno = rollno
            post.sname = sname
            post.gender = gender
            post.physics = physics
            post.chemistry = chemistry
            post.maths = maths
            post.english = english
            post.computer = computer
            post.total = total
            post.percent = percent
            db.session.commit()
            flash("Student information updated successfully", "success")
            return redirect('/studentdetails')
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating student information", "danger")
    
    posts = Student.query.filter_by(id=id).first()
    return render_template('edit.html', posts=posts)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        # new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        newuser=User(username=username,email=email,password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Success Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return render_template('login.html')




    
@app.route('/addstudent', methods=['POST', 'GET'])
@login_required
def addstudent():
    if request.method == "POST":
        rollno = request.form.get('rollno')
        if rollno is not None and rollno.strip():
            sname = request.form.get('sname')
            gender = request.form.get('gender')
            
            # Convert subject marks to float, defaulting to 0 if not provided
            physics = min(float(request.form.get('physics', 0)), 100)  # Limit to 100
            chemistry = min(float(request.form.get('chemistry', 0)), 100)  # Limit to 100
            maths = min(float(request.form.get('maths', 0)), 100)  # Limit to 100
            english = min(float(request.form.get('english', 0)), 100)  # Limit to 100
            computer = min(float(request.form.get('computer', 0)), 100)  # Limit to 100
            
            # Calculate total
            total = physics + chemistry + maths + english + computer
            percent = (total / 500) * 100  # Assuming total marks for all subjects is 500

            try:
                query = Student(rollno=rollno, sname=sname, gender=gender, physics=physics, chemistry=chemistry,
                                maths=maths, english=english, computer=computer, total=total, percent=percent)
                db.session.add(query)
                db.session.commit()
                flash("Student added successfully", "success")
                

            except Exception as e:
                db.session.rollback()
                flash("Invalid credentials. Rollno already exists.", "danger")
        else:
            flash("Invalid credentials. Rollno cannot be empty.", "danger")

    return render_template('student.html')


@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)    