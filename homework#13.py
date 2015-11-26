__author__ = 'T Jeremiah November 2015'
from flask import Flask, render_template, request, redirect, session, g, url_for, abort, flash
import os.path,time,re,sqlite3
# conn = sqlite3.connect('hw13.db')

# configuration featued from other examples/textbooks
DATABASE = 'hw13.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid Username'
            return render_template('login.html', error=error)
        elif request.form['password'] != 'password':
            error = 'Invalid Password'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            return redirect('/dashboard')
    else:
        return render_template('login.html', error=error)


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if session['logged_in'] != True:
        flash("You are not logged in")
        return redirect('/login')
    else:
        cur = g.db.execute('select ID, FIRSTNAME, LASTNAME from STUDENTS order by LASTNAME ASC')
        students = [dict(student_id=row[0], first_name=row[1], last_name=row[2]) for row in cur.fetchall()]
        cur = g.db.execute('select ID, SUBJECT, QUESTION_COUNT, QUIZ_DATE from QUIZZES order by ID asc')
        quizzes = [dict(quiz_id=row[0], subject=row[1], question_count=row[2], date=row[3]) for row in cur.fetchall()]
        return render_template("dashboard.html", students=students, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
def studentadd():
    if session['logged_in'] != True:
        flash("You are not logged in")
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('studentadd.html')
        elif request.method == 'POST':
            if request.form['first_name'] == "":
                flash("No First Name, Try Again")
                return redirect('/student/add')
            elif request.form['last_name'] == "":
                flash("No Last Name, Try Again")
                return redirect('/student/add')
            else:
                try:
                    g.db.execute('insert into STUDENTS (FIRSTNAME, LASTNAME) values (?,?)',
                                 (request.form['first_name'], request.form['last_name']))
                    g.db.commit()
                    return redirect('/dashboard')
                except:
                    flash("Error updating record")
                    return redirect('/student/add')


@app.route('/quiz/add', methods=['GET', 'POST'])
def quizadd():
    if session['logged_in'] != True:
        flash("You are not logged in")
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('quizadd.html')
        elif request.method == 'POST':
            if request.form['subject'] == "":
                flash("No Quiz Subject, Try Again")
                return redirect('/quiz/add')
            else:
                try:
                    g.db.execute('insert into QUIZZES (SUBJECT, QUESTION_COUNT, QUIZ_DATE) values (?,?,?)',
                                 (request.form['subject'], request.form['question_count'], request.form['date']))
                    g.db.commit()
                    return redirect('/dashboard')
                except:
                    flash("Error Updating Record")
                    return redirect('/quiz/add')


@app.route('/student/<id>', methods=['GET'])
def studentquiz(id):
    if session['logged_in'] != True:
        flash("You are not logged in")
        return redirect('/login')
    else:
        cur = g.db.execute('select FIRSTNAME, LASTNAME from STUDENTS where ID = ?', (id))
        namelist = cur.fetchall()[0]
        studentname = namelist[0] + " " + namelist[1]
        cur = g.db.execute('select QUIZID, SCORE from RESULTS where STUDENTID = ?', id)
        results = [dict(quiz_id=row[0], score=row[1]) for row in cur.fetchall()]
        return render_template('results.html', results=results, studentname=studentname)


@app.route('/results/add', methods=['GET', 'POST'])
def addresults():
    if session['logged_in'] != True:
        flash("You are not logged in")
        return redirect('/login')
    else:
        if request.method == 'GET':
            cur = g.db.execute('select ID, SUBJECT from QUIZZES')
            quizzes = [dict(quiz_id=row[0], subject=row[1]) for row in cur.fetchall()]
            cur = g.db.execute('select ID, FIRSTNAME, LASTNAME from STUDENTS')
            students = [dict(student_id=row[0], studentname=row[1] + " " + row[2]) for row in cur.fetchall()]
            return render_template('addresults.html', quizzes=quizzes, students=students)
        elif request.method == 'POST':
            try:
                g.db.execute('insert into RESULTS (STUDENTID, QUIZID, SCORE) values (?, ?, ?)',
                             (request.form['student_id'], request.form['quiz_id'], request.form['score']))
                g.db.commit()
                flash("Quiz Records Updated")
                return redirect("/dashboard")

            except:
                flash("Error Updating Record")
                return redirect("/results/add")


if __name__ == '__main__':
    app.run()
