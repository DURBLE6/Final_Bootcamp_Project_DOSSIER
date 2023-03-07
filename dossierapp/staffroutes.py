import re, os, smtplib
from email.mime.text import MIMEText
from crypt import methods
from flask import render_template, redirect, flash, session, request,url_for
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from dossierapp import app,db
from dossierapp.models import Department, Employees, Office, Staffreport, Managementreport
from dossierapp.forms import SignupForm







@app.route('/dossier', methods = ['POST', 'GET'])
@app.route('/', methods = ['POST', 'GET'])
def staffhome():
    if request.method == 'GET':
        offices = Office.query.all()
        return render_template('home.html',offices = offices)
    else:
        deets = request.form.get('pick')
        if deets == 'New staff':
            return redirect('/staffregister')
        else:
            return redirect('/stafflogin')
        



@app.route('/staffregister', methods=['POST', 'GET'])
def staffregister():
    if request.method == 'GET':
        offices = Office.query.all()
        depts = Department.query.all()
        return render_template('staffreg.html', offices = offices, depts = depts)
    else:
        name = request.form.get('fullname')
        mail = request.form.get('email')
        pwd = request.form.get('pwd')
        pwd2 = request.form.get('pwd2')
        phone = request.form.get('phone')
        office = request.form.get('office')
        department = request.form.get('depts')
        
        if name != "" and mail != "" and pwd != "" and phone != "" and office != None and department != None:
            mail_pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z]+\.[a-zA-Z]{2,}$"
            check_mail = re.match(mail_pattern,mail)
            if check_mail:
                fetch = db.session.query(Employees).filter(Employees.employee_email == mail).first()
                if fetch:
                    flash('Username already exist!')
                    return redirect(url_for('staffregister'))
                else:
                    pwd_pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)([a-zA-Z\d]{8,})$"
                    phone_pattern = "0[7-9][0-1]([0-9]){8}"
                    pwd_check = re.match(pwd_pattern,pwd)
                    phone_check = re.match(phone_pattern,phone)
    
                    if pwd_check:
                        if phone_check:
                            if  pwd == pwd2:
                                pwdhash = generate_password_hash(pwd)
                                add = Employees(employee_email = mail, employee_password = pwdhash, employee_phone = phone, employee_fullname = name, office_id = office, dept_id = department)
                                db.session.add(add)
                                db.session.commit()
                                flash('Account created successfully, you can now login with your username and password', category='success')
                                return redirect(url_for('staffregister'))
                            else:
                                flash('password must match')
                                return redirect(url_for('staffregister'))
                        else:
                            flash('Invalid phone number!', category='error')
                            return redirect(url_for('staffregister'))
                    else:
                        flash('Please check password requirements')
                        return redirect(url_for('staffregister'))                           
            else:
                flash("Invalid mail address", category='error')
                return redirect(url_for('staffregister'))
        else:
            flash('please complete all the fields')
            return redirect(url_for('staffregister'))




@app.route('/stafflogin/', methods = ["POST", 'GET'])
def stafflogin():
    if request.method == 'GET':
        return render_template('stafflogin.html')
    else:
        mail= request.form.get('email') 
        pwd = request.form.get('pwd')

        fetch = db.session.query(Employees).filter(Employees.employee_email == mail).first()

        if fetch != None:
            check = check_password_hash(fetch.employee_password,pwd)
            if check:
                session['staff'] = fetch.employee_id
                session['office'] = fetch.office_id
                return redirect(url_for('staffdashboard'))
            else:
                flash('Username or Password Incorrect', category='error')
                return redirect(url_for('stafflogin'))
        else:
            flash('Details doesn\'t match any of our records', category='error')
            return redirect(url_for('stafflogin'))






@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    EMAIL_PROVIDERS = {
    'gmail': ('smtp.gmail.com', 465),
    'yahoo': ('smtp.mail.yahoo.com', 587),
    'hotmail': ('smtp.live.com', 587),
    }

    if request.method == 'POST':
        email = request.form.get('email')
        
        # Get the SMTP settings based on the email provider
        domain = email.split('@')[-1]
        smtp_server, smtp_port = EMAIL_PROVIDERS.get(domain, ('smtp.gmail.com', 465))
        
        if smtp_server == '':
            print(f'Sorry, invalid email domain: {domain}')
            flash('Sorry, invalid email', category='error')
            return (f'Using SMTP server {smtp_server}:{smtp_port} for domain {domain}')#redirect('/forgotpassword')
        

        link = 'You got this message because you requested to reset your password, if this was you please click the link below and follow the instructions to reset your password. However if this wasn\'t your action you may need to change your password as someone might be trying to manipulate your credentials. http://127.0.0.1:8080/passwordreset'
        
        # Create the email message
        message = MIMEText(link)
        message['Subject'] = 'Password Reset Link'
        message['From'] = 'awoofgistblogspot@gmail.com'
        message['To'] = email
        
        try:
            # Send the email using SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login('awoofgistblogspot@gmail.com', 'awoofperson00')
                smtp.send_message(message)
                
            flash('Password reset link has been sent to your email.', category='success')
            return redirect('/forgotpassword')
        
        except (smtplib.SMTPException, ConnectionRefusedError) as e:
            flash(f'Could not send email: {str(e)}', category='error')
            return redirect('/forgotpassword')
    
    return render_template('forgotpassword.html')







# @app.route('/forgotpassword')
# def forgotpassword():
#     if request.method == 'GET':
#         email_providers = {}
#         link = 'http://127.0.0.1:8080/passwordreset'
#         with open('staffmail.txt','r+') as message:
#             message.write(link)
#         return 'a password reset link has been sent to your mail'

@app.route('/passwordreset/', methods = ["POST", "GET"])
def staffforgot():
    if request.method == 'GET':
        return render_template('passwordreset.html')
    else:
        mail = request.form.get('email')
        newpwd = request.form.get('pwd')
        newpwd2 = request.form.get('confirm-pwd')

        if mail != "" and newpwd != "" and newpwd2 != "":
            registeredstaff = Employees.query.filter(Employees.employee_email == mail).first()
            if registeredstaff != None:
                if newpwd == newpwd2:
                    pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)([a-zA-Z\d]{8,})$"
                    p = re.match(pattern,newpwd)
                    if p:
                        pwdhash = generate_password_hash(newpwd)
                        registeredstaff.employee_password = pwdhash
                        db.session.commit()
                        flash('password changed successfully, you can log in with your new password!', category='success')
                        return redirect(url_for('staffforgot'))
                    else:
                        flash('please check password requirements')
                        return redirect(url_for('staffforgot'))
                else:
                    flash('password must match')
                    return redirect(url_for('staffforgot'))

            else:
                flash('Username doesn\'t exist', category='error')
                return redirect(url_for('staffforgot'))
        else:
            flash('all field required')
            return redirect(url_for('staffforgot'))



@app.route('/staffdashboard/') 
def staffdashboard():
    if session.get('staff') is not None:
        staff = Employees.query.get(session['staff'])
        total = Managementreport.query.filter(Managementreport.employee == session['staff']).all()
        reports = db.session.query(Managementreport).filter(Managementreport.report_status == 1).all()
        return render_template('staffdashboard.html', reports = reports, staff = staff, total = total)
    else:
        return redirect('/stafflogin')

@app.route('/report/', methods=['POST', 'GET'])
def report():
    if 'staff' in session and 'office' in session:
        staff = session['staff']
        office = session['office']
        if request.method == 'GET':
            getid = Employees.query.get(staff)
            department = getid.dept_id
            mgt = Office.query.filter(Office.office_id != 3).all()
            depts = Department.query.filter_by(dept_id = department).all()

            if session['office'] == 1 or session['office'] == 2: 
                workers = Employees.query.filter(Employees.office_id == 3).filter(Employees.dept_id == department).all()
            elif session['office'] == 3:
                workers = Employees.query.filter(Employees.office_id != 3).filter(Employees.dept_id == department).all()

            reports = Staffreport.query.filter(Staffreport.reported_by == staff).all()
            return render_template('report.html', workers = workers, mgt = mgt, depts = depts, getid = getid, reports = reports)
        else:            
            text = request.form.get('report')
            about = request.form.get('workers')
            offices = request.form.get('offices')
            depts = request.form.get('depts')
            if text != "" and about != "" and depts != "": 
                if session['office'] == 1 or session['office'] == 2:
                    insert = Managementreport(report_msg = text, employee = about, department = depts, reported_by = office)
                    db.session.add(insert)
                    db.session.commit()
                    flash("Your report has been submitted, approved reports will be available in the dashboard", category='success')
                    return redirect('/report')
                elif session['office'] == 3:
                    add = Staffreport(report_msg = text, office= offices, department = depts, employee = about, reported_by = staff)
                    db.session.add(add)
                    db.session.commit()
                    flash('Thanks for submitting the report, it will looked into and the status will appear at the notification center as soon as possible!', category='success')
                    return redirect('/report')
                else:
                    flash("something went wrong, please refresh this page and try again", category='error')
                    return redirect('/report')
            else:
                flash("Your message is empty, unable to process an empty message", category='error')
                return redirect('/report')
                 
    else:
        return redirect('/stafflogin')




@app.route('/stafflogout')
def stafflogout():
    if session.get('staff') != None:
        session.pop('staff', None)
        return redirect('/stafflogin')