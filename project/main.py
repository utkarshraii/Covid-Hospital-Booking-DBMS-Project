from flask.globals import request, session
from flask import session
from flask.helpers import url_for
from flask import Flask, json, redirect, render_template, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required,logout_user,login_user,LoginManager,login_manager,current_user
from flask_mail import Mail
import json

# my database connection
local_server = True
app = Flask(__name__)  # activate flask
app.secret_key = "Utkarsh"

with open('backend\config.json', 'r') as c:
    params = json.load(c)["params"]

app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["gmail-user"],
    MAIL_PASSWORD=params["gmail-password"],
)
mail = Mail(app)


# this is for getting the unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/covid"
db = SQLAlchemy(app)  # connect sqlalchemy with app.config


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))


# need to tell that i have created a database table of user
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(100), unique=True)
    dob = db.Column(db.String(1000))


class Hospitaluser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20))
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(200), unique=True)
    hname = db.Column(db.String(200))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    vbed = db.Column(db.Integer)

class Trig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hcode = db.Column(db.String(20))
    normalbed = db.Column(db.Integer)
    hicubed = db.Column(db.Integer)
    icubed = db.Column(db.Integer)
    vbed = db.Column(db.Integer)
    query=db.Column(db.String(50))
    date=db.Column(db.String(50))

class Bookingpatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    srfid = db.Column(db.String(20), unique=True)
    bedtype = db.Column(db.String(100))
    hcode = db.Column(db.String(20))
    spo2 = db.Column(db.Integer)
    pname = db.Column(db.String(100))
    pphone = db.Column(db.String(100))
    paddress = db.Column(db.String(100))


@app.route("/")  # return html file
def home():
    return render_template(
        "index.html"
    )  # render file name is index.html and ../ means it will go and check one directory back i.e. it will check frontend in dbms project

@app.route("/trigers")  # return html file
def trigers():
    query=Trig.query.all()
    return render_template("trigers.html",query=query)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('SRF')
        email = request.form.get('email')
        dob = request.form.get('dob')
        # print(SRFID,email,dob)
        encpassword = generate_password_hash(dob)
        user = User.query.filter_by(srfid=srfid).first()
        emailUser = User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srif is already taken", "warning")
            return render_template("usersignup.html")
        new_user = db.engine.execute(
            f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}') "
        )
        user1 = User.query.filter_by(srfid=srfid).first()
        if user1 and check_password_hash(user1.dob, dob):
            login_user(user)
            flash("SignIn Success", "success")
            return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        srfid = request.form.get("SRF")
        dob = request.form.get("dob")
        user = User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob, dob):
            login_user(user)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("userlogin.html")
    return render_template("userlogin.html")


@app.route("/hospitallogin", methods=["POST", "GET"])
def hospitallogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login Success", "info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials", "danger")
            return render_template("hospitallogin.html")
    return render_template("hospitallogin.html")


@app.route("/admin", methods=["POST", "GET"])
def admin():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == params["user"] and password == params["password"]:
            session["user"] = username
            flash("Login Success", "info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials", "danger")
    return render_template("admin.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for("login"))


@app.route("/addHospitalUser", methods=["POST", "GET"])
def hospitalUser():
    query=db.engine.execute(f"SELECT * FROM `trig` ")
            
    if "user" in session and session["user"] == params["user"]:
        if request.method == "POST":
            hcode = request.form.get("hcode")
            email = request.form.get("email")
            password = request.form.get("password")
            encpassword = generate_password_hash(password)
            hcode = hcode.upper()
            emailUser = Hospitaluser.query.filter_by(email=email).first()
            if emailUser:
                flash("Email is already taken", "warning")
            db.engine.execute(
                f"INSERT INTO `hospitaluser` (`hcode`,`email`,`password`) VALUES ('{hcode}','{email}','{encpassword}') "
            )
            # mail.send_message('COVID CARE CENTRE',sender=params['gmail-user'],recipients=[email],body=f"Welcome thanks for choosing us \nYour login credentials are:\nEmail Address: {email} \nPassword: {password}\n\n\n\n Do not share your password\n\n\nThank you")

            flash("dATA sent and inserted successfully", "info")
            return render_template("addHosUser.html",query=query)

    else:
        flash("login and try again", "warning")
        return render_template("addHosUser.html")


@app.route("/logoutadmin")
def logoutadmin():
    session.pop("user")
    flash("You are logged out", "primary")
    return redirect("/admin")


# testing whether db is connected or not
@app.route("/test")  # return html file
def test():
    try:
        a = Test.query.all()
        print(a)
        return f"MY DATABASE IS CONNECTED "
    except Exception as e:
        print(e)
        return f"MY DATABASE IS NOT CONNECTED {e}"


@app.route("/addhospitalinfo", methods=["POST", "GET"])
def addhospitalinfo():
        email =current_user.email
        posts = Hospitaluser.query.filter_by(email=email).first()
        code = posts.hcode
        postsdata = Hospitaldata.query.filter_by(hcode=code).first()

        if request.method == "POST":
            hcode = request.form.get("hcode")
            hname = request.form.get("hname")
            nbed = request.form.get("normalbed")
            hbed = request.form.get("hicubed")
            ibed = request.form.get("icubed")
            vbed = request.form.get("vbed")
            hcode = hcode.upper()
            huser = Hospitaluser.query.filter_by(hcode=hcode).first()
            hduser = Hospitaldata.query.filter_by(hcode=hcode).first()
            if hduser:
                flash("Data is already added you can update it", "primary")
                return render_template("hospitaldata.html")
            if huser:
                db.engine.execute(
                    f"INSERT INTO `hospitaldata` (`hcode`,`hname`,`normalbed`,`hicubed`,`icubed`,`vbed`) values('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')"
                )
                flash("Data added", "primary")
            else:
                flash("Hospital Code does not exist", "warning")
        return render_template("hospitaldata.html",postsdata=postsdata)
    

@app.route("/hedit/<string:id>", methods=["POST", "GET"])
@login_required
def hedit(id):
    posts = Hospitaldata.query.filter_by(id=id).first()
    if request.method == "POST":
        hcode = request.form.get("hcode")
        hname = request.form.get("hname")
        nbed = request.form.get("normalbed")
        hbed = request.form.get("hicubed")
        ibed = request.form.get("icubed")
        vbed = request.form.get("vbed")
        hcode = hcode.upper()
        db.engine.execute(
            f"UPDATE `hospitaldata` SET `hcode` = '{hcode}',`hname` = '{hname}',`normalbed` = '{nbed}',`hicubed` = '{hbed}',`icubed` = '{ibed}',`vbed` = '{vbed}' WHERE `hospitaldata`.`id`={id}"
        )
        flash("Slot Updated", "info")
        return redirect("/addhospitalinfo")

    return render_template("hedit.html", posts=posts)

@app.route("/hdelete/<string:id>", methods=["POST", "GET"])
@login_required
def hdelete(id):
    db.engine.execute(f"DELETE FROM `hospitaldata` WHERE  `hospitaldata`.`id`={id}")
    flash("Data Deleted", "danger")
    return redirect("/addhospitalinfo")

@app.route("/pdetails", methods=[ "GET"])
@login_required
def pdetails():
    code=current_user.srfid
    data=Bookingpatient.query.filter_by(srfid=code).first()        
    return render_template("/details.html",data=data)

@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    query=db.engine.execute(f"SELECT * FROM `hospitaldata` ")
    if request.method=="POST":
        srfid=request.form.get('srfid')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress')  
        check2=Hospitaldata.query.filter_by(hcode=hcode).first()
        if not check2:
            flash("Hospital Code not exist","warning")

        code=hcode
        dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")        
        bedtype=bedtype
        if bedtype=="NormalBed":       
            for d in dbb:
                seat=d.normalbed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.normalbed=seat-1
                db.session.commit()
                
            
        elif bedtype=="HICUBed":      
            for d in dbb:
                seat=d.hicubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.hicubed=seat-1
                db.session.commit()

        elif bedtype=="ICUBed":     
            for d in dbb:
                seat=d.icubed
                print(seat)
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.icubed=seat-1
                db.session.commit()

        elif bedtype=="VENTILATORBed": 
            for d in dbb:
                seat=d.vbed
                ar=Hospitaldata.query.filter_by(hcode=code).first()
                ar.vbed=seat-1
                db.session.commit()
        else:
            pass

        check=Hospitaldata.query.filter_by(hcode=hcode).first()
        if(seat>0 and check):
            res=Bookingpatient(srfid=srfid,bedtype=bedtype,hcode=hcode,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress)
            db.session.add(res)
            db.session.commit()
            flash("Slot is Booked kindly Visit Hospital for Further Procedure","success")
        else:
            flash("Something Went Wrong","danger")
    
    return render_template("booking.html",query=query)


app.run(debug=True)  # run your application
