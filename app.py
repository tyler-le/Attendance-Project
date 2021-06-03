import os
import time

from flask import Flask, render_template, request
from flask_dropzone import Dropzone
# import AttendanceProject
from AttendanceProject import processAttendance

app = Flask(__name__, static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD']=True
UPLOAD_FOLDER = '/Users/tylerle/Zoom-Attendance/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

dropzone = Dropzone(app)

@app.route('/uploads-students', methods=['GET', 'POST'])
def uploads_students():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(f'{UPLOAD_FOLDER}/students', f.filename))
    return render_template('takeAttendance.html')


@app.route('/uploads-class', methods=['GET', 'POST'])
def uploads_class():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(f'{UPLOAD_FOLDER}/class', f.filename))
    return render_template('takeAttendance.html')


@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template('index.html')


@app.route('/results')
def results():
    return render_template('results.html')


@app.route("/takeAttendance.html", methods=['GET', 'POST'])
def takeAttendance():
    filenames = []
    for filename in os.listdir('static/uploads/students'):
        if filename.endswith(".jpg"):
            filenames.append(os.path.join('static/uploads/students', filename))
    processAttendance()
    return render_template('takeAttendance.html', filenames=filenames)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
