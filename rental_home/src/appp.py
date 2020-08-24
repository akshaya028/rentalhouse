from flask import *
#from flask.app import Flask
#from flask.globals import request
#from flask.templating import render_template 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, not_
from _overlapped import NULL
from flask_mail import *

app = Flask(__name__) 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kce.rentalhouse@gmail.com'
app.config['MAIL_PASSWORD'] = 'rentalhouse@123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 
app.config['SQLALCHEMY_DATABASE_URI']='oracle://system:akshaya@localhost:1521/XE'
db=SQLAlchemy(app)
class home(db.Model):
    __tablename__ = 'login_detail'
    fname=db.Column(db.String(25))
    lname=db.Column(db.String(25))
    mobile_no=db.Column(db.Integer,primary_key=True)
    address=db.Column(db.String(80))
    email=db.Column(db.String(40))
    login=db.Column(db.String(20))
    pwd=db.Column(db.String(20))
    cpwd=db.Column(db.String(20))
    sec_ques=db.Column(db.String(10))
    sec_ans=db.Column(db.String(10))
class house(db.Model):
    __tablename__='house_details'
    id =db.Column(db.Integer,db.Sequence('seq_id',start=101))
    ownername=db.Column(db.String(50))
    contact_no=db.Column(db.Integer,db.ForeignKey('login_detail.mobile_no'),primary_key=True)
    email=db.Column(db.String(50))
    address=db.Column(db.String(100))
    city=db.Column(db.String(50))
    pincode=db.Column(db.Integer)
    description=db.Column(db.String(150))
    rent=db.Column(db.String(10))
    advance=db.Column(db.String(10))
    expectations=db.Column(db.String(50))
    status=db.Column(db.String(10))
class customer(db.Model):
    __tablename__='customer_details'
    req_id=db.Column(db.Integer,db.Sequence('req_id',start=101),primary_key=True)
    h_id=db.Column(db.Integer)
    name=db.Column(db.String(50))
    contact_no=db.Column(db.Integer)
    email=db.Column(db.String(50))
    address=db.Column(db.String(100))
    job=db.Column(db.String(50))
    age=db.Column(db.Integer)
    members=db.Column(db.Integer)
    status=db.Column(db.String(50))
@app.route('/')
@app.route('/loginpage',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method=='POST':
        uname=request.form['mobile']
        password=request.form['password']
        conn=home.query.filter(home.mobile_no==uname).first()
        if conn is not NULL:
            if conn.pwd==password:    
                if conn.login=='Customer':
                    msg='Successfully logged in'
                    resp = make_response(render_template('customerhome.html',cont=conn,msg=msg))  
                    resp.set_cookie('uname',uname)  
                    return resp  
                else:
                    msg='Successfully logged in'
                    resp = make_response(render_template("adminhome.html",cont=conn,msg=msg)) 
                    resp.set_cookie('uname',uname)  
                    return resp  
            else:
                msg="Invalid mobilenumber or password :("
                return render_template("register.html",msg=msg)
        else:
            return render_template("register.html")
@app.route('/signuppage',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('register.html')
    elif request.method=='POST':
        firstname=request.form['fname']
        lastname=request.form['lname']
        mobno=request.form['mobilenumber']
        addr=request.form['address']
        email=request.form['email']
        logtype=request.form['logintype']
        password=request.form['password']
        con_password=request.form['confirmpassword']
        sques=request.form['question']
        sans=request.form['answer']
        if password==con_password:
            conn=home(fname=firstname,lname=lastname,mobile_no=mobno,address=addr,email=email,login=logtype,pwd=password,cpwd=con_password,sec_ques=sques,sec_ans=sans)
            db.session.add(conn)
            #print(conn)
            db.session.commit()
            msg='Successfully signed in!!!'
            return render_template('register.html',msg=msg)
        else:
            msg="Password and confirm password do not match "
            return render_template("register.html",msg=msg)
@app.route('/forgetpass',methods=['GET','POST'])
def forgetpass():
    if request.method=='GET':
        return render_template('forgetpass.html')
    elif request.method=='POST':
        mobno=request.form['mobilenumber']
        password=request.form['password']
        sques=request.form['question']
        sans=request.form['answer']
        if len(str(mobno))==10:
            conn=home.query.filter(home.sec_ans==sans).one()
            if conn.sec_ques==sques:
                conn.mobile_no=mobno
                conn.pwd=password
                conn.cpwd=password
                db.session.add(conn)
                db.session.commit()
                return render_template('register.html')
            else:
                return render_template('forgetpass.html')
        else:
            return render_template('forgetpass.html')
@app.route("/homepage")
def homepage():
    mobno = request.cookies.get('uname')  
    conn=home.query.filter(home.mobile_no==mobno).first()
    if conn.login=='Customer':
        return render_template("customerhome.html",cont=conn)
    else:
        return render_template("adminhome.html",cont=conn)
@app.route('/profile')
def viewprofile():
    #print(firstname)
    mobno = request.cookies.get('uname')  
    conn=home.query.filter(home.mobile_no==mobno).first()
    resp = make_response(render_template("viewprofile.html",cont=conn))  
    return resp  
@app.route('/editprofile',methods=['GET', 'POST'])
def editprofile():
    if request.method=='GET':
        mobno = request.cookies.get('uname') 
        conn=home.query.filter(home.mobile_no==mobno).first()
        return render_template('editprofile.html',cont=conn)
    elif request.method=='POST':
        firstname=request.form['fname']
        lastname=request.form['lname']
        addr=request.form['address']
        email=request.form['email']
        mobno = request.cookies.get('uname') 
        conn=home.query.filter(home.mobile_no==mobno).first()
        conn.fname=firstname
        conn.lname=lastname
        conn.address=addr
        conn.email=email
        db.session.add(conn)
        db.session.commit()
        if conn.login=="Customer":
            return render_template("customerhome.html")
        else:
            return render_template("adminhome.html")
@app.route('/adddetails',methods=['GET','POST'])
def add():
    if request.method=='GET':
        mobno = request.cookies.get('uname') 
        conn=home.query.filter(home.mobile_no==mobno).first()
        return render_template('adddetails.html',cont =conn)
    elif request.method=='POST':
        name=request.form['fname']
        mobno=request.form['mobilenumber']
        email=request.form['email']
        city=request.form['location']
        addr=request.form['address']
        pin=request.form['pincode']
        descrip=request.form['desc']
        rent=request.form['rent']
        advance=request.form['advance']
        expectation=request.form['expectation']
        status='open'
        conn=house(ownername=name,contact_no=mobno,email=email,address=addr,pincode=pin,description=descrip,city=city,rent=rent,advance=advance,expectations=expectation,status=status)
        db.session.add(conn)
        db.session.commit()
        msg='Successfully Added'
        return render_template('adminhome.html',msg=msg)
@app.route('/updatedetails',methods=['GET','POST'])
def update():
    if request.method=='GET':
        mobno = request.cookies.get('uname') 
        conn=house.query.filter(house.contact_no==mobno).first()
        return render_template('updatedetails.html',cont =conn)
    elif request.method=='POST':
        addr=request.form['address']
        pin=request.form['pincode']
        city=request.form['location']
        descrip=request.form['desc']
        rent=request.form['rent']
        advance=request.form['advance']
        expectation=request.form['expectation']
        mobno = request.cookies.get('uname')
        conn=house.query.filter(house.contact_no==mobno).first()
        conn.address=addr
        conn.pincode=pin
        conn.city=city
        conn.description=descrip
        conn.rent=rent
        conn.advance=advance
        conn.expectations=expectation
        db.session.add(conn)
        db.session.commit()
        msg='Successfully Added'
        return render_template('adminhome.html',msg=msg)
@app.route('/searchhouse',methods=['GET','POST'])
def search():
    if request.method=='GET':
        return render_template('searchhouse.html')
    elif request.method=='POST':
        city=request.form['search']
        conn=house.query.filter(house.city==city).all()
        conn=house.query.filter(and_(house.city==city,house.status=="open")).all()
        return render_template('searchhouse.html',cont=conn)
@app.route('/viewdetails/<id>')
def viewdetails(id):
    conn=house.query.filter(house.id==id).one()
    return render_template("viewdetails.html",cont=conn)
@app.route('/sendmail/<id>',methods=['GET','POST'])
def sendmail(id):
        contn=house.query.filter(house.id==id).one()
        mobno = request.cookies.get('uname')
        conn=customer.query.filter(customer.contact_no==mobno).first()
        con=home.query.filter(home.mobile_no==mobno).first()
        addr=request.form['address']
        job=request.form['job']
        age=request.form['age']
        fammem=request.form['fammem']
        '''if conn:
            conn.h_id=id
            conn.address=addr
            conn.job=job
            conn.age=age
            conn.members=fammem
            conn.status='Open'
            db.session.add(conn)
            db.session.commit()
        else:'''
        cont=customer(h_id=id,name=con.fname,contact_no=con.mobile_no,email=con.email,address=addr,job=job,age=age,members=fammem,status='Open')
        db.session.add(cont)
        db.session.commit()
        cont=customer.query.filter(customer.contact_no==mobno).first()
        msg = Message( 'Request from '+cont.name,  sender ='kce.rentalhouse@gmail.com',recipients = [contn.email]) 
        msg.body='Hi,'+contn.ownername+'\nI would like to accomodate your house.\nMy details are given below:\nName: '+cont.name+'\nMobile Number: '+str(cont.contact_no)+'\nEmail Id: '+cont.email+'\nAddress: '+cont.address+'\nAge: '+str(cont.age)+'\nJob: '+cont.job+'\nFamily members: '+str(cont.members)
        mail.send(msg)
        #print(contn.email) 
        return render_template("customerhome.html")
@app.route('/custdetails/<id>',methods=['GET','POST'])
def custdetails(id):
    mobno = request.cookies.get('uname') 
    con=home.query.filter(home.mobile_no==mobno).first()
    return render_template('custdetails.html',o_id=id,cont=con)
@app.route('/ownerrequest')
def ownerrequest():
    mobno = request.cookies.get('uname')
    con=house.query.filter(house.contact_no==mobno).first()
    #print(con.contact_no)
    conn=customer.query.filter(customer.h_id==con.id,customer.status=='Open').first()
    if conn:
        conn=customer.query.filter(customer.h_id==con.id,customer.status=='Open').all()
    return render_template('ownerreq.html',cont=conn)
@app.route("/accept/<req_id>")
def accept(req_id):
    mobno = request.cookies.get('uname')
    conn=customer.query.filter(customer.req_id==req_id).all()
    for i in conn:
        conn.status='Accepted'
    db.session.add(conn)
    db.session.commit()
    con=house.query.filter(house.id==conn.h_id).first()
    con.status='Closed'
    db.session.add(con)
    db.session.commit()
    #cont=house.query.filter(house.id==conn.h_id).first()
    msg = Message( 'Message from '+con.ownername,  sender ='kce.rentalhouse@gmail.com',recipients = [conn.email]) 
    msg.body='Hi,'+conn.name+' Your request has been accepted'
    mail.send(msg)
    return render_template('adminhome.html')
@app.route("/decline/<req_id>")
def decline(req_id):
    #mobno = request.cookies.get('uname')
    conn=customer.query.filter(customer.req_id==req_id).first()
    conn.status='Declined'
    db.session.add(conn)
    db.session.commit()
    cont=house.query.filter(house.id==conn.h_id).first()
    msg = Message( 'Message from '+cont.ownername,  sender ='kce.rentalhouse@gmail.com',recipients = [conn.email]) 
    msg.body='Hi,'+conn.name+' Sorry !! Your request has been declined'
    mail.send(msg)
    return render_template('adminhome.html')
@app.route("/custrequest")
def custreq():
    mobno = request.cookies.get('uname')
    conn=customer.query.filter(customer.contact_no==mobno).first()
    if conn:
        conn=customer.query.filter(customer.contact_no==mobno).all()
    return render_template('custstatus.html',cont=conn)
@app.route('/logout')
def logout():  
    return render_template("register.html")
if __name__=="__main__":
    db.create_all()
    app.run(debug=True,port=8073)