"""The flask application"""
#!/usr/bin/env python3
import sqlite3
from flask import Flask, Response,render_template,url_for,request,session,redirect  # pylint: disable=import-error
import prometheus_client  # pylint: disable=import-error

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
app = Flask(__name__)
app.secret_key = "sessions"

def get_db_connection():
    conn = sqlite3.connect('db/hotel.db')
    #conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register/',methods = ['POST', 'GET'])
def register():
  if request.method == 'POST':
    conn = get_db_connection()
    error = {}
    msg = {}
    for x in request.form:
      if request.form[x] == "":
        error[x] = 'this field not empty'

    if(len(error)  > 0):
      msg['error'] = 'form is cant be empty'
      return render_template('register.html',msg = msg)

    is_exist_user = conn.execute('SELECT username,usermail FROM users WHERE username = ? or usermail = ?', (request.form['username'],request.form['usermail']))
    
    if is_exist_user.fetchone() is not None:
      msg['error'] = 'try another username and email cause there is exists'
      return render_template('register.html',msg = msg)
    
    conn.execute("INSERT INTO users (name,username,usermail,password,country,city) VALUES (?,?,?,?,?,?)", 
    (request.form['name'] + ' '+ request.form['lastname'], request.form['username'],request.form['usermail'],request.form['password'],request.form['country'],request.form['city']))
    conn.commit()
    conn.close()
    msg['success'] = 'register ok'
    return render_template('register.html',msg = msg) 
  else:
    return render_template('register.html')


@app.route('/login/',methods = ['POST', 'GET'])
def login():
  if request.method == 'POST':
    session.permanent = True
    msg = {}
    conn = get_db_connection()
    is_exist_user = conn.execute('SELECT username,password FROM users WHERE username = ? and password = ?', (request.form['username'],request.form['password']))
    if is_exist_user.fetchone() is None:
      msg['error'] = 'username or password wrong'
      return render_template('login.html',msg = msg) 
    else:
      session["login"] = 1
      session["user"] = request.form['username']
      #return render_template('login.html',msg = 'login is success fully will be redirect login page')
      return redirect(url_for("index"))
  else:
    return render_template('login.html')
 


@app.route('/otel/detail/<id>',methods = ['GET'])
def oteldetail(id):
  return render_template('detail.html',id=id)



@app.route("/logout")
def logout():
    session.pop("login", None)
    session.pop("user", None)
    return redirect(url_for("index"))

  
@app.errorhandler(500)
def handle_500(error):
    """The error handler"""
    return str(error), 500




if __name__ == '__main__':
    app.run()
