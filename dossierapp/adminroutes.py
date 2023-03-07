from collections import UserList
import re, os
from crypt import methods
from flask import render_template, redirect, flash, session, request,url_for
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from dossierapp import app,db
from dossierapp.models import Office, Department, Managementreport, Staffreport, Admin






@app.route('/adminregister/', methods=['POST','GET'])
def adminreg():
    if request.method == 'GET':
        return render_template('adminregister.html')
    else:
        name = request.form.get('fullname')
        mail = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd2 = request.form.get('confirm_pwd')
        phone = request.form.get('phone')
        addr = request.form.get('address')
        
        if name != "" and mail != "" and pwd != "" and phone != "" and addr != "":
            pwd_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)([a-zA-Z\d]{8,})$"
            phone_pattern = "0[7-9][0-1]([0-9]){8}"
            pwd_check = re.match(pwd_pattern,pwd)
            phone_check = re.match(phone_pattern,phone)
            if pwd_check:
                if phone_check:
                    if pwd == pwd2:
                        pwdhash = generate_password_hash(pwd)
                        fetch = db.session.query(Admin).filter(Admin.admin_mail == mail).first()
                        if fetch == None:
                            flash('username already exist!')
                            return redirect('/adminregister')
                        else:
                            addup = Admin(admin_fullname = name, admin_mail = mail, admin_pwd = pwdhash, admin_phone = phone, admin_address = addr)
                            db.session.add(addup)
                            db.session.commit()
                            flash('Account created successfully, login with your Username and password to continue', category='success')
                            return redirect(url_for('/adminregister'))
                    else:
                        flash('Password must match')
                        return redirect(url_for('adminreg'))
                else:
                    flash('Invalid phone number', category='error')
                    return redirect(url_for('adminreg'))
            else:
                flash('Please check the password requirements', category='error')
                return redirect(url_for('adminreg'))
        else:
            flash('Please complete the fields')
            return redirect(url_for('adminreg'))




@app.route('/admin/', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'GET':
        return render_template('adminlogin.html')
    else:
        mail = request.form.get('email')
        pwd = request.form.get('pwd')

        admin = db.session.query(Admin).filter(Admin.admin_mail == mail).first()

        if admin is not None:
            check = check_password_hash(admin.admin_pwd, pwd)
            if check:
                session['admin'] = admin.admin_id
                flash('Login successful', category='success')
                return redirect(url_for('admindashboard'))
            else:
                flash('Username or password is incorrect.', category='error')
                return render_template('adminlogin.html')
        else:
            flash('Username does not match our records.', category='error')
            return render_template('adminlogin.html')



@app.route('/adminforgotpassword')
def adminforgotpassword():
    if request.method == 'GET':
        link = 'http://127.0.0.1:8080/adminpasswordreset'
        with open('adminmail.txt','r+') as message:
            message.write(link)
            return 'a password reset link has been sent to your mail'


@app.route('/adminpasswordreset/', methods = ["POST", 'GET'])
def adminreset():
    if request.method == 'GET':
        return render_template('adminforgot.html')
    else:
        mail = request.form.get('email')
        newpwd = request.form.get('pwd')
        newpwd2 = request.form.get('confirm-pwd')

        if mail != "" and newpwd != "" and newpwd2 != "":
            registeredadmin = Admin.query.filter(Admin.admin_mail == mail).first()
            if registeredadmin != None:
                if newpwd == newpwd2:
                    pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)([a-zA-Z\d]{8,})$"

                    p = re.match(pattern,newpwd)
                    if p:
                        pwdhash = generate_password_hash(newpwd)
                        registeredadmin.admin_pwd = pwdhash
                        db.session.commit()
                        flash('password changed successfully, you can log in with your new password!')
                        return redirect(url_for('adminlogin'))
                    else:
                        flash('please check password requirements')
                        return redirect(url_for('adminreset'))
                else:
                    flash('password must match')
                    return redirect(url_for('adminreset'))
            else:
                flash('Admin doesn\'t exist')
                return redirect(url_for('adminreset'))

        else:
            flash('all field required')
            return redirect(url_for('adminreset'))




@app.route('/admindashboard/')
def admindashboard():
        if session.get('admin') is not None:
                adminquery = Admin.query.get(session['admin'])
                alladminquery = Admin.query.all()
                staffreports = db.session.query(Staffreport).all()
                mgtreports = Managementreport.query.all()
                return render_template('admindashboard.html', staffreports = staffreports, adminquery = adminquery, mgtreports = mgtreports, alladminquery = alladminquery)
        else:
            return redirect('/admin')
        




@app.route('/management/report/approve/<id>', methods = ['POST'])
def mgt_approve(id):
    if session.get('admin') != None:
        if request.method == 'POST':
            reportid = request.form.get('reportid')
            stat = request.form.get('stat')
            fetch = Managementreport.query.get(reportid)
            fetch.report_status = stat
            db.session.commit()
            return redirect('/admindashboard')

    return redirect('/adminlogin')



@app.route('/staff/report/approve/<id>', methods = ['POST'])
def staff_approve(id):
    if session.get('admin') != None:
        if request.method == 'POST':
            reportid = request.form.get('reportid')
            stat = request.form.get('stat')
            fetch = Staffreport.query.get(reportid)
            fetch.report_status = stat
            db.session.commit()
            return redirect('/admindashboard')

    return redirect('/adminlogin')






@app.route('/adminlogout')
def adminlogout():
    if session.get('admin') != None:
        session.pop('admin', None)
        return redirect('/admin')



