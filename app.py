from flask import Flask,request,render_template,redirect,url_for,flash,session,send_file
from flask_session import Session
import flask_excel as excel
from otp import genotp
from smail import send_mail
from stoken import endata,dndata
from io import BytesIO
import mimetypes
from openpyxl import Workbook
import re
import mysql.connector
mydb=mysql.connector.connect(user='root',password='Ghana@1230',host='localhost',database='snmprj')
app=Flask(__name__)
excel.init_excel(app)
app.secret_key='codd@456'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=="POST":
        username=request.form['username']
        usermail=request.form['email']
        userpassword=request.form['password']
        print(request.form)
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select count(*) from users where email=%s',[usermail])
            count_email=cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(e)
            flash('could not take user details')
            return redirect(url_for('register'))
        else:
            if count_email[0]==0:
                serverotp=genotp()
                userdata={'username': username,
                'usermail': usermail,
                'userpassword': userpassword,
                'userotp': serverotp}
                subject="OTP Verification For SNM APP"
                body=f'use the given OTP:{serverotp} for registering SNM APP'
                send_mail(to= usermail,body=body,subject=subject)
                return redirect(url_for('otpverify',votp=endata(data=userdata)))
            elif count_email[0]==1:
                flash('email already existed please give new email')
    return render_template('register.html')

@app.route('/otpverify/<votp>',methods=['GET','POST'])
def otpverify(votp):
    if request.method=='POST':
        user_otp=request.form['otp1']+request.form['otp2']+request.form['otp3']+request.form['otp4']+request.form['otp5']+request.form['otp6']
        try:
            decode_server_otp=dndata(data=votp)
        except Exception as e:
            print(e)
            flash('Verify OTP failed')
            return redirect(url_for('otpverify' ,votp=votp))
        else:
            if user_otp==decode_server_otp['userotp']:
                 cursor=mydb.cursor()
                 cursor.execute('insert into users(username,email,password) values(%s,%s,%s)',[decode_server_otp['username'],decode_server_otp['usermail'],decode_server_otp['userpassword']])
                 mydb.commit()
                 cursor.close()
                 flash('user details has been stored please login')
                 return redirect(url_for('login'))
            else:
                flash('OTP is wrong')
    return render_template('otpverify.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        login_useremail = request.form['email']
        login_password = request.form['password']
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select count(*) from users where email=%s',[login_useremail])
            email_count = cursor.fetchone()
        except Exception as e:
            print(e)
            flash('Could connect to server')
            return redirect(url_for('login'))
        else:
            if email_count[0] == 1:
                cursor.execute('select password from users where email=%s',[login_useremail])
                stored_password = cursor.fetchone()
                if stored_password[0] == login_password:
                    session['user']=login_useremail  #creating session id
                    return redirect(url_for('dashboard'))
                else:
                    flash('Incorrect Password')
                    return redirect(url_for('login'))
            elif email_count[0]==0:
                flash('No email found please check')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/addnotes',methods=['GET','POST'])
def addnotes():
    if session.get('user'):
        if request.method=='POST':
            notes_title = request.form['title']
            notes_description = request.form['description']
            try:
                cursor = mydb.cursor(buffered=True)
                cursor.execute('insert into notesdata(title,description,added_by) values(%s,%s,%s)',[notes_title,notes_description,session.get('user')])
                mydb.commit()
                cursor.close()
            except Exception as e:
                print(e)
                flash('Could not add notes details')
                return redirect(url_for('addnotes'))
            else:
                flash('Notes added successfully','success')
        return render_template('addnotes.html')
    else:
        flash('Please Login first')
        return render_template('login.html')
    
@app.route('/viewallnotes')
def viewallnotes():
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select nid,title,created_at from notesdata where added_by = %s',[session.get('user')])
            notes_data = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not fetch notes details')
            return redirect(url_for('viewallnotes'))
        else:
            return render_template('viewallnotes.html',notes_data=notes_data)
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select nid,title,description,created_at from notesdata where added_by = %s and nid = %s',[session.get('user'),nid])
            notes_data = cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not fetch notes details')
            return redirect(url_for('viewnotes'))
        else:
            return render_template('viewnotes.html',notes_data=notes_data)
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/deletenotes/<nid>')
def deletenotes(nid):
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('delete from notesdata where added_by = %s and nid = %s',[session.get('user'),nid])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not delete notes details')
            return redirect(url_for('viewallnotes'))
        else:
            flash('Note deleted successfully')
            return redirect(url_for('viewallnotes'))
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/update_notes/<nid>',methods=['GET','PUT'])
def update_notes(nid):
    if session.get('user'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select nid,title,description,created_at from notesdata where added_by=%s and nid=%s',[session.get('user'),nid])
            notes_data=cursor.fetchone()  #[(1,'python','2025-11-07')] 
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not update notes details')
            return redirect(url_for('viewallnotes'))
        else:
            if request.method == 'PUT':
                print(request.get_json())
                update_title = request.get_json()['title']
                update_description = request.get_json()['description']
                try:
                    cursor = mydb.cursor(buffered=True)
                    cursor.execute('update notesdata set title=%s, description=%s where added_by=%s and nid=%s',
               [update_title, update_description, session.get('user'), nid])
                    mydb.commit()
                    cursor.close()
                except Exception as e:
                    print(e)
                    flash('Could not update notes data')
                    return redirect(url_for('viewallnotes'))
                else:
                    return 'ok'
        return render_template('updatenotes.html',notes_data=notes_data)
    else:
        flash('Please Login first')
        return redirect(url_for('login')) 

@app.route('/getexceldata')
def getexceldata():
    if session.get('user'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select nid,title,description,created_at from notesdata where added_by=%s',[session.get('user')])
            notes_data=cursor.fetchall()  #[(1,'python','2025-11-07'),(2,'python','2025-11-07')]]
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not fetch notes details')
            return redirect(url_for('viewallnotes'))
        else:
            columns=['Notes_id','Title','Description','Created_at']
            array_data=[list(i) for i in notes_data]
            array_data.insert(0,columns)
            # generate XLSX in-memory using openpyxl to avoid OS/tempfile issues
            try:
                wb = Workbook()
                ws = wb.active
                for row in array_data:
                    ws.append(row)
                output = BytesIO()
                wb.save(output)
                output.seek(0)
                return send_file(output, as_attachment=True, download_name="my_data.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                print(e)
                flash('Could not generate excel file')
                return redirect(url_for('viewallnotes'))
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/uploadfile', methods=['GET', 'POST'])
def uploadfile():
    if not session.get('user'):
        flash('Please login first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_file = request.files.get('file')

        if not user_file or user_file.filename == '':
            return render_template('uploadfile.html')

        filename = user_file.filename
        file_data = user_file.read()

        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute(
                'SELECT COUNT(*) FROM filesdata WHERE filename=%s AND added_by=%s',
                (filename, session.get('user'))
            )
            exists = cursor.fetchone()[0]
            cursor.close()
        except Exception as e:
            print(e)
            flash('Database error', 'error')
            return render_template('uploadfile.html')

        if exists:
            return render_template(
                'uploadfile.html',
                file_exists=True,
                filename=filename
            )

        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute(
                'INSERT INTO filesdata (filename, filedata, added_by) VALUES (%s,%s,%s)',
                (filename, file_data, session.get('user'))
            )
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Upload failed', 'error')
            return render_template('uploadfile.html')

        flash(f'File "{filename}" uploaded successfully', 'success')
        return render_template(
            'uploadfile.html',
            uploaded_filename=filename
        )

    return render_template('uploadfile.html')
@app.route('/viewallfiles')
def viewallfiles():
    if session.get('user'):
        try:
            cursor=mydb.cursor(buffered=True)
            cursor.execute('select fid,filename,created_at from filesdata where added_by=%s',[session.get('user')])
            files_data=cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not fetch files details')
            return redirect(url_for('dashboard'))
        else:
            return render_template('viewallfiles.html',files_data=files_data)
    else:
        flash('Please login first')
        return redirect(url_for('login'))
    
@app.route('/viewfiledata/<fid>')
def viewfiledata(fid):
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select fid,filename,filedata,created_at from filesdata where added_by=%s and fid=%s',[session.get('user'),fid])
            file_data = cursor.fetchone()
            mime_type, encoding = mimetypes.guess_type(file_data[1])
            print(f'MIME Type: {mime_type}')
            print(f'Encoding: {encoding}')

            fdata = BytesIO(file_data[2])
            filename = file_data[1]
            cursor.close()
        except Exception as e:
            print(e)
            flash("Could not fetch file details")
            return redirect(url_for('viewallfiles'))
        else:
            if not mime_type:
                mime_type = 'application/octet-stream'
            return send_file(fdata, mimetype=mime_type, as_attachment=False, download_name=filename)
    else:
        flash('Please login first')
        return redirect(url_for('login')) 
    
@app.route('/downloadfiledata/<fid>')
def downloadfiledata(fid):
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select fid,filename,filedata,created_at from filesdata where added_by=%s and fid=%s',[session.get('user'),fid])
            file_data = cursor.fetchone()
            mime_type, encoding = mimetypes.guess_type(file_data[1])
            print(f'MIME Type: {mime_type}')
            print(f'Encoding: {encoding}')

            fdata = BytesIO(file_data[2])
            filename = file_data[1]
            cursor.close()
        except Exception as e:
            print(e)
            flash("Could not delete file details")
            return redirect(url_for('viewallfiles'))
        else:
            if not mime_type:
                mime_type = 'application/octet-stream'
            return send_file(fdata, mimetype=mime_type, as_attachment=True, download_name=filename)
    else:
        flash('Please login first')
        return redirect(url_for('login')) 
    
@app.route('/deletefile/<fid>')
def deletefile(fid):
    if session.get('user'):
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('delete from filesdata where added_by = %s and fid = %s',[session.get('user'),fid])
            mydb.commit()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not delete notes details')
            return redirect(url_for('viewallfiles'))
        else:
            flash('Note deleted successfully')
            return redirect(url_for('viewallfiles'))
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/search',methods=['POST'])
def search():
    if session.get('user'):
        search_data = request.form['q']
        strg = ['A-Za-z0-9']
        pattern = re.compile(f'^{strg}',re.IGNORECASE)
        if pattern.match(search_data):
            try:
                cursor = mydb.cursor(buffered=True)
                cursor.execute('select nid,title,created_at from notesdata where added_by=%s and title like %s',[session.get('user'),search_data+'%'])
                snotes_data = cursor.fetchall()
                cursor.close()
            except Exception as e:
                print(e)
                flash('Could not fetch notes details')
                return redirect(url_for('viewallnotes'))
            else:
                return render_template('viewallnotes.html',notes_data=snotes_data)
        else:
            flash('Invalid search data')
            return redirect(url_for('dashboard'))
    else:
        flash('Please Login first')
        return redirect(url_for('login'))
    
@app.route('/userlogout')
def userlogout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('login'))
    else:
        flash('Please Login')
        return redirect(url_for('login'))

@app.route('/forgotpassword',methods=['GET','POST'])
def forgotpassword():
    if request.method=='POST':
        email_id = request.form['email']
        try:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('select count(*) from users where email=%s',[email_id])
            count_email = cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(e)
            flash('Could not take user details')
            return redirect(url_for('login'))
        else:
            if count_email[0] == 1:
                subject='Reset link for forgot password'
                body = f"Click the link for {url_for('newpassword',data=endata(email_id),_external=True)}"
                send_mail(to=email_id,subject=subject,body=body)
                flash('Resetlink has been sent to given mail')
                return redirect(url_for('forgotpassword'))
            elif count_email[0] == 0:
                flash('Check your email_id')

    return render_template('forgotpassword.html')

@app.route('/newpassword/<data>',methods=['GET','PUT'])
def newpassword(data):
    try:
        email_data=dndata(data)
    except Exception as e:
        print(e)
        flash('Could not fetch user data')
        return redirect(url_for('newpassword',data=data))
    else:
        if request.method == 'PUT':
            new_password = request.get_json()['password']
            try:
                cursor = mydb.cursor(buffered=True)
                cursor.execute('update users set password=%s where email=%s',[new_password,email_data])
                mydb.commit()
                cursor.close()
            except Exception as e:
                print(e)
                flash('Could not update password')
                return redirect(url_for('newpassword'))
            else:
                return 'ok'
    return render_template('newpassword.html',data=data)
    

            
    
app.run(debug=True,use_reloader=True)