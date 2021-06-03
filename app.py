import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_dropzone import Dropzone
import AttendanceProject

app = Flask(__name__, static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
UPLOAD_FOLDER = '/Users/tylerle/Zoom-Attendance/static/uploads'
# UPLOAD_FOLDER = '/Users/tylerle/Zoom-Attendance/BaseImagesOfStudents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

dropzone = Dropzone(app)
src_images = AttendanceProject.getImgSrc()


@app.route('/uploads', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    return render_template('takeAttendance.html')


@app.route("/", methods=['GET', 'POST'])
def main():
    return render_template('index.html', src_images=src_images)


@app.route('/results')
def results():
    return render_template('results.html')


@app.route("/takeAttendance.html", methods=['GET', 'POST'])
def takeAttendance():
    AttendanceProject.processAttendance()
    filenames = []
    for filename in os.listdir('static/uploads'):
        if filename.endswith(".jpg") and filename != "class.jpg" and filename != "result.jpg":
            filenames.append(os.path.join('static/uploads', filename))

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
